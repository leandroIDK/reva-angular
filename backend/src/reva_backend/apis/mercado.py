import hashlib
import secrets
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Header
from reva_backend.config import get_settings
from reva_backend.database import conexion
from reva_backend.repositories.mercado_repository import MercadoRepository
from reva_backend.schemas.mercado import Acceso, Registro, Tienda, Producto, ItemCarrito, Pedido, Puja, Moderacion, EstadoCuenta, Reporte
from reva_backend.schemas.mercado import Campana
from reva_backend.services.integraciones_service import consultar_documento, geocodificar as buscar_direccion

router = APIRouter(prefix='/api')

def exigir(condicion, mensaje, codigo=400):
    if not condicion:
        raise HTTPException(codigo,mensaje)

def repositorio(db=Depends(conexion)):
    return MercadoRepository(db)

def usuario(authorization: str = Header(default=''), repo=Depends(repositorio)):
    token = authorization.removeprefix('Bearer ')
    fila = repo.usuario_con_sesion_activa(token)
    exigir(fila is not None,'Inicia sesión para continuar.',401)
    return fila

def admin(u=Depends(usuario)):
    exigir(u['rol']=='administrador','Solo administradores.',403)
    return u

def publico(u):
    return {k:u[k] for k in ('id_usuario','correo','nombres','rol')}

@router.post('/registro',status_code=201)
def registro(datos: Registro,db=Depends(conexion)):
    correo = str(datos.correo).lower()
    fila = db.execute('INSERT INTO usuarios(correo,nombres,clave_hash) VALUES (%s,%s,%s) RETURNING id_usuario,correo,nombres,rol', (correo,datos.nombres,bcrypt.hashpw(datos.clave.encode(),bcrypt.gensalt()).decode())).fetchone()
    return fila

@router.post('/sesion')
def sesion(datos: Acceso,db=Depends(conexion)):
    fila = db.execute('SELECT * FROM usuarios WHERE correo=%s AND activo',(str(datos.correo).lower(),)).fetchone()
    # Comparación costosa también para correos inexistentes.
    referencia = fila['clave_hash'].encode() if fila else bcrypt.hashpw(b'inexistente',bcrypt.gensalt())
    valido = bcrypt.checkpw(datos.clave.encode(),referencia)
    exigir(fila is not None and valido,'Credenciales incorrectas.',401)
    token = secrets.token_urlsafe(48)
    db.execute("INSERT INTO sesiones VALUES (%s,%s,now()+interval '8 hours')",(hashlib.sha256(token.encode()).hexdigest(),fila['id_usuario']))
    return {'token':token,'usuario':publico(fila)}

@router.delete('/sesion')
def salir(authorization: str = Header(default=''),db=Depends(conexion)):
    db.execute('DELETE FROM sesiones WHERE token_hash=%s',(hashlib.sha256(authorization.removeprefix('Bearer ').encode()).hexdigest(),))
    return {'mensaje':'Sesión cerrada'}

@router.get('/yo')
def yo(u=Depends(usuario)):
    return u

@router.get('/categorias')
def categorias(db=Depends(conexion)):
    return db.execute('SELECT * FROM categorias ORDER BY nombre').fetchall()

@router.get('/planes')
def planes(db=Depends(conexion)):
    return db.execute('SELECT * FROM planes ORDER BY precio').fetchall()

@router.post('/planes/{id_plan}/activar')
def activar(id_plan: str,u=Depends(usuario),db=Depends(conexion)):
    exigir(get_settings().modo_demostracion,'Los cobros reales aún no están integrados.',409)
    exigir(db.execute('SELECT 1 FROM planes WHERE id_plan=%s',(id_plan,)).fetchone(),'Plan inexistente',404)
    db.execute("INSERT INTO suscripciones VALUES (%s,%s,now()+interval '30 days',true) ON CONFLICT(id_usuario) DO UPDATE SET id_plan=excluded.id_plan,vence_en=excluded.vence_en",(u['id_usuario'],id_plan))
    return {'mensaje':'Plan de demostración activado por 30 días. No se realizó ningún cobro.'}

