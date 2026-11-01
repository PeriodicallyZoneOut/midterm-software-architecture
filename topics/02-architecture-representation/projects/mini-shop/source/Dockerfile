FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package.json
COPY services/gateway/package.json services/gateway/package.json
COPY services/products/package.json services/products/package.json
COPY services/orders/package.json services/orders/package.json
RUN npm ci
COPY services services
ARG SERVICE
RUN npm run build --workspace=@mini/${SERVICE} && npm prune --omit=dev
FROM node:24-alpine
WORKDIR /app
ARG SERVICE
ENV NODE_ENV=production
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/services/${SERVICE}/dist ./dist
COPY --from=build /app/services/${SERVICE}/package.json ./package.json
USER node
CMD ["node", "dist/index.js"]
