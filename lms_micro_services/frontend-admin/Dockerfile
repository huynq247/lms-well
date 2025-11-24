# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY bun.lockb* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_API_BASE_URL
ARG VITE_AUTH_SERVICE_URL
ARG VITE_CONTENT_SERVICE_URL
ARG VITE_ASSIGNMENT_SERVICE_URL
ARG VITE_APP_NAME
ARG VITE_APP_VERSION
ARG VITE_ENABLE_DEBUG_LOGS
ARG VITE_ENABLE_ANALYTICS

# Set environment variables
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_AUTH_SERVICE_URL=$VITE_AUTH_SERVICE_URL
ENV VITE_CONTENT_SERVICE_URL=$VITE_CONTENT_SERVICE_URL
ENV VITE_ASSIGNMENT_SERVICE_URL=$VITE_ASSIGNMENT_SERVICE_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_VERSION=$VITE_APP_VERSION
ENV VITE_ENABLE_DEBUG_LOGS=$VITE_ENABLE_DEBUG_LOGS
ENV VITE_ENABLE_ANALYTICS=$VITE_ENABLE_ANALYTICS

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
