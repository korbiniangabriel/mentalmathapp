#!/bin/bash
# Stop script for Mental Math Training App Docker deployment

echo "🛑 Stopping Mental Math Training App..."
echo ""

# Use docker compose (newer) or docker-compose (older)
if docker compose version &> /dev/null 2>&1; then
    docker compose down
else
    docker-compose down
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Container stopped successfully!"
else
    echo ""
    echo "❌ Failed to stop container"
    exit 1
fi
