FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package.json
COPY services/gateway/package.json services/gateway/package.json
COPY services/products/package.json services/products/package.json
COPY services/orders/package.json services/orders/package.json
RUN npm ci
COPY frontend frontend
RUN npm run build --workspace=@mini/frontend
FROM nginx:alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
