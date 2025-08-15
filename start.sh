#!/bin/bash

echo "🚀 Starting ZeusAI - The DevOps CoPilot"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your credentials before continuing."
    echo "   Required: AWS credentials, GitHub token, OpenAI API key"
    read -p "Press Enter when you've configured .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p terraform
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Start the platform
echo "🐳 Starting ZeusAI platform..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API is not responding"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 ZeusAI is now running!"
echo ""
echo "📱 Access your dashboard:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   Grafana:      http://localhost:3001 (admin/zeusai)"
echo "   Prometheus:   http://localhost:9090"
echo ""
echo "🔧 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop platform: docker-compose down"
echo ""
echo "Happy DevOps-ing! 🚀"
