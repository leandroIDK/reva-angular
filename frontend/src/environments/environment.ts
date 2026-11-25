/**
 * Configuración base. En Render la URL real se inyecta en index.html mediante
 * REVA_API_URL; en desarrollo se deja vacía para usar el proxy /api.
 */
export const environment = {
  production: false,
  apiUrl: '',
};
