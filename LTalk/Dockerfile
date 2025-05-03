FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . /app/

RUN mkdir -p /app/logs && chmod -R 777 /app/logs

# Collect static files using the correct settings path
RUN python manage.py collectstatic --noinput --settings=LTalk.settings_docker

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "LTalk.wsgi:application", "--chdir", "LTalk"]