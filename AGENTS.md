# Guía del proyecto REVA

- Lee `PRD.md` antes de modificar decisiones funcionales.
- Mantén `backend`, `frontend` y `testsprite_tests` separados.
- Usa español y `snake_case` para tablas, columnas, migraciones y nombres de dominio de la base de datos.
- No guardes tokens, contraseñas ni claves de APIs en el repositorio. Usa `.env` local y conserva solo `.env.example`.
- Las consultas de DNI/RUC se realizan desde el backend, nunca exponiendo el token al navegador.
- Supabase/PostgreSQL aún debe evolucionar mediante migraciones revisadas; no cambies el esquema directamente sin documentarlo.
- El administrador es un rol de `usuarios`, no una tabla independiente. Usar bcrypt en FastAPI; esta versión no usa Supabase Auth.
- Los resultados y artefactos de TestSprite deben guardarse en `testsprite_tests/`.
- Los MCP se configuran en `.mcp.json`; son herramientas del agente, no servicios que deba importar el backend.
- Supabase MCP queda limitado a este proyecto y en modo `read_only=true` hasta que se apruebe explícitamente una migración.
- Revisa y aprueba manualmente las operaciones de MCP que puedan modificar datos o repositorios.
- Antes de entregar cambios, ejecuta las pruebas disponibles y verifica que frontend y backend compilen.
