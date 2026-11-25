from fastapi import HTTPException, Request


def conexion(request: Request):
    pool = request.app.state.pool
    if pool is None:
        raise HTTPException(503, 'Configura DATABASE_URL y ejecuta las migraciones de REVA.')
    with pool.connection() as conn:
        yield conn
