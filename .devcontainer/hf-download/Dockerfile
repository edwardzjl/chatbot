FROM python:3.13-slim

RUN python -m pip install \
  --no-cache-dir \
  huggingface-hub[cli]

ENV HF_HUB_ENABLE_HF_TRANSFER=0
ENV HUGGINGFACE_HUB_CACHE=/data

ENTRYPOINT ["huggingface-cli"]
