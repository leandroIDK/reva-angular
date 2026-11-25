from fastapi import APIRouter

from reva_backend.schemas.catalog import ProductPreview

router = APIRouter(prefix="/api/catalog", tags=["Catálogo"])


@router.get("/products", response_model=list[ProductPreview], summary="Listar productos")
def list_products() -> list[ProductPreview]:
    """Contrato inicial. La persistencia se conectará después de aprobar el modelo."""
    return []
