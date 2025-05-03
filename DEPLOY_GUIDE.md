# LTalk Deployment Guide

This guide explains how to deploy the LTalk application to an SSH server using Docker.

## Prerequisites

Before deployment, ensure you have:

1. Access to an SSH server with Docker and Docker Compose installed
2. Basic knowledge of Docker and Linux commands
3. A domain name (optional but recommended for production)

## Files Overview

The deployment setup consists of these key files:

- `Dockerfile`: Defines how to build the Django application container
- `docker-compose.yml`: Orchestrates the web app, database, and Nginx services
- `nginx/nginx.conf`: Configures Nginx to serve the application and static files
- `settings_docker.py`: Production settings for the Django application
- `env.example`: Example environment variables (to be copied to `.env`)
- `deploy.sh`: Deployment script to automate the process
- `requirements.txt`: Python dependencies for the application

## Deployment Steps

### 1. Prepare Your Environment

1. SSH into your server:
   ```
   ssh username@your-server-ip
   ```

2. Clone your repository or upload your project files to the server.

3. Navigate to your project directory:
   ```
   cd path/to/LTalk
   ```

4. Copy the example environment file and edit it:
   ```
   cp env.example .env
   nano .env
   ```

   Update the following settings:
   - Set a secure `SECRET_KEY`
   - Add your domain to `ALLOWED_HOSTS`
   - Set a strong PostgreSQL password
   - Add your Google Gemini API key

### 2. Run the Deployment Script

1. Make the deployment script executable:
   ```
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```
   ./deploy.sh
   ```

3. Follow the prompts to create a superuser when asked.

### 3. Access Your Application

After a successful deployment, you can access:

- Your application: `http://your-server-ip` (or your domain if configured)
- API documentation: `http://your-server-ip/api/docs/`
- Admin interface: `http://your-server-ip/admin/`

## Understanding Static Files Configuration

The static files issue has been resolved by:

1. Setting `STATIC_ROOT = BASE_DIR / 'staticfiles'` in the production settings
2. Adding a volume mount in Docker Compose to share static files between the Django app and Nginx
3. Using the `collectstatic` command in the Dockerfile to collect all static files to the STATIC_ROOT
4. Configuring Nginx to serve static files directly from the mounted volume

## Managing Your Deployment

### Viewing Logs

```
docker-compose logs -f
```

To view logs for a specific service:
```
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

### Stopping the Application

```
docker-compose down
```

### Restarting After Changes

If you make changes to your code:

```
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Migrations

To run migrations after model changes:

```
docker-compose exec web python manage.py migrate --settings=LTalk.settings_docker
```

### Backup and Restore Database

To backup:
```
docker-compose exec db pg_dump -U postgres ltalk > backup.sql
```

To restore:
```
cat backup.sql | docker-compose exec -T db psql -U postgres ltalk
```

## Troubleshooting

### Static Files Not Loading

1. Check if static files are collected properly:
   ```
   docker-compose exec web ls -la /app/staticfiles/
   ```

2. Verify Nginx configuration:
   ```
   docker-compose exec nginx nginx -t
   ```

3. Ensure the volume is properly mounted:
   ```
   docker-compose config
   ```

### Database Connection Issues

1. Check if the database container is running:
   ```
   docker-compose ps
   ```

2. Verify the database settings in `.env` match those in `docker-compose.yml`

### Application Errors

1. Check the application logs:
   ```
   docker-compose logs web
   ```

2. Verify the Django settings are correctly loading:
   ```
   docker-compose exec web python manage.py check --settings=LTalk.settings_docker
   ```

## Security Considerations

For a production deployment, consider:

1. Using HTTPS with Let's Encrypt
2. Adding a firewall (UFW) to limit access
3. Setting up regular database backups
4. Implementing rate limiting for the API
5. Regularly updating dependencies

---

By following this guide, you should have a working deployment of LTalk on your SSH server with properly configured static files. 