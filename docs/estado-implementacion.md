# Estado de implementación — 23 de noviembre de 2026

## Entregado

Frontend Angular con rutas Inicio, Ofertas, Cuenta, Vender, Planes, Carrito, Subastas, REVA Crece y Administración. Formularios conectados por HTTP a FastAPI, mensajes de carga/error y diseño adaptable. Publicidad de video con controles y sin reproducción automática, administrable mediante formulario.

Backend: registro con bcrypt, sesiones revocables, autorización por rol, tiendas, consultas externas DNI/RUC/Maps, productos con variantes, moderación, suspensión de cuentas, carrito, pedido transaccional e idempotente, comisión del 5 %, planes de demostración, límites 0/2/5/7, pujas con bloqueo de fila y validación del cierre, reportes y métricas iniciales. Esquema privado PostgreSQL en español con migración y comando administrativo.

## Validación realizada

- 13 pruebas pytest aprobadas: CORS, disponibilidad sin configuración, restricciones de contraseña, permisos, montos mínimos, autopujas, cierre y stock negativo.
- Compilador Angular (`ngc --noEmit`): TypeScript y plantillas sin errores.
- PostgreSQL embebido (PGlite): migración ejecutada en memoria; claves foráneas, unicidad, comisión, consulta SQL de checkout con bloqueos, decremento de stock, pujas y límites de planes verificados. No equivale a validar concurrencia ni la conexión al Session Pooler real.
- `ng build`: bloqueado en este entorno por `spawn EPERM` al ejecutar esbuild. No hay build final validado ni revisión visual de navegador.

## Configuración pendiente

No hay `.env` con DATABASE_URL real ni claves APISPERU_TOKEN / NOMINATIM_USER_AGENT en esta carpeta. No se modificó el proyecto remoto de Supabase. Copiar `.env.example`, completar secretos localmente, ejecutar migración y crear el administrador con el comando documentado en README.

No se ejecutó TestSprite: el archivo de configuración no demuestra una sesión MCP activa y no hay API key configurada aquí.

## Límites funcionales actuales

- Compras, comisiones y planes son demostraciones sin cobros reales.
- Las subastas cierran para nuevas pujas, pero falta adjudicación, pago y entrega al ganador.
- Entrega por coordinar: sin integración logística ni seguimiento.
- Imágenes mediante URL HTTPS; pendiente carga a Storage.
- DNI autocompleta datos, no acredita identidad. RUC y geocodificación se consultan en el formulario; queda pendiente guardar los resultados comerciales y coordenadas.
- No hay campañas de marcas precargadas; el administrador carga videos autorizados.
- Pendientes: recuperación de contraseña, correo verificado, protección distribuida contra abuso, edición completa de catálogo/categorías/planes y seguimiento de pedidos de vendedores.

## Reproducir comprobación SQL

Desde la raíz: `npm ci --prefix testsprite_tests/sql-check` y `node testsprite_tests/sql-check/verificar.mjs`.
Los datos de esta prueba solo existen en memoria, nunca en Supabase.
