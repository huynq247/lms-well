# 🌐 API Gateway with Traefik

This directory contains the API Gateway configuration using Traefik to route requests between microservices.

## 🏗️ Architecture

```
Client → Traefik (Port 80) → Assignment Service (Port 8004)
                            → Content Service (Port 8002)
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Ports 80, 8080 available

### Start All Services
```bash
# Windows PowerShell
./start.ps1

# Linux/Mac  
chmod +x start.sh
./start.sh
```

### Manual Start
```bash
cd api-gateway
docker-compose up --build -d
```

## 📊 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Traefik Dashboard | http://localhost:8080 | Gateway monitoring |
| API Gateway | http://localhost | Main entry point |
| Assignment Service | http://localhost/api/assignments | Assignment endpoints |
| Content Service | http://localhost/api/courses | Content endpoints |

## 🛣️ Routing Rules

### Assignment Service Routes
- `/api/assignments/*` → assignment-service:8004
- `/api/progress/*` → assignment-service:8004  
- `/api/sessions/*` → assignment-service:8004
- `/api/analytics/*` → assignment-service:8004

### Content Service Routes
- `/api/content/*` → content-service:8002
- `/api/courses/*` → content-service:8002
- `/api/decks/*` → content-service:8002

## 🔧 Configuration

### Traefik Configuration
- `traefik.yml` - Static configuration
- `dynamic.yml` - Dynamic routing rules
- `docker-compose.yml` - Service orchestration

### Features Enabled
- ✅ Load balancing
- ✅ Health checks
- ✅ CORS middleware
- ✅ Rate limiting
- ✅ Request logging
- ✅ Circuit breaker
- ✅ Service discovery

## 🧪 Testing

### Health Checks
```bash
# Check all services
curl http://localhost/api/assignments/health
curl http://localhost/api/courses

# Check Traefik
curl http://localhost:8080/ping
```

### Sample API Calls
```bash
# Create assignment through gateway
curl -X POST http://localhost/api/assignments \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Assignment","student_id":1}'

# Get courses through gateway  
curl http://localhost/api/courses
```

## 🔍 Monitoring

### Traefik Dashboard
- URL: http://localhost:8080/dashboard/
- Shows real-time routing, health, and metrics

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f traefik
docker-compose logs -f assignment-service
docker-compose logs -f content-service
```

## 🛑 Stop Services

```bash
docker-compose down

# Remove volumes (reset data)
docker-compose down -v
```

## 🔧 Development

### Environment Variables
- Services auto-discover each other via Docker network
- Database connections configured in docker-compose.yml
- CORS enabled for development

### Adding New Service
1. Add service to `docker-compose.yml`
2. Add routing rules in labels
3. Update `dynamic.yml` if needed

## 📈 Performance

### Current Configuration
- Rate limit: 50 requests/second (burst 100)
- Health check interval: 30 seconds
- Connection timeout: 5 seconds

### Scaling
```bash
# Scale specific service
docker-compose up -d --scale assignment-service=3
```

## 🚨 Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 80, 8080 are free
2. **Service not starting**: Check `docker-compose logs [service]`
3. **Routing issues**: Verify Traefik dashboard
4. **Database connections**: Check network connectivity

### Debug Commands
```bash
# Check running containers
docker ps

# Check networks
docker network ls

# Inspect service
docker-compose exec traefik /bin/sh
```
