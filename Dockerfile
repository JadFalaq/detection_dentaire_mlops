FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-service.txt .
RUN pip install --upgrade pip && \
    pip install --default-timeout=1000 --retries 10 -r requirements-service.txt

COPY . .

EXPOSE 8000

CMD ["python", "scripts/serve_api.py", "--host", "0.0.0.0", "--port", "8000"]
