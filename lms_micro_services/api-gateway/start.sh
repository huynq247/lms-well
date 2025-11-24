#!/bin/bash

echo "🚀 Starting Microservices with API Gateway..."

# Change to API Gateway directory
cd /d/XProject/Xmicro1/api-gateway

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

echo "Traefik Dashboard: http://localhost:8080"
echo "API Gateway: http://localhost:80"

# Test endpoints through gateway
echo ""
echo "🧪 Testing endpoints through API Gateway..."

echo "Testing Assignment Service health:"
curl -s http://localhost/api/assignments/health || echo "❌ Assignment Service not ready"

echo ""
echo "Testing Content Service health:"  
curl -s http://localhost/api/courses || echo "❌ Content Service not ready"

echo ""
echo "🎉 API Gateway setup complete!"
echo "📊 Traefik Dashboard: http://localhost:8080/dashboard/"
echo "🌐 API Gateway: http://localhost/"
echo "📚 Assignment Service: http://localhost/api/assignments/"
echo "📖 Content Service: http://localhost/api/courses/"
