FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY activity_logger/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /install

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /install /usr/local/lib/python3.11/site-packages
COPY activity_logger/ ./activity_logger/

ENV PYTHONPATH=/app
EXPOSE 8082
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8082/health')" || exit 1
CMD ["uvicorn", "activity_logger.main:app", "--host", "0.0.0.0", "--port", "8082", "--log-level", "info"]
