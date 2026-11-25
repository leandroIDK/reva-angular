# Arquitectura inicial de REVA

## Frontend

Angular standalone conectado a FastAPI mediante el servicio `services/api.ts`. La pantalla de mercado agrupa los formularios iniciales y se selecciona mediante rutas. Inicio y anuncios son componentes separados. El proxy de desarrollo enruta `/api` hacia el puerto 8000.

## Backend

FastAPI con separación por responsabilidades:

- `apis/`: endpoints y dependencias HTTP.
- `schemas/`: contratos de entrada y salida.
- `apis/mercado.py`: reglas transaccionales y consultas parametrizadas de la primera versión; extraer servicios y repositorios por dominio conforme crezcan los flujos.
- `database.py`: dependencia de conexión psycopg por petición.
- `manage.py`: migraciones y alta segura del administrador.
- `config.py`: configuración por variables de entorno.
- `main.py`: creación de la aplicación.

## Roles previstos

- `comprador`: explora ofertas y registra pedidos.
- `vendedor`: registra tienda y envía publicaciones a moderación.
- `administrador`: modera publicaciones, suspende cuentas y gestiona campañas y reportes.

El administrador es un usuario con rol `administrador`. Supabase aloja el esquema privado `reva`; la autenticación la gestiona FastAPI con bcrypt. No se utiliza Supabase Auth. Las sesiones expiran y se revocan al suspender la cuenta. Ver `estado-implementacion.md` para las verificaciones y limitaciones.
