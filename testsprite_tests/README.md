# Tests de TestSprite

Esta carpeta contiene los planes, casos y reportes generados por TestSprite para REVA.

Los MCP de Playwright, Supabase y GitHub están definidos en el `.mcp.json` de la raíz. No son dependencias de ejecución de la aplicación.

## Preparación

1. Define `TESTSPRITE_API_KEY` en el entorno local; nunca lo escribas en `.mcp.json`.
2. Levanta el backend y el frontend en sus puertos de desarrollo.
3. Desde el agente con MCP activo, solicita: `Ayúdame a probar este proyecto con TestSprite`.

Los casos deben cubrir como mínimo registro/inicio de sesión, catálogo, publicación pendiente de aprobación, carrito, pedido, subasta y acciones del administrador.

## MCP disponibles

- **TestSprite:** pruebas funcionales y generación de reportes.
- **Playwright:** navegación, interacción y revisión visual del frontend.
- **Supabase:** consulta de documentación y diagnóstico de la base de datos REVA en modo solo lectura.
- **GitHub:** repositorios, issues, Pull Requests y Actions cuando el proyecto tenga repositorio remoto.

Playwright requiere Node.js 20 o superior. Supabase y GitHub solicitan autenticación OAuth al conectarse; no se guardan tokens en este repositorio.
