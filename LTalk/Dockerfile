FROM python:3.12-slim

# 1. Set workdir & install system deps
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV DJANGO_SETTINGS_MODULE=LTalk.settings_docker

WORKDIR /LTalk
RUN apt-get update && apt-get install -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Install python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 3. Copy project
COPY . .

# 4. Collect static at build time (optional); else run it in entrypoint
# RUN python manage.py collectstatic --no-input

EXPOSE 8000
