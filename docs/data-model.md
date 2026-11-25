# Modelo de datos implementado

La migración `backend/migrations/001_inicial.sql` define el esquema privado `reva`. Fue comprobada en PostgreSQL embebido; su ejecución en Supabase está pendiente de credenciales.

## Entidades principales

- `usuarios`: UUID, correo único, nombres, hash bcrypt, DNI único y rol.
- `sesiones`: hash de token, usuario y vencimiento.
- `tiendas`: una tienda por usuario, distrito y dirección.
- `categorias`: catálogo único de categorías.
- `productos`: descripción, condición, modalidad y estado de moderación.
- `variantes_producto`: talla, color, precio y stock; combinación única por producto.
- `imagenes_producto`: URLs de imágenes de cada producto.
- `carrito`: cantidades por usuario y variante.
- `pedidos`: comprador, operación idempotente, dirección, importe y comisión histórica.
- `detalle_pedidos`: cantidad y precio unitario histórico por variante.
- `planes`: precio y límites comerciales.
- `suscripciones`: plan vigente y vencimiento por usuario.
- `subastas`: precio inicial, incremento y cierre por producto.
- `pujas`: usuario, monto y fecha por subasta.
- `campanas_publicitarias`: marca, video, destino y vigencia.
- `reportes`: motivo y estado del reporte de producto.
- `acciones_moderacion`: auditoría de decisiones administrativas.

## Decisión sobre administración

El administrador es un registro de `usuarios` con `rol = 'administrador'`. Las contraseñas se protegen en FastAPI; Supabase Auth no participa en esta versión.

## Relaciones y normalización

- Un vendedor puede tener una tienda y varias publicaciones.
- Un producto puede tener varias variantes y cada variante controla su stock.
- Un pedido tiene una cabecera y uno o varios detalles.
- Una subasta pertenece a un vendedor y recibe varias pujas.
- Solo una publicación activa puede entrar al catálogo.
- Los precios históricos del pedido no cambian cuando cambia el catálogo; la comisión del 5 % se calcula mediante una función SQL.
- Las listas de variantes, imágenes y líneas de pedido son tablas separadas, sin columnas repetidas. Los datos de tienda y plan se referencian mediante claves foráneas.
- No se duplican nombres del vendedor o categoría en el producto. Las instantáneas monetarias del pedido se conservan como hechos históricos de la operación.
- Los cupos de publicaciones y las pujas se comprueban con bloqueo de filas; la compra comprueba y descuenta stock dentro de una transacción.
