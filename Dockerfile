FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir .

EXPOSE 8000
HEALTHCHECK CMD python -c "import httpx; httpx.get('http://localhost:8000/healthz', timeout=5).raise_for_status()" || exit 1
CMD ["uvicorn", "nanoclaw.server:app", "--host", "0.0.0.0", "--port", "8000"]
