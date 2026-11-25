"""Comandos explícitos para migración, administración y datos de prueba."""
import argparse
import getpass
from pathlib import Path
import bcrypt
import psycopg
from reva_backend.config import get_settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=['migrar', 'crear_admin', 'sembrar_pruebas'])
    args = parser.parse_args()
    url = get_settings().database_url
    if not url:
        raise SystemExit('Configura DATABASE_URL en backend/.env')
    with psycopg.connect(url) as conn:
        if args.accion == 'migrar':
            conn.execute('CREATE TABLE IF NOT EXISTS public.reva_migraciones(nombre text PRIMARY KEY)')
            conn.execute('SELECT pg_advisory_xact_lock(738201)')
            for file in sorted(Path('migrations').glob('*.sql')):
                if not conn.execute('SELECT 1 FROM public.reva_migraciones WHERE nombre=%s',(file.name,)).fetchone():
                    conn.execute(file.read_text(encoding='utf-8'))
                    conn.execute('INSERT INTO public.reva_migraciones VALUES (%s)',(file.name,))
                    print('Aplicada:', file.name)
        elif args.accion == 'crear_admin':
            correo = input('Correo del administrador: ').strip().lower()
            clave = getpass.getpass('Contraseña (10 caracteres mínimo): ')
            if '@' not in correo or not 10 <= len(clave) or len(clave.encode()) > 72:
                raise SystemExit('Correo o contraseña inválidos.')
            if clave != getpass.getpass('Repite la contraseña: '):
                raise SystemExit('Las contraseñas no coinciden.')
            conn.execute("INSERT INTO reva.usuarios(correo,nombres,clave_hash,rol) VALUES (%s,'Administrador',%s,'administrador')", (correo,bcrypt.hashpw(clave.encode(),bcrypt.gensalt()).decode()))
            print('Administrador creado.')
        else:
            correo = input('Correo del administrador de pruebas: ').strip().lower()
            clave = getpass.getpass('Contraseña (10 caracteres mínimo): ')
            if '@' not in correo or not 10 <= len(clave) or len(clave.encode()) > 72:
                raise SystemExit('Correo o contraseña inválidos.')
            if clave != getpass.getpass('Repite la contraseña: '):
                raise SystemExit('Las contraseñas no coinciden.')

            usuario = conn.execute('SELECT id_usuario FROM reva.usuarios WHERE correo=%s', (correo,)).fetchone()
            clave_hash = bcrypt.hashpw(clave.encode(), bcrypt.gensalt()).decode()
            if usuario:
                usuario = conn.execute("UPDATE reva.usuarios SET nombres='Administrador de Pruebas', clave_hash=%s, rol='administrador', activo=true WHERE id_usuario=%s RETURNING id_usuario", (clave_hash, usuario[0])).fetchone()
            else:
                usuario = conn.execute("INSERT INTO reva.usuarios(correo,nombres,clave_hash,rol) VALUES (%s,'Administrador de Pruebas',%s,'administrador') RETURNING id_usuario", (correo, clave_hash)).fetchone()

            id_usuario = usuario[0]
            tienda = conn.execute("""
                INSERT INTO reva.tiendas(id_usuario,nombre,distrito,direccion)
                VALUES (%s,'Tienda de Pruebas REVA','Huancayo','Av. Giráldez 100, Huancayo')
                ON CONFLICT(id_usuario) DO UPDATE SET nombre=excluded.nombre,distrito=excluded.distrito,direccion=excluded.direccion
                RETURNING id_tienda
            """, (id_usuario,)).fetchone()
            id_tienda = tienda[0]
            conn.execute("""
                INSERT INTO reva.suscripciones(id_usuario,id_plan,vence_en,demostracion)
                VALUES (%s,'negocio',now()+interval '30 days',true)
                ON CONFLICT(id_usuario) DO UPDATE SET id_plan=excluded.id_plan,vence_en=excluded.vence_en,demostracion=true
            """, (id_usuario,))

            productos = [
                ('Producto pendiente de prueba', 'Producto enviado para validar la moderación.', 'Hogar', 'Nuevo', 'venta', 'pendiente', 33.33, 3),
                ('Producto aprobado de prueba', 'Producto disponible para carrito, pedido y comisión.', 'Algodón', 'Nuevo', 'venta', 'aprobado', 33.33, 3),
                ('Subasta aprobada de prueba', 'Producto disponible para probar pujas.', 'Cuero', 'Como nuevo', 'subasta', 'aprobado', 20, 1),
            ]
            for titulo, descripcion, material, condicion, modalidad, estado, precio, stock in productos:
                producto = conn.execute('SELECT id_producto FROM reva.productos WHERE id_tienda=%s AND titulo=%s', (id_tienda, titulo)).fetchone()
                if not producto:
                    producto = conn.execute("""
                        INSERT INTO reva.productos(id_tienda,id_categoria,titulo,descripcion,material,condicion,modalidad,estado,motivo)
                        VALUES (%s,1,%s,%s,%s,%s,%s,%s,'Datos iniciales de prueba')
                        RETURNING id_producto
                    """, (id_tienda, titulo, descripcion, material, condicion, modalidad, estado)).fetchone()
                    conn.execute('INSERT INTO reva.variantes_producto(id_producto,talla,color,precio,stock) VALUES (%s,%s,%s,%s,%s)', (producto[0], 'M', 'Morado', precio, stock))
                    if modalidad == 'subasta':
                        conn.execute("INSERT INTO reva.subastas(id_producto,precio_inicial,incremento,cierre) VALUES (%s,20,5,now()+interval '7 days')", (producto[0],))
            print('Datos de prueba preparados.')

if __name__ == '__main__':
    main()
