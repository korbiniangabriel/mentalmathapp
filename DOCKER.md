# Docker Deployment Guide

This guide explains how to run the Mental Math Training App using Docker and docker-compose.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)

## Quick Start

### 1. Build and Start the Container

```bash
docker-compose up -d
```

This command will:
- Build the Docker image (first time only)
- Start the container in detached mode
- Create an isolated network for the app
- Mount the `data/` directory for database persistence

### 2. Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

### 3. Stop the Container

```bash
docker-compose down
```

## Docker Commands

### Build the image

```bash
docker-compose build
```

### Start the container

```bash
# Foreground (see logs in terminal)
docker-compose up

# Background (detached mode)
docker-compose up -d
```

### View logs

```bash
# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Stop the container

```bash
# Stop but keep container
docker-compose stop

# Stop and remove container
docker-compose down

# Stop, remove container, and remove volumes
docker-compose down -v
```

### Restart the container

```bash
docker-compose restart
```

### Execute commands in the running container

```bash
# Open a shell in the container
docker-compose exec mentalmath bash

# Run Python in the container
docker-compose exec mentalmath python

# Run tests in the container
docker-compose exec mentalmath pytest tests/
```

## Configuration

### Port Mapping

The default port mapping is `8501:8501` (host:container). To change the host port, edit `docker-compose.yml`:

```yaml
ports:
  - "9000:8501"  # Access app on http://localhost:9000
```

### Resource Limits

Resource limits are configured in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '1'        # Max 1 CPU core
      memory: 512M     # Max 512MB RAM
```

Adjust these values based on your system resources.

### Data Persistence

The SQLite database is stored in the `data/` directory, which is mounted as a volume. This ensures your progress and statistics persist between container restarts.

To reset all data:
```bash
docker-compose down
rm -rf data/*.db
docker-compose up -d
```

### Network Isolation

The app runs on an isolated Docker network (`mentalmath-network`) to prevent interference with other containers. If you need to connect other services to this app, add them to the same network in your docker-compose configuration.

## Development Mode

For development with hot-reload, uncomment the source code volumes in `docker-compose.yml`:

```yaml
volumes:
  - ./data:/app/data
  - ./src:/app/src          # Uncomment for development
  - ./main.py:/app/main.py  # Uncomment for development
```

Then restart the container:
```bash
docker-compose restart
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs mentalmath
```

### Port already in use

Change the host port in `docker-compose.yml` or stop the conflicting service:
```bash
# Find what's using port 8501
lsof -i :8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Change port in docker-compose.yml
ports:
  - "8502:8501"
```

### Permission issues with data directory

Ensure the `data/` directory has proper permissions:
```bash
mkdir -p data
chmod 755 data
```

### Container is running but app is not accessible

Check if the container is healthy:
```bash
docker-compose ps
docker inspect mentalmath-app
```

Verify port forwarding:
```bash
docker-compose port mentalmath 8501
```

### Database corruption

Stop the container and remove the database:
```bash
docker-compose down
rm -rf data/*.db*
docker-compose up -d
```

## Building for Production

For production deployment:

1. Remove development volume mounts from `docker-compose.yml`
2. Build the image:
   ```bash
   docker-compose build --no-cache
   ```
3. Start in detached mode:
   ```bash
   docker-compose up -d
   ```
4. Monitor logs:
   ```bash
   docker-compose logs -f
   ```

## Security Notes

- The container runs as root by default. For production, consider creating a non-root user in the Dockerfile.
- The app is exposed on all interfaces (0.0.0.0). Use a reverse proxy (nginx, traefik) for production.
- Database files are stored locally. Ensure proper backup procedures.

## Multi-Container Deployment

To run multiple instances on different ports:

```bash
# Copy docker-compose.yml to docker-compose.instance2.yml
# Edit ports and container name
# Run with:
docker-compose -f docker-compose.instance2.yml up -d
```

Or use Docker Compose profiles for managing multiple instances in a single file.

## Health Checks

The container includes a health check that monitors the Streamlit app. View health status:

```bash
docker inspect --format='{{.State.Health.Status}}' mentalmath-app
```

## Backup and Restore

### Backup database

```bash
docker-compose exec mentalmath cp /app/data/mental_math.db /app/data/backup_$(date +%Y%m%d).db
# Or from host
cp data/mental_math.db data/backup_$(date +%Y%m%d).db
```

### Restore database

```bash
docker-compose down
cp data/backup_20231201.db data/mental_math.db
docker-compose up -d
```

## Advanced: Custom Build

To build with a different Python version or add custom dependencies:

1. Edit `Dockerfile`
2. Edit `pyproject.toml` (if needed)
3. Rebuild:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Support

For issues related to Docker deployment, check:
- Docker logs: `docker-compose logs`
- Container status: `docker-compose ps`
- Docker version: `docker --version && docker-compose --version`
