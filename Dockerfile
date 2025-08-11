FROM node:lts-alpine AS frontend-builder

ARG PUBLIC_URL=
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0

WORKDIR /build
COPY web/package.json web/yarn.lock web/.yarnrc.yml ./
RUN corepack enable \
  && yarn install --immutable
COPY web/ ./
RUN yarn build


FROM python:3.13 AS backend-builder

ENV UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
COPY api/pyproject.toml api/uv.lock ./

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-uv-temporarily
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --locked --no-install-project --no-dev --group prod --no-cache


FROM python:3.13-slim AS app
WORKDIR /app
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libpq5 \
  && apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt/archives
COPY --from=backend-builder /.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY api/ .
COPY --from=frontend-builder /build/dist ./static

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --locked --no-dev --group prod --group mysql --group oracle --no-cache

RUN adduser --system --no-create-home --group chatbot \
  && chown -R chatbot:chatbot /app
USER chatbot:chatbot

EXPOSE 8000

ENTRYPOINT [ "python", "-m", "uvicorn", "chatbot.main:app" ]
CMD [ "--host", "0.0.0.0", "--port", "8000" ]
