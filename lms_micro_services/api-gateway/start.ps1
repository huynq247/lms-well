# PowerShell script to start microservices with API Gateway

Write-Host "🚀 Starting Microservices with API Gateway..." -ForegroundColor Green

# Change to API Gateway directory
Set-Location "d:\XProject\Xmicro1\api-gateway"

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker compose down

# Build and start all services
Write-Host "🏗️ Building and starting services..." -ForegroundColor Blue
docker compose up --build -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Magenta

Write-Host "Traefik Dashboard: http://localhost:8080" -ForegroundColor Green
Write-Host "API Gateway: http://localhost:80" -ForegroundColor Green

# Test endpoints through gateway
Write-Host "" 
Write-Host "🧪 Testing endpoints through API Gateway..." -ForegroundColor Yellow

Write-Host "Testing Assignment Service health:" -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost/api/assignments/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Assignment Service: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Assignment Service not ready" -ForegroundColor Red
}

Write-Host "Testing Content Service health:" -ForegroundColor White  
try {
    $response = Invoke-RestMethod -Uri "http://localhost/api/courses" -Method GET -TimeoutSec 5
    Write-Host "✅ Content Service: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Content Service not ready" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 API Gateway setup complete!" -ForegroundColor Green
Write-Host "📊 Traefik Dashboard: http://localhost:8080/dashboard/" -ForegroundColor Cyan
Write-Host "🌐 API Gateway: http://localhost/" -ForegroundColor Cyan
Write-Host "📚 Assignment Service: http://localhost/api/assignments/" -ForegroundColor Cyan
Write-Host "📖 Content Service: http://localhost/api/courses/" -ForegroundColor Cyan

Write-Host ""
Write-Host "💡 To stop services, run: docker compose down" -ForegroundColor Yellow
