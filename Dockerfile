FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

COPY . .

RUN chmod +x /app/docker-entrypoint.sh && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 7860 8000

CMD ["sh", "/app/docker-entrypoint.sh"]
