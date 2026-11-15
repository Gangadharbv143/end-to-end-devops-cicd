FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY app/ ./app/
COPY gunicorn.conf.py .
COPY docker-entrypoint.sh .

RUN chown -R appuser:appgroup /app && \
    chmod 755 /app/docker-entrypoint.sh

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"

CMD ["./docker-entrypoint.sh"]