@router.get('/documentos/{tipo}/{numero}')
def consultar_documento(tipo: str,numero: str,consentimiento: bool=False,u=Depends(usuario)):
    exigir(consentimiento,'Se requiere consentimiento.')
    exigir(tipo in ('dni','ruc') and numero.isdecimal() and len(numero)==(8 if tipo=='dni' else 11),'Documento inválido')
    datos=consultar_documento(tipo,numero)
    permitidos=('dni','nombres','apellidoPaterno','apellidoMaterno') if tipo=='dni' else ('ruc','razonSocial','estado','condicion','direccion')
    return {k:datos.get(k) for k in permitidos}

@router.post('/tienda')
def tienda(datos:Tienda,u=Depends(usuario),db=Depends(conexion)):
    exigir(datos.consentimiento,'Acepta consultar tu documento.')
    identidad = consultar_documento('dni',datos.dni)
    exigir(identidad.get('nombres'),'No se pudo validar el DNI.',422)
    db.execute("UPDATE usuarios SET dni=%s,nombres=%s,rol=CASE WHEN rol='administrador' THEN rol ELSE 'vendedor' END WHERE id_usuario=%s",(datos.dni,' '.join(str(identidad.get(k,'')) for k in ('nombres','apellidoPaterno','apellidoMaterno')),u['id_usuario']))
    return db.execute('INSERT INTO tiendas(id_usuario,nombre,distrito,direccion) VALUES (%s,%s,%s,%s) ON CONFLICT(id_usuario) DO UPDATE SET nombre=excluded.nombre,distrito=excluded.distrito,direccion=excluded.direccion RETURNING *',(u['id_usuario'],datos.nombre,datos.distrito,datos.direccion)).fetchone()

@router.get('/geocodificar')
def geocodificar(direccion: str,u=Depends(usuario)):
    exigir(5<=len(direccion)<=250,'Dirección inválida')
    return buscar_direccion(direccion)

@router.get('/productos')
def productos(repo=Depends(repositorio)):
    return repo.catalogo()

@router.get('/mis-productos')
def propios(u=Depends(usuario),repo=Depends(repositorio)):
    return repo.catalogo(u['id_usuario'])

@router.post('/productos',status_code=201)
def publicar(datos:Producto,u=Depends(usuario),db=Depends(conexion)):
    # El bloqueo por vendedor serializa publicaciones y comprobación del cupo.
    db.execute('SELECT id_usuario FROM usuarios WHERE id_usuario=%s FOR UPDATE',(u['id_usuario'],))
    tienda=db.execute('SELECT * FROM tiendas WHERE id_usuario=%s',(u['id_usuario'],)).fetchone()
    exigir(tienda,'Primero registra tu tienda.',403)
    plan=db.execute("SELECT p.* FROM planes p WHERE id_plan=coalesce((SELECT id_plan FROM suscripciones WHERE id_usuario=%s AND vence_en>now()),'gratis')",(u['id_usuario'],)).fetchone()
    cuenta=db.execute("SELECT count(*) AS n FROM productos WHERE id_tienda=%s AND estado!='rechazado'",(tienda['id_tienda'],)).fetchone()['n']
    exigir(cuenta<plan['limite_publicaciones'],'Alcanzaste el límite de publicaciones.',409)
    if datos.modalidad=='subasta':
        exigir(datos.cierre and datos.cierre.tzinfo and datos.cierre>datetime.now(timezone.utc),'Define un cierre futuro con zona horaria.')
        activas=db.execute("SELECT count(*) AS n FROM subastas s JOIN productos p USING(id_producto) WHERE p.id_tienda=%s AND p.estado!='rechazado' AND s.cierre>now()",(tienda['id_tienda'],)).fetchone()['n']
        exigir(activas<plan['limite_subastas'],'Tu plan no permite más subastas simultáneas.',403)
        exigir(len(datos.variantes)==1 and datos.variantes[0].stock==1,'La subasta corresponde a una unidad y una variante.')
    p=db.execute('INSERT INTO productos(id_tienda,id_categoria,titulo,descripcion,material,condicion,modalidad) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *',(tienda['id_tienda'],datos.id_categoria,datos.titulo,datos.descripcion,datos.material,datos.condicion,datos.modalidad)).fetchone()
    for v in datos.variantes:
        db.execute('INSERT INTO variantes_producto(id_producto,talla,color,precio,stock) VALUES (%s,%s,%s,%s,%s)',(p['id_producto'],v.talla,v.color,v.precio,v.stock))
    if datos.imagen:
        exigir(str(datos.imagen).startswith('https://'),'La imagen debe usar HTTPS.')
        db.execute('INSERT INTO imagenes_producto(id_producto,url) VALUES (%s,%s)',(p['id_producto'],str(datos.imagen)))
    if datos.modalidad=='subasta':
        db.execute('INSERT INTO subastas(id_producto,precio_inicial,incremento,cierre) VALUES (%s,%s,%s,%s)',(p['id_producto'],datos.precio_inicial,datos.incremento,datos.cierre))
    return p

