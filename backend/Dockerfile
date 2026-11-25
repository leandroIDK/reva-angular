FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY migrations ./migrations
RUN uv sync --frozen --no-dev

EXPOSE 10000

# La migración es idempotente y se protege con un bloqueo de PostgreSQL.
CMD ["sh", "-c", "python -m reva_backend.manage migrar && uvicorn reva_backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
