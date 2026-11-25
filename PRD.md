# PRD — REVA

## 1. Resumen

REVA es un marketplace local para Huancayo, El Tambo y Chilca que ayuda a pequeños comerciantes a mover mercadería acumulada, recuperar capital inmovilizado y encontrar nuevos compradores. La propuesta incorpora **REVA Crece**, un espacio de orientación para que los negocios conozcan pasos de formalización y mejoren su gestión.

El producto debe generar impacto social positivo: más visibilidad para emprendimientos locales, rotación de inventario y acceso sencillo a oportunidades de compra y venta.

## 2. Problema y oportunidad

- Los comerciantes acumulan inventario y pierden capital por falta de visibilidad.
- Muchos negocios dependen de redes sociales y mensajes manuales para vender.
- Los compradores no tienen un catálogo local confiable, filtrable y ordenado.
- Los emprendimientos necesitan orientación práctica para crecer y formalizarse.

## 3. Usuarios y roles

1. **Comprador:** explora productos, filtra, agrega al carrito y registra pedidos.
2. **Vendedor:** verifica su identidad, administra tienda, productos, variantes, stock, subastas y pedidos.
3. **Administrador:** modera publicaciones, subastas, reportes, usuarios, planes y anuncios.

El administrador es un rol dentro de `usuarios`; no se crea una tabla de administradores separada.

## 4. Alcance funcional

### Catálogo y tiendas

- Inicio con categorías y ofertas destacadas.
- Búsqueda y filtros por categoría, distrito, precio y disponibilidad.
- Ficha específica del producto: descripción, precio, fotos, talla, color, material, condición, stock y ubicación.
- Perfil público de tienda y productos del vendedor.

### Registro y verificación

- Registro mediante FastAPI, bcrypt para contraseñas y sesiones revocables de ocho horas. Supabase aloja PostgreSQL; esta implementación no usa Supabase Auth.
- Alta de vendedor con consulta de DNI/RUC mediante APIs Perú, siempre con consentimiento y desde el backend.
- No guardar tokens de terceros ni contraseñas en el frontend.

### Compra

- Carrito persistente por usuario.
- Creación de pedido y detalle de productos.
- Comisión configurable de REVA registrada en el pedido.
- En esta fase académica no se integra una pasarela de pago real; el flujo queda preparado para una integración posterior.

### Subastas

- Publicación de subastas con precio inicial, incremento mínimo, fecha de cierre y reglas.
- Pujas registradas con usuario, monto y fecha; el backend valida que cada puja supere la anterior.
- Solo vendedores con un plan habilitado pueden crear subastas.
- Toda subasta pasa por aprobación del administrador antes de mostrarse.

### Planes y anuncios

- Planes con límites de publicaciones/subastas y beneficios configurables.
- Suscripción activa y fecha de vencimiento.
- Anuncios no intrusivos dentro de espacios definidos del catálogo, sujetos a aprobación.

### Administración

- Bandeja de publicaciones y subastas pendientes.
- Aprobar, rechazar y solicitar cambios con motivo.
- Suspender/reactivar cuentas y revisar reportes.
- Gestionar categorías, planes, anuncios y métricas básicas.

### REVA Crece

- Contenido educativo y enlaces de orientación para formalización y mejora del negocio.
- No sustituye asesoría legal, tributaria o contable profesional.

## 5. Arquitectura y tecnologías

- **Frontend:** Angular, componentes reutilizables, diseño responsive y validaciones.
- **Backend:** FastAPI con Python, esquemas Pydantic, rutas versionadas y CORS restringido por variables de entorno.
- **Base de datos:** Supabase PostgreSQL, conexión Session Pooler con `psycopg`/`psycopg_pool`.
- **Convención:** nombres de tablas y columnas en español y `snake_case`; modelo normalizado hasta 3FN.
- **Pruebas:** TestSprite para pruebas funcionales end-to-end sobre la aplicación levantada; pruebas unitarias del backend y frontend en sus respectivas carpetas.
- **Despliegue:** se definirá después de estabilizar el entorno local y las migraciones.

## 6. Modelo de datos previsto

Entidades principales: `perfiles`, `tiendas`, `categorias`, `productos`, `variantes_producto`, `imagenes_producto`, `pedidos`, `detalle_pedidos`, `subastas`, `pujas`, `planes`, `suscripciones`, `reportes`, `acciones_moderacion` y `campanas_publicitarias`.

La tabla de identidad implementada se llama `usuarios` en lugar de `perfiles`. Su clave primaria es `id_usuario`, un UUID propio generado por PostgreSQL. El DNI es único, pero no la clave primaria. El esquema privado `reva` se consulta desde el backend con psycopg.

## 7. Fuera de alcance inicial

- Pasarela de pagos y retención financiera real.
- Integración de WhatsApp como canal de compra.
- Facturación electrónica.
- Geocodificación avanzada; se evaluará después de estabilizar el catálogo.
- Automatizaciones publicitarias con marcas reales.

## 8. Requisitos no funcionales

- Validar entradas y aplicar autorización por rol en backend.
- Mantener secretos únicamente en variables de entorno.
- Documentar API con OpenAPI.
- Responder con mensajes claros y estados HTTP correctos.
- Diseñar para móvil y escritorio.
- Registrar auditoría de acciones administrativas.

## 9. Criterios de aceptación del MVP

- Un usuario puede registrarse e iniciar sesión.
- Un vendedor puede completar verificación, crear tienda y enviar una publicación a moderación.
- Un administrador puede aprobar o rechazar una publicación y suspender una cuenta.
- Un comprador puede explorar, agregar al carrito y crear un pedido de prueba.
- Una subasta aprobada acepta pujas válidas y rechaza montos menores o iguales a la puja vigente.
- Los flujos principales tienen pruebas reproducibles y no exponen secretos.

## 10. Métricas de impacto

- Comerciantes verificados y activos.
- Publicaciones aprobadas y productos con stock rotado.
- Pedidos completados y valor recuperado de inventario.
- Participación en contenidos de REVA Crece.
- Tiempo promedio desde registro hasta primera publicación aprobada.
