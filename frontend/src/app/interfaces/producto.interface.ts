/** Variante comercial de un producto (talla, color, precio y stock). */
export interface Variante {
  id_variante: string;
  precio: number;
  stock: number;
  talla: string;
  color: string;
}

export interface ImagenProducto {
  url: string;
}

/** Datos que el frontend muestra para un producto del catálogo. */
export interface Producto {
  id_producto: string;
  titulo: string;
  descripcion: string;
  condicion: string;
  material: string;
  distrito: string;
  tienda: string;
  modalidad: string;
  estado: string;
  motivo: string;
  variantes: Variante[];
  imagenes: ImagenProducto[];
}
