CREATE SCHEMA IF NOT EXISTS reva;
SET search_path TO reva;
CREATE TABLE usuarios (
 id_usuario uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 correo text NOT NULL UNIQUE CHECK(correo=lower(correo)),
 nombres text NOT NULL,
 clave_hash text NOT NULL,
 dni varchar(8) UNIQUE CHECK(dni ~ '^[0-9]{8}$'),
 rol text NOT NULL DEFAULT 'comprador' CHECK(rol IN ('comprador','vendedor','administrador')),
 activo boolean NOT NULL DEFAULT true,
 creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE sesiones (
 token_hash text PRIMARY KEY, id_usuario uuid NOT NULL REFERENCES usuarios,
 vence_en timestamptz NOT NULL
);
CREATE TABLE tiendas (
 id_tienda uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 id_usuario uuid UNIQUE NOT NULL REFERENCES usuarios,
 nombre text NOT NULL, distrito text NOT NULL CHECK(distrito IN ('Huancayo','El Tambo','Chilca')),
 direccion text NOT NULL, ruc varchar(11) UNIQUE, latitud numeric, longitud numeric
);
CREATE TABLE categorias (id_categoria integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY, nombre text UNIQUE NOT NULL);
INSERT INTO categorias(nombre) VALUES ('Moda'),('Tecnología'),('Hogar'),('Calzado'),('Otros');
CREATE TABLE planes (
 id_plan text PRIMARY KEY, nombre text NOT NULL, precio numeric(12,2) NOT NULL CHECK(precio>=0),
 limite_publicaciones integer NOT NULL, limite_subastas integer NOT NULL
);
INSERT INTO planes VALUES ('gratis','REVA Básico',0,5,0),('emprende','REVA Emprende',19,20,2),('pro','REVA Pro',39,50,5),('negocio','REVA Negocio',79,500,7);
CREATE TABLE suscripciones (
 id_usuario uuid PRIMARY KEY REFERENCES usuarios, id_plan text NOT NULL REFERENCES planes,
 vence_en timestamptz NOT NULL, demostracion boolean NOT NULL DEFAULT true
);
CREATE TABLE productos (
 id_producto uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_tienda uuid NOT NULL REFERENCES tiendas,
 id_categoria integer NOT NULL REFERENCES categorias, titulo text NOT NULL, descripcion text NOT NULL,
 material text NOT NULL DEFAULT '', condicion text NOT NULL,
 modalidad text NOT NULL DEFAULT 'venta' CHECK(modalidad IN ('venta','subasta')),
 estado text NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','aprobado','rechazado')),
 motivo text NOT NULL DEFAULT '', creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE variantes_producto (
 id_variante uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_producto uuid NOT NULL REFERENCES productos,
 talla text NOT NULL DEFAULT '', color text NOT NULL DEFAULT '',
 precio numeric(12,2) NOT NULL CHECK(precio>0), stock integer NOT NULL CHECK(stock>=0),
 UNIQUE(id_producto,talla,color)
);
CREATE TABLE imagenes_producto (
 id_imagen uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_producto uuid NOT NULL REFERENCES productos, url text NOT NULL
);
CREATE TABLE carrito (
 id_usuario uuid REFERENCES usuarios, id_variante uuid REFERENCES variantes_producto,
 cantidad integer NOT NULL CHECK(cantidad>0), PRIMARY KEY(id_usuario,id_variante)
);
CREATE TABLE pedidos (
 id_pedido uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_usuario uuid NOT NULL REFERENCES usuarios,
 clave_operacion uuid NOT NULL UNIQUE, direccion text NOT NULL, estado text NOT NULL DEFAULT 'confirmado_demo',
 total numeric(12,2) NOT NULL, comision numeric(12,2) NOT NULL, creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE detalle_pedidos (
 id_pedido uuid REFERENCES pedidos, id_variante uuid REFERENCES variantes_producto,
 cantidad integer NOT NULL CHECK(cantidad>0), precio_unitario numeric(12,2) NOT NULL,
 PRIMARY KEY(id_pedido,id_variante)
);
CREATE TABLE subastas (
 id_subasta uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_producto uuid UNIQUE NOT NULL REFERENCES productos,
 precio_inicial numeric(12,2) NOT NULL CHECK(precio_inicial>0), incremento numeric(12,2) NOT NULL CHECK(incremento>0),
 cierre timestamptz NOT NULL
);
CREATE TABLE pujas (
 id_puja uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_subasta uuid NOT NULL REFERENCES subastas,
 id_usuario uuid NOT NULL REFERENCES usuarios, monto numeric(12,2) NOT NULL CHECK(monto>0), creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX pujas_subasta_monto ON pujas(id_subasta,monto DESC);
CREATE TABLE acciones_moderacion (
 id_accion uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_administrador uuid NOT NULL REFERENCES usuarios,
 entidad text NOT NULL, id_entidad uuid NOT NULL, accion text NOT NULL, motivo text NOT NULL,
 creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE reportes (
 id_reporte uuid PRIMARY KEY DEFAULT gen_random_uuid(), id_usuario uuid NOT NULL REFERENCES usuarios,
 id_producto uuid NOT NULL REFERENCES productos, motivo text NOT NULL,
 estado text NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','resuelto'))
);
CREATE TABLE campanas_publicitarias (
 id_campana uuid PRIMARY KEY DEFAULT gen_random_uuid(), marca text NOT NULL, video_url text NOT NULL,
 destino_url text NOT NULL, activa boolean NOT NULL DEFAULT false, vence_en timestamptz NOT NULL
);
CREATE FUNCTION calcular_comision(importe numeric) RETURNS numeric LANGUAGE sql IMMUTABLE AS $$ SELECT round(importe * 0.05,2) $$;
-- Esquema privado: el navegador accede exclusivamente a FastAPI.
REVOKE ALL ON SCHEMA reva FROM PUBLIC;
