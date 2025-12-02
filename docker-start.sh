#!/bin/bash
# Quick start script for Mental Math Training App Docker deployment

echo "🐳 Mental Math Training App - Docker Startup"
echo "=============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Check if container is already running
if docker ps --format '{{.Names}}' | grep -q "^mentalmath-app$"; then
    echo "ℹ️  Container is already running"
    echo ""
    echo "To restart: docker-compose restart"
    echo "To stop: docker-compose down"
    echo "To view logs: docker-compose logs -f"
    echo ""
    echo "📱 Access the app at: http://localhost:8501"
    exit 0
fi

# Start the container
echo "🚀 Starting Mental Math Training App..."
echo ""

# Use docker compose (newer) or docker-compose (older)
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Container started successfully!"
    echo ""
    echo "📱 Access the app at: http://localhost:8501"
    echo ""
    echo "Useful commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop app: docker-compose down"
    echo "  • Restart app: docker-compose restart"
    echo ""
else
    echo ""
    echo "❌ Failed to start container"
    echo "Check the logs with: docker-compose logs"
    exit 1
fi
