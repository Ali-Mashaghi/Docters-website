FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' docker/entrypoint.sh && chmod +x docker/entrypoint.sh

RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

ENTRYPOINT ["docker/entrypoint.sh"]
