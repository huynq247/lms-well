# LearnHub Frontend - Admin Portal Integration

## Overview
LearnHub Frontend is integrated with the LMS microservices backend to provide a modern, responsive admin interface built with:
- **Vite** - Fast build tool
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Shadcn/UI** - Modern component library
- **TailwindCSS** - Utility-first styling
- **React Query** - Server state management
- **React Router** - Client-side routing
- **Axios** - HTTP client

## Backend Integration

### API Services Configuration
The frontend is configured to communicate with 4 backend microservices:

1. **API Gateway** (Port 8000) - Main entry point
2. **Auth Service** (Port 8001) - Authentication & authorization
3. **Content Service** (Port 8002) - Courses & lessons management
4. **Assignment Service** (Port 8004) - Assignments & submissions

### Environment Configuration

**Development** (`.env.development`):
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_SERVICE_URL=http://localhost:8001
VITE_CONTENT_SERVICE_URL=http://localhost:8002
VITE_ASSIGNMENT_SERVICE_URL=http://localhost:8004
```

**Production** (`.env.production`):
```bash
VITE_API_BASE_URL=http://14.161.50.86:8000
VITE_AUTH_SERVICE_URL=http://14.161.50.86:8001
VITE_CONTENT_SERVICE_URL=http://14.161.50.86:8002
VITE_ASSIGNMENT_SERVICE_URL=http://14.161.50.86:8004
```

## Project Structure

```
learnhub-frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── config/          # Configuration files
│   │   └── index.ts     # Environment config
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility functions
│   ├── pages/           # Route pages
│   │   ├── admin/       # Admin-specific pages
│   │   │   └── AdminDashboard.tsx
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   └── ...
│   ├── services/        # API service layer
│   │   ├── api.ts       # Axios client setup
│   │   ├── auth.ts      # Authentication service
│   │   └── content.ts   # Content service
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── Dockerfile           # Docker build configuration
├── nginx.conf           # Nginx server configuration
├── .env.development     # Development environment vars
├── .env.production      # Production environment vars
└── package.json         # Dependencies
```

## Key Features

### 1. Authentication
- JWT token-based authentication
- Automatic token injection in API requests
- Token storage in localStorage
- Auto-redirect on 401 (unauthorized)

### 2. API Client (`src/services/api.ts`)
- Centralized Axios instance
- Request/response interceptors
- Automatic error handling
- Debug logging in development

### 3. Service Layer
- **Auth Service**: Login, logout, registration, current user
- **Content Service**: CRUD operations for courses and lessons
- Extensible for additional services

### 4. Admin Routes
- `/login` - Admin login page
- `/admin/dashboard` - Admin dashboard
- `/dashboard` - User dashboard
- `/course/:id` - Course details
- `/learning/:id` - Learning interface

## Development

### Local Development
```bash
# Install dependencies
npm install

# Start development server (port 8080)
npm run dev

# Build for development
npm run build:dev
```

### Testing with Backend
Ensure all 4 backend services are running:
```bash
# Start backend services
sudo docker compose up -d api-gateway auth-service content-service assignment-service

# Verify services are healthy
sudo docker ps
```

## Docker Deployment

### Build and Run with Docker Compose
```bash
# Build and start learnhub-frontend
sudo docker compose up -d --build learnhub-frontend

# Check status
sudo docker ps | grep learnhub

# View logs
sudo docker compose logs -f learnhub-frontend
```

### Access Points
- **Frontend**: http://localhost:3005
- **Health Check**: http://localhost:3005/health

### Manual Docker Build
```bash
cd lms_micro_services/learnhub-frontend

# Build image
sudo docker build -t lms-learnhub-frontend \
  --build-arg VITE_API_BASE_URL=http://14.161.50.86:8000 \
  --build-arg VITE_AUTH_SERVICE_URL=http://14.161.50.86:8001 \
  --build-arg VITE_CONTENT_SERVICE_URL=http://14.161.50.86:8002 \
  --build-arg VITE_ASSIGNMENT_SERVICE_URL=http://14.161.50.86:8004 \
  .

# Run container
sudo docker run -d \
  -p 3005:80 \
  --name lms-learnhub-frontend \
  lms-learnhub-frontend
```

## API Integration Examples

### Login Example
```typescript
import authService from '@/services/auth';

const handleLogin = async () => {
  try {
    const response = await authService.login({
      email: 'admin@example.com',
      password: 'password123'
    });
    console.log('Logged in:', response.user);
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

### Fetch Courses Example
```typescript
import contentService from '@/services/content';

const fetchCourses = async () => {
  try {
    const courses = await contentService.getCourses();
    console.log('Courses:', courses);
  } catch (error) {
    console.error('Failed to fetch courses:', error);
  }
};
```

## Architecture Benefits

### Compared to frontend-admin (React CRA)
1. **Faster Build**: Vite vs Create React App (10x faster)
2. **Modern UI**: Shadcn/UI components (headless, accessible)
3. **Better DX**: Hot Module Replacement, faster refresh
4. **Type Safety**: Full TypeScript integration
5. **Smaller Bundle**: Better tree-shaking and optimization
6. **Modern React**: Uses React 18 features

### Integration with Backend
- Clean service layer separation
- Type-safe API calls with TypeScript interfaces
- Centralized error handling
- Automatic authentication token management
- Debug logging for development

## Troubleshooting

### Backend Connection Issues
```bash
# Check if backend services are running
sudo docker ps

# Check backend logs
sudo docker compose logs api-gateway
sudo docker compose logs auth-service
```

### Frontend Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Port Conflicts
```bash
# Check if port 3005 is in use
sudo lsof -i :3005

# Use different port in docker-compose.yml
ports:
  - "3006:80"  # Change 3005 to 3006
```

## Next Steps

1. **Add More Admin Pages**:
   - User management
   - Course management
   - Assignment grading
   - Analytics dashboard

2. **Implement Role-Based Access Control**:
   - Protected routes
   - Permission checks
   - Admin-only features

3. **Enhanced Features**:
   - Real-time notifications
   - File upload management
   - Rich text editor for content
   - Video player integration

4. **Testing**:
   - Unit tests with Vitest
   - Integration tests
   - E2E tests with Playwright

## Resources
- [Vite Documentation](https://vitejs.dev/)
- [Shadcn/UI Components](https://ui.shadcn.com/)
- [React Query](https://tanstack.com/query/latest)
- [Axios Documentation](https://axios-http.com/)
