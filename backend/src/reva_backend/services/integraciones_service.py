"""Servicios de conexión segura con proveedores externos."""

import threading
import time

import httpx
from fastapi import HTTPException

from reva_backend.config import get_settings


_cache_geocodificacion: dict[str, list[dict]] = {}
_bloqueo_geocodificacion = threading.Lock()
_ultima_consulta_geocodificacion = 0.0


def consultar_documento(tipo: str, numero: str) -> dict:
    """Consulta DNI/RUC en APIs Perú usando el token privado del backend."""
    token = get_settings().apisperu_token
    if not token:
        raise HTTPException(503, 'Configura APISPERU_TOKEN para consultar documentos.')
    try:
        respuesta = httpx.get(
            f'https://dniruc.apisperu.com/api/v1/{tipo}/{numero}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=12,
        )
        if respuesta.status_code == 404:
            raise HTTPException(404, 'Documento no encontrado')
        respuesta.raise_for_status()
        datos = respuesta.json()
        if datos.get('success') is False:
            raise HTTPException(404, 'Documento no encontrado')
        return datos
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, 'El proveedor de documentos no respondió. Intenta nuevamente.')


def geocodificar(direccion: str) -> list[dict]:
    """Busca una dirección peruana respetando caché y límite de Nominatim."""
    agente = get_settings().nominatim_user_agent.strip()
    if not agente:
        raise HTTPException(503, 'Configura NOMINATIM_USER_AGENT con un correo de contacto.')

    consulta = ' '.join(direccion.split())
    global _ultima_consulta_geocodificacion
    with _bloqueo_geocodificacion:
        if consulta in _cache_geocodificacion:
            return _cache_geocodificacion[consulta]
        espera = 1 - (time.monotonic() - _ultima_consulta_geocodificacion)
        if espera > 0:
            raise HTTPException(429, 'Espera un segundo antes de buscar otra dirección.')

    try:
        respuesta = httpx.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': consulta, 'countrycodes': 'pe', 'format': 'jsonv2', 'limit': 5},
            headers={'User-Agent': agente, 'Accept-Language': 'es'},
            timeout=12,
        )
        respuesta.raise_for_status()
        resultado = [
            {'direccion': dato['display_name'], 'lat': dato['lat'], 'lng': dato['lon']}
            for dato in respuesta.json()
        ]
        if not resultado:
            raise HTTPException(422, 'No se encontró la dirección.')
        with _bloqueo_geocodificacion:
            _ultima_consulta_geocodificacion = time.monotonic()
            _cache_geocodificacion[consulta] = resultado
        return resultado
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, 'No se pudo consultar el servicio de ubicaciones.')
