# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production server stage
FROM nginx:alpine
# Copy built assets to NGINX
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom nginx config (handles SPA routing + API proxying)
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
