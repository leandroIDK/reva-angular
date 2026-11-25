from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator

class Acceso(BaseModel):
    correo: EmailStr
    clave: str = Field(min_length=10, max_length=72)

    @field_validator('clave')
    @classmethod
    def longitud_bytes(cls, value):
        if len(value.encode()) > 72:
            raise ValueError('Máximo 72 bytes para bcrypt')
        return value

class Registro(Acceso):
    nombres: str = Field(min_length=2, max_length=120)

class Tienda(BaseModel):
    nombre: str = Field(min_length=2,max_length=100)
    distrito: Literal['Huancayo','El Tambo','Chilca']
    direccion: str = Field(min_length=5,max_length=250)
    dni: str = Field(pattern=r'^\d{8}$')
    consentimiento: bool

class Variante(BaseModel):
    talla: str = Field(default='',max_length=30)
    color: str = Field(default='',max_length=40)
    precio: Decimal = Field(gt=0,le=1000000,max_digits=12,decimal_places=2)
    stock: int = Field(ge=1,le=100000)

class Producto(BaseModel):
    titulo: str = Field(min_length=3,max_length=150)
    descripcion: str = Field(min_length=10,max_length=3000)
    material: str = Field(default='',max_length=100)
    condicion: Literal['Nuevo','Como nuevo','Usado'] = 'Nuevo'
    id_categoria: int = Field(gt=0)
    imagen: HttpUrl | None = None
    variantes: list[Variante] = Field(min_length=1,max_length=50)
    modalidad: Literal['venta','subasta'] = 'venta'
    precio_inicial: Decimal = Field(default=20,gt=0,max_digits=12,decimal_places=2)
    incremento: Decimal = Field(default=1,gt=0,max_digits=12,decimal_places=2)
    cierre: datetime | None = None

class ItemCarrito(BaseModel):
    id_variante: UUID
    cantidad: int = Field(ge=0,le=1000)

class Pedido(BaseModel):
    direccion: str = Field(min_length=5,max_length=250)
    clave_operacion: UUID

class Puja(BaseModel):
    monto: Decimal = Field(gt=0,le=1000000,max_digits=12,decimal_places=2)

class Moderacion(BaseModel):
    estado: Literal['aprobado','rechazado']
    motivo: str = Field(min_length=3,max_length=500)

class EstadoCuenta(BaseModel):
    activo: bool
    motivo: str = Field(min_length=3,max_length=500)

class Reporte(BaseModel):
    id_producto: UUID
    motivo: str = Field(min_length=5,max_length=500)

class Campana(BaseModel):
    marca: str = Field(min_length=2,max_length=100)
    video_url: HttpUrl
    destino_url: HttpUrl
    activa: bool = False
    vence_en: datetime
