# REVA Angular

Implementación académica con Angular, FastAPI y PostgreSQL en Supabase. Incluye código de registro, sesiones, tiendas, productos, variantes, carrito, pedidos de demostración, planes, subastas y moderación.

## Arranque local

Desde `backend/`:

```powershell
uv sync --cache-dir .uv-cache
Copy-Item .env.example .env
# Completa DATABASE_URL y las claves privadas en .env.
uv run --cache-dir .uv-cache python -m reva_backend.manage migrar
uv run --cache-dir .uv-cache python -m reva_backend.manage crear_admin
uv run --cache-dir .uv-cache uvicorn reva_backend.main:app --reload --port 8000
```

El comando crear_admin pide correo y contraseña de forma interactiva. No existe una contraseña administrativa pública.

En otra terminal, desde `frontend/`:

```powershell
npm install
npm start
```

Frontend: http://localhost:4200. Documentación API: http://localhost:8000/docs.
Angular usa un proxy `/api` al backend. En producción configurar ese mismo enrutamiento con HTTPS.

## Despliegue en Render

El repositorio incluye `render.yaml`, `backend/Dockerfile` y una configuración para publicar el frontend como sitio estático. El backend aplica migraciones idempotentes al iniciar y escucha el puerto entregado por Render.

1. En Render crea un **Web Service** desde este repositorio con `Root Directory: backend`, runtime **Docker** y health check `/health`. También puedes usar el Blueprint `render.yaml`.
2. Configura en el backend `DATABASE_URL`, `APISPERU_TOKEN`, `NOMINATIM_USER_AGENT`, `MODO_DEMOSTRACION=true` y, inicialmente, `CORS_ORIGINS` con la URL pública final del frontend.
3. Cuando Render entregue la URL del backend (`https://...onrender.com`), crea un **Static Site** con `Root Directory: frontend`, build command `npm ci && npm run build:render` y directorio publicado `dist/reva-frontend/browser`.
4. En el sitio estático define `REVA_API_URL` con la URL HTTPS del backend. No lleva `/api` al final.
5. Configura o conserva la regla SPA `/* → /index.html`, incluida en `render.yaml`, y vuelve a desplegar el backend después de definir su `CORS_ORIGINS`.

Nunca subas `.env`, la URL de PostgreSQL, tokens de APIs Perú ni contraseñas al repositorio.

## Base de datos y seguridad

Migración versionada en `backend/migrations/001_inicial.sql`. Esquema privado `reva`, nombres españoles en snake_case, claves foráneas y función SQL `calcular_comision` (5 %).
Se conecta con psycopg al Session Pooler. La migración es explícita; no se ejecuta al arrancar la API.
Se utiliza autenticación propia en FastAPI con bcrypt y UUID propio de usuario, en lugar de Supabase Auth. Las sesiones caducan a las ocho horas y se revocan al suspender la cuenta. El DNI es único y no es la clave primaria.

## Integraciones

APIs Perú DNI/RUC y Nominatim/OpenStreetMap se consultan únicamente desde backend. Configurar `APISPERU_TOKEN` y `NOMINATIM_USER_AGENT` en `.env`. Nominatim se usa solo mediante búsquedas explícitas, con caché y límite de una consulta por segundo. Una consulta de DNI no demuestra posesión del documento.
Los MCP están declarados en `.mcp.json`; eso no los autentica ni los activa automáticamente. El formato depende del cliente: VS Code Copilot usa `.vscode/mcp.json`. TestSprite requiere su API key y aplicación accesible.

## Validación

Desde backend: `uv run --cache-dir .uv-cache pytest`. Desde frontend: `npm run build`.
Las pruebas unitarias no sustituyen las pruebas de integración con credenciales reales de Supabase y proveedores.

## Alcance de la demostración

Los pedidos y planes no realizan cobros. La comisión se registra contablemente. Los planes permiten 0/2/5/7 subastas simultáneas y 5/20/50/500 publicaciones (500 es el límite inicial de uso razonable).
Las pujas comprueban el monto mínimo y el cierre, sin verificar saldo bancario. La adjudicación y pago del ganador están pendientes. La entrega se coordina; no hay tarifa automática de envío.

## Pendientes de producción

Pasarela real, validación de identidad, recuperación/verificación de correo, rate limiting distribuido, subida de imágenes a Storage, adjudicación de subastas, seguimiento de entrega y métricas sociales. No publicar como plataforma de cobros reales.

## Propósito

REVA conecta a pequeños comerciantes de Huancayo, El Tambo y Chilca con compradores locales para ayudarles a mover mercadería acumulada, recuperar capital y fortalecer sus negocios mediante REVA Crece.

## Estructura

- `frontend/`: aplicación Angular.
- `backend/`: API FastAPI organizada por rutas, esquemas, servicios y repositorios.
- `docs/`: decisiones iniciales de arquitectura y modelo de datos.

## Configuración pendiente

Completar credenciales locales, aplicar la migración y ejecutar los recorridos completos con cuentas de prueba antes de desplegar.