@router.get('/carrito')
def carrito(u=Depends(usuario),db=Depends(conexion)):
    return db.execute('SELECT c.*,v.precio,v.talla,v.color,p.titulo FROM carrito c JOIN variantes_producto v USING(id_variante) JOIN productos p USING(id_producto) WHERE c.id_usuario=%s',(u['id_usuario'],)).fetchall()

@router.put('/carrito')
def guardar_carrito(datos:ItemCarrito,u=Depends(usuario),db=Depends(conexion)):
    if not datos.cantidad:
        db.execute('DELETE FROM carrito WHERE id_usuario=%s AND id_variante=%s',(u['id_usuario'],datos.id_variante))
    else:
        v=db.execute("SELECT v.stock,t.id_usuario FROM variantes_producto v JOIN productos p USING(id_producto) JOIN tiendas t USING(id_tienda) JOIN usuarios u ON u.id_usuario=t.id_usuario WHERE v.id_variante=%s AND p.estado='aprobado' AND p.modalidad='venta' AND u.activo",(datos.id_variante,)).fetchone()
        exigir(v and v['stock']>=datos.cantidad,'Producto sin stock suficiente.',409)
        exigir(v['id_usuario']!=u['id_usuario'],'No puedes comprar tu propio producto.')
        db.execute('INSERT INTO carrito VALUES (%s,%s,%s) ON CONFLICT(id_usuario,id_variante) DO UPDATE SET cantidad=excluded.cantidad',(u['id_usuario'],datos.id_variante,datos.cantidad))
    return {'mensaje':'Carrito actualizado'}

