from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from psycopg_pool import ConnectionPool
from psycopg_pool import PoolTimeout
from psycopg.rows import dict_row
from psycopg import IntegrityError, OperationalError
from fastapi.responses import JSONResponse
from reva_backend.apis.mercado import router
from reva_backend.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    @asynccontextmanager
    async def lifespan(app):
        app.state.pool = None
        if settings.database_url:
            app.state.pool = ConnectionPool(settings.database_url, min_size=0, max_size=5, timeout=8, kwargs={'row_factory':dict_row,'options':'-c search_path=reva,public','connect_timeout':8})
        yield
        if app.state.pool:
            app.state.pool.close()

    app = FastAPI(title="REVA API", version="0.2.0", lifespan=lifespan)
    app.state.pool = None
    @app.exception_handler(IntegrityError)
    async def integridad(request,exc):
        return JSONResponse(status_code=409,content={'detail':'Los datos están duplicados o no cumplen las relaciones del sistema.'})
    @app.exception_handler(OperationalError)
    async def desconexion(request,exc):
        return JSONResponse(status_code=503,content={'detail':'Base de datos temporalmente no disponible.'})
    @app.exception_handler(PoolTimeout)
    async def tiempo_agotado(request,exc):
        return JSONResponse(status_code=503,content={'detail':'No se pudo conectar con PostgreSQL. Revisa DATABASE_URL.'})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    @app.get("/health", tags=["Sistema"])
    def health() -> dict[str, str]:
        return {"status": "ok", "project": "reva"}

    return app


app = create_app()
