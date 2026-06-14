FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# ── Dépendances système minimales ────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Dépendances Python ───────────────────────────────────────────────────────
COPY requirements-service.txt .
RUN pip install --upgrade pip && \
    pip install --default-timeout=1000 --retries 10 -r requirements-service.txt

# ── Code source ──────────────────────────────────────────────────────────────
COPY src/ ./src/
COPY scripts/serve_api.py ./scripts/serve_api.py
COPY configs/ ./configs/
COPY pyproject.toml .
COPY setup.cfg .

# ── Installation du package ──────────────────────────────────────────────────
RUN pip install -e .

# ── Checkpoint Champion (inclus dans l'image pour démo autonome) ─────────────
COPY models/checkpoints/champion/weights/best.pt \
     ./models/checkpoints/champion/weights/best.pt

# ── Port et commande de démarrage ────────────────────────────────────────────
EXPOSE 8000

CMD ["python", "scripts/serve_api.py", "--host", "0.0.0.0", "--port", "8000"]
