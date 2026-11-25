from fastapi import APIRouter

router = APIRouter(prefix="/api/admin", tags=["Administración"])


@router.get("/modules", summary="Módulos previstos del panel administrador")
def admin_modules() -> dict[str, list[str]]:
    """Contrato informativo inicial; aún no ejecuta acciones ni consulta datos."""
    return {"modules": ["publicaciones", "usuarios", "reportes", "planes", "publicidad"]}
