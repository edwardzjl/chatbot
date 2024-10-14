FROM node:lts-alpine as frontend-builder

ARG PUBLIC_URL=

WORKDIR /build
COPY web/package.json web/yarn.lock ./
RUN yarn
COPY web/ ./
RUN yarn build


FROM python:3.13 as backend-builder
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install pipenv
COPY api/Pipfile api/Pipfile.lock ./
RUN pipenv install --deploy --categories="packages prod-packages"


FROM python:3.13-slim as app
WORKDIR /app
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libpq5 \
  && apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt/archives
COPY --from=backend-builder /.venv ./.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY api/ .
COPY --from=frontend-builder /build/build ./static

RUN adduser --system --no-create-home --group chatbot \
  && chown -R chatbot:chatbot /app
USER chatbot:chatbot

ENTRYPOINT [ "python", "-m", "uvicorn", "chatbot:app" ]
CMD [ "--host", "0.0.0.0", "--port", "8000" ]
