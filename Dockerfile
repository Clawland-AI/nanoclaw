FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY src/ src/
EXPOSE 8000
HEALTHCHECK CMD python -c "import httpx; httpx.get('http://localhost:8000/healthz')" || exit 1
CMD ["uvicorn", "nanoclaw.server:app", "--host", "0.0.0.0", "--port", "8000"]