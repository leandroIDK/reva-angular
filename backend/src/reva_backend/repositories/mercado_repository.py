"""Consultas de lectura reutilizables para el dominio del marketplace."""

from hashlib import sha256


class MercadoRepository:
    """Encapsula consultas de lectura para que las rutas no repitan SQL común."""

    def __init__(self, conexion):
        self.conexion = conexion

    def usuario_con_sesion_activa(self, token: str):
        return self.conexion.execute(
            """
            SELECT u.id_usuario, u.correo, u.nombres, u.rol
            FROM usuarios u
            JOIN sesiones s USING(id_usuario)
            WHERE s.token_hash=%s AND s.vence_en>now() AND u.activo
            """,
            (sha256(token.encode()).hexdigest(),),
        ).fetchone()

    def catalogo(self, propietario=None, moderacion: bool = False):
        filtro = "true" if moderacion else "p.estado='aprobado' AND u.activo"
        parametros = ()
        if propietario:
            filtro = 't.id_usuario=%s'
            parametros = (propietario,)

        productos = self.conexion.execute(
            """
            SELECT p.*, t.nombre AS tienda, t.distrito
            FROM productos p
            JOIN tiendas t USING(id_tienda)
            JOIN usuarios u ON u.id_usuario=t.id_usuario
            WHERE """ + filtro + " ORDER BY p.creado_en DESC LIMIT 200",
            parametros,
        ).fetchall()
        for producto in productos:
            producto['variantes'] = self.conexion.execute(
                'SELECT * FROM variantes_producto WHERE id_producto=%s ORDER BY talla,color',
                (producto['id_producto'],),
            ).fetchall()
            producto['imagenes'] = self.conexion.execute(
                'SELECT url FROM imagenes_producto WHERE id_producto=%s',
                (producto['id_producto'],),
            ).fetchall()
        return productos
