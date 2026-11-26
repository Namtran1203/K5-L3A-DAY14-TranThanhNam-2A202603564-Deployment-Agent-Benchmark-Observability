FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
RUN useradd --create-home agent
COPY app ./app
COPY utils ./utils
USER agent
ENV PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,os; urllib.request.urlopen('http://localhost:'+os.getenv('PORT','8000')+'/health',timeout=2)"
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-graceful-shutdown 8"]
