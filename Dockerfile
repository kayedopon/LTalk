FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project files
COPY . /app/

# Make sure we're in the correct directory where manage.py exists
WORKDIR /app/LTalk

# Create logs directory
RUN mkdir -p /app/logs && chmod -R 777 /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput --settings=LTalk.settings_docker

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run gunicorn from the correct directory
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "LTalk.wsgi:application"]