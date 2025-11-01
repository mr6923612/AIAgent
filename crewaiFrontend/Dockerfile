# Use Node.js 18 official image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies, as vite is needed for build)
RUN npm ci

# Copy application code
COPY . .

# Build application
RUN npm run build

# Use nginx to serve static files
FROM nginx:alpine

# Copy built files to nginx directory
COPY --from=0 /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
