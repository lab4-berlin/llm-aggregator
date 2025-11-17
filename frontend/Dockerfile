# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build the application (VITE_API_URL can be set as build arg or from .env.production)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration template
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Expose port (Cloud Run will set PORT env var, default to 80)
EXPOSE 80

# Install gettext for envsubst
RUN apk add --no-cache gettext

# Start nginx with PORT from environment variable (default to 80 if not set)
CMD sh -c "export PORT=\${PORT:-80} && envsubst '\$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"


