# --------- Builder Stage ---------
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder


ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# --------- Final Stage ---------
FROM python:3.14-slim-bookworm

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

COPY --from=builder --chown=app:app /app/.venv /app/.venv

COPY src /app/src
COPY tests /app/tests
COPY pyproject.toml /app/pyproject.toml

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

USER app

WORKDIR /app

# -------- replace with comment to run with gunicorn --------
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