@router.post('/pedidos')
def comprar(datos:Pedido,u=Depends(usuario),db=Depends(conexion)):
    exigir(get_settings().modo_demostracion,'Pago real pendiente de integración.',409)
    db.execute('SELECT id_usuario FROM usuarios WHERE id_usuario=%s FOR UPDATE',(u['id_usuario'],))
    anterior=db.execute('SELECT * FROM pedidos WHERE clave_operacion=%s AND id_usuario=%s',(datos.clave_operacion,u['id_usuario'])).fetchone()
    if anterior:
        return anterior
    items=db.execute('SELECT c.*,v.precio,v.stock,p.estado,p.modalidad,u.activo,t.id_usuario AS vendedor FROM carrito c JOIN variantes_producto v USING(id_variante) JOIN productos p USING(id_producto) JOIN tiendas t USING(id_tienda) JOIN usuarios u ON u.id_usuario=t.id_usuario WHERE c.id_usuario=%s ORDER BY v.id_variante FOR UPDATE OF v,c',(u['id_usuario'],)).fetchall()
    exigir(items,'El carrito está vacío.')
    for i in items:
        exigir(i['activo'] and i['estado']=='aprobado' and i['modalidad']=='venta' and i['stock']>=i['cantidad'] and i['vendedor']!=u['id_usuario'],'Un producto ya no está disponible.',409)
    total=sum(i['precio']*i['cantidad'] for i in items)
    pedido=db.execute('INSERT INTO pedidos(id_usuario,clave_operacion,direccion,total,comision) VALUES (%s,%s,%s,%s,calcular_comision(%s)) RETURNING *',(u['id_usuario'],datos.clave_operacion,datos.direccion,total,total)).fetchone()
    for i in items:
        db.execute('UPDATE variantes_producto SET stock=stock-%s WHERE id_variante=%s',(i['cantidad'],i['id_variante']))
        db.execute('INSERT INTO detalle_pedidos VALUES (%s,%s,%s,%s)',(pedido['id_pedido'],i['id_variante'],i['cantidad'],i['precio']))
    db.execute('DELETE FROM carrito WHERE id_usuario=%s',(u['id_usuario'],))
    return pedido

@router.get('/pedidos')
def pedidos(u=Depends(usuario),db=Depends(conexion)):
    return db.execute('SELECT * FROM pedidos WHERE id_usuario=%s ORDER BY creado_en DESC',(u['id_usuario'],)).fetchall()

@router.get('/subastas')
def subastas(db=Depends(conexion)):
    return db.execute("SELECT s.*,p.titulo,t.distrito,(SELECT max(monto) FROM pujas WHERE id_subasta=s.id_subasta) AS ultima_puja FROM subastas s JOIN productos p USING(id_producto) JOIN tiendas t USING(id_tienda) JOIN usuarios u ON u.id_usuario=t.id_usuario WHERE p.estado='aprobado' AND u.activo ORDER BY s.cierre DESC LIMIT 200").fetchall()

@router.post('/subastas/{id_subasta}/pujas')
def pujar(id_subasta:UUID,datos:Puja,u=Depends(usuario),db=Depends(conexion)):
    s=db.execute("SELECT s.*,t.id_usuario FROM subastas s JOIN productos p USING(id_producto) JOIN tiendas t USING(id_tienda) JOIN usuarios u ON u.id_usuario=t.id_usuario WHERE id_subasta=%s AND p.estado='aprobado' AND u.activo FOR UPDATE OF s",(id_subasta,)).fetchone()
    exigir(s,'Subasta inexistente.',404)
    exigir(s['cierre']>datetime.now(timezone.utc),'La subasta terminó.',409)
    exigir(s['id_usuario']!=u['id_usuario'],'No puedes pujar por tu producto.',403)
    ultima=db.execute('SELECT max(monto) AS monto FROM pujas WHERE id_subasta=%s',(id_subasta,)).fetchone()['monto']
    minimo=s['precio_inicial'] if ultima is None else ultima+s['incremento']
    exigir(datos.monto>=minimo,f'La puja mínima es S/ {minimo}.',409)
    return db.execute('INSERT INTO pujas(id_subasta,id_usuario,monto) VALUES (%s,%s,%s) RETURNING *',(id_subasta,u['id_usuario'],datos.monto)).fetchone()

@router.get('/admin/productos')
def pendientes(u=Depends(admin),repo=Depends(repositorio)):
    return repo.catalogo(moderacion=True)

@router.patch('/admin/productos/{identificador}')
def moderar(identificador:UUID,datos:Moderacion,u=Depends(admin),db=Depends(conexion)):
    fila=db.execute('UPDATE productos SET estado=%s,motivo=%s WHERE id_producto=%s RETURNING *',(datos.estado,datos.motivo,identificador)).fetchone()
    exigir(fila,'Producto inexistente',404)
    db.execute("INSERT INTO acciones_moderacion(id_administrador,entidad,id_entidad,accion,motivo) VALUES (%s,'producto',%s,%s,%s)",(u['id_usuario'],identificador,datos.estado,datos.motivo))
    return fila

