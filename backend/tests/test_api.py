from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from reva_backend.main import create_app
from reva_backend.config import get_settings
from reva_backend.apis.mercado import admin, pujar
from reva_backend.schemas.mercado import Acceso, Producto, Puja, Registro

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('DATABASE_URL','')
    monkeypatch.setenv('CORS_ORIGINS','http://localhost:4200')
    get_settings.cache_clear()
    with TestClient(create_app()) as c:
        yield c
    get_settings.cache_clear()

def test_health(client):
    assert client.get('/health').status_code==200

def test_sin_configuracion_no_finge_datos(client):
    assert client.get('/api/productos').status_code==503

def test_cors(client):
    headers={'Origin':'http://localhost:4200','Access-Control-Request-Method':'POST'}
    assert client.options('/api/registro',headers=headers).status_code==200
    headers['Origin']='https://otro.example'
    assert client.options('/api/registro',headers=headers).status_code==400

@pytest.mark.parametrize('clave',['corta','ñ'*40])
def test_bcrypt_limites(clave):
    with pytest.raises(ValidationError):
        Acceso(correo='persona@example.com',clave=clave)

def test_registro_no_permite_elegir_admin():
    r=Registro(correo='persona@example.com',clave='contrasena-larga',nombres='Persona',rol='administrador')
    assert not hasattr(r,'rol')

def test_admin_rechaza_comprador():
    with pytest.raises(HTTPException) as e:
        admin({'rol':'comprador'})
    assert e.value.status_code==403

class Resultado:
    def __init__(self,fila): self.fila=fila
    def fetchone(self): return self.fila

class BasePuja:
    def __init__(self,subasta,ultima): self.subasta=subasta; self.ultima=ultima; self.insertada=False
    def execute(self,sql,parametros):
        if 'FOR UPDATE' in sql: return Resultado(self.subasta)
        if 'max(monto)' in sql: return Resultado({'monto':self.ultima})
        self.insertada=True
        return Resultado({'monto':parametros[2]})

@pytest.mark.parametrize('monto,ultima,permitida',[(20,None,True),(19,None,False),(25,Decimal(24),True),(24,Decimal(24),False)])
def test_puja_respeta_minimos(monto,ultima,permitida):
    db=BasePuja({'id_usuario':uuid4(),'precio_inicial':Decimal(20),'incremento':Decimal(1),'cierre':datetime.now(timezone.utc)+timedelta(hours=1)},ultima)
    if permitida:
        assert pujar(uuid4(),Puja(monto=monto),{'id_usuario':uuid4()},db)['monto']==monto
    else:
        with pytest.raises(HTTPException): pujar(uuid4(),Puja(monto=monto),{'id_usuario':uuid4()},db)
    assert db.insertada==permitida

def test_no_autopujas_ni_pujas_vencidas():
    propietario=uuid4()
    for cierre,comprador in [(datetime.now(timezone.utc)-timedelta(hours=1),uuid4()),(datetime.now(timezone.utc)+timedelta(hours=1),propietario)]:
        db=BasePuja({'id_usuario':propietario,'cierre':cierre},None)
        with pytest.raises(HTTPException): pujar(uuid4(),Puja(monto=20),{'id_usuario':comprador},db)
        assert not db.insertada

def test_stock_negativo_rechazado():
    with pytest.raises(ValidationError):
        Producto(titulo='Zapatos',descripcion='Producto de prueba',id_categoria=1,variantes=[{'precio':20,'stock':-1}])
