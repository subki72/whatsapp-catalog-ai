FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

CMD ["sh", "/app/docker-entrypoint.sh"]
