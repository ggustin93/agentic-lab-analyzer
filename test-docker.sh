#!/bin/bash
# Test script for Docker builds

echo "🐳 Testing Docker setup..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker Compose is available (both old and new syntax)
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available"
    exit 1
fi

echo "✅ Using: $COMPOSE_CMD"

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
$COMPOSE_CMD down --volumes --remove-orphans

# Build and start services
echo "🔨 Building and starting services..."
$COMPOSE_CMD up --build -d

# Check if services are running
echo "🔍 Checking service status..."
$COMPOSE_CMD ps

# Wait a bit for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 30

# Test if frontend is accessible
echo "🌐 Testing frontend accessibility..."
if curl -f http://localhost:4200 &> /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
fi

# Test if backend is accessible
echo "🔧 Testing backend accessibility..."
if curl -f http://localhost:8000 &> /dev/null; then
    echo "✅ Backend is accessible"
else
    echo "❌ Backend is not accessible"
fi

# Show logs if there are issues
echo "📝 Recent logs:"
$COMPOSE_CMD logs --tail=10

echo "🎉 Docker test completed!"