FROM node:lts-alpine as frontend-builder

ARG PUBLIC_URL=

WORKDIR /build
COPY web/package.json ./
COPY web/yarn.lock ./
RUN yarn
COPY web/ ./
RUN yarn build


FROM python:3.11-slim as app

WORKDIR /app
COPY api/requirements.txt .
RUN python -m pip install --no-cache-dir -U pip \
  && python -m pip install --no-cache-dir -r requirements.txt
COPY api/ .
COPY --from=frontend-builder /build/build ./static

RUN adduser --system --no-create-home --group chatbot \
  && chown -R chatbot:chatbot /app
USER chatbot:chatbot

ENTRYPOINT [ "uvicorn", "chatbot.main:app" ]
CMD [ "--host", "0.0.0.0", "--port", "8080" ]
