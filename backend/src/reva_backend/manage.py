"""Comandos explícitos: migrar y crear_admin. Nunca ejecuta DDL al arrancar la API."""
import argparse
import getpass
from pathlib import Path
import bcrypt
import psycopg
from reva_backend.config import get_settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=['migrar', 'crear_admin'])
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
        else:
            correo = input('Correo del administrador: ').strip().lower()
            clave = getpass.getpass('Contraseña (10 caracteres mínimo): ')
            if '@' not in correo or not 10 <= len(clave) or len(clave.encode()) > 72:
                raise SystemExit('Correo o contraseña inválidos.')
            if clave != getpass.getpass('Repite la contraseña: '):
                raise SystemExit('Las contraseñas no coinciden.')
            conn.execute("INSERT INTO reva.usuarios(correo,nombres,clave_hash,rol) VALUES (%s,'Administrador',%s,'administrador')", (correo,bcrypt.hashpw(clave.encode(),bcrypt.gensalt()).decode()))
            print('Administrador creado.')

if __name__ == '__main__':
    main()