@router.get('/admin/usuarios')
def usuarios(u=Depends(admin),db=Depends(conexion)):
    return db.execute('SELECT id_usuario,correo,nombres,rol,activo FROM usuarios ORDER BY creado_en DESC LIMIT 200').fetchall()

@router.patch('/admin/usuarios/{identificador}')
def desactivar(identificador:UUID,datos:EstadoCuenta,u=Depends(admin),db=Depends(conexion)):
    fila=db.execute("UPDATE usuarios SET activo=%s WHERE id_usuario=%s AND rol!='administrador' RETURNING id_usuario",(datos.activo,identificador)).fetchone()
    exigir(fila,'No se puede modificar esta cuenta.',409)
    if not datos.activo:
        db.execute('DELETE FROM sesiones WHERE id_usuario=%s',(identificador,))
    db.execute("INSERT INTO acciones_moderacion(id_administrador,entidad,id_entidad,accion,motivo) VALUES (%s,'usuario',%s,%s,%s)",(u['id_usuario'],identificador,'activar' if datos.activo else 'suspender',datos.motivo))
    return {'mensaje':'Cuenta actualizada'}

@router.post('/reportes')
def reportar(datos:Reporte,u=Depends(usuario),db=Depends(conexion)):
    return db.execute('INSERT INTO reportes(id_usuario,id_producto,motivo) VALUES (%s,%s,%s) RETURNING *',(u['id_usuario'],datos.id_producto,datos.motivo)).fetchone()

@router.get('/admin/reportes')
def reportes(u=Depends(admin),db=Depends(conexion)):
    return db.execute('SELECT * FROM reportes').fetchall()

@router.patch('/admin/reportes/{identificador}')
def resolver(identificador:UUID,u=Depends(admin),db=Depends(conexion)):
    return db.execute("UPDATE reportes SET estado='resuelto' WHERE id_reporte=%s RETURNING *",(identificador,)).fetchone()

@router.get('/anuncios')
def anuncios(db=Depends(conexion)):
    return db.execute('SELECT marca,video_url,destino_url FROM campanas_publicitarias WHERE activa AND vence_en>now() LIMIT 3').fetchall()

@router.get('/admin/anuncios')
def anuncios_admin(u=Depends(admin),db=Depends(conexion)):
    return db.execute('SELECT * FROM campanas_publicitarias ORDER BY vence_en DESC').fetchall()

@router.post('/admin/anuncios',status_code=201)
def crear_anuncio(datos:Campana,u=Depends(admin),db=Depends(conexion)):
    exigir(str(datos.video_url).startswith('https://') and str(datos.destino_url).startswith('https://'),'Utiliza enlaces HTTPS.')
    exigir(datos.vence_en.tzinfo and datos.vence_en>datetime.now(timezone.utc),'Define un vencimiento futuro.')
    return db.execute('INSERT INTO campanas_publicitarias(marca,video_url,destino_url,activa,vence_en) VALUES (%s,%s,%s,%s,%s) RETURNING *',(datos.marca,str(datos.video_url),str(datos.destino_url),datos.activa,datos.vence_en)).fetchone()

@router.get('/admin/metricas')
def metricas(u=Depends(admin),db=Depends(conexion)):
    return db.execute("SELECT (SELECT count(*) FROM tiendas) AS tiendas,(SELECT count(*) FROM productos WHERE estado='pendiente') AS pendientes,(SELECT count(*) FROM pedidos) AS pedidos_demo,(SELECT coalesce(sum(total),0) FROM pedidos) AS ventas_demo,(SELECT coalesce(sum(comision),0) FROM pedidos) AS comisiones_demo").fetchone()
