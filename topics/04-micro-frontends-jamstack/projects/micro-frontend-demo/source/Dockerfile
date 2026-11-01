FROM node:22-alpine AS build
WORKDIR /app
RUN npm install --global --force yarn@1.22.22
COPY package.json yarn.lock .yarnrc.yml ./
COPY main/package.json ./main/package.json
COPY products/package.json ./products/package.json
COPY cart/package.json ./cart/package.json
COPY scripts/prepare-docker.mjs ./scripts/prepare-docker.mjs
# Install only the Webpack build tools and libraries imported by the apps.
RUN node scripts/prepare-docker.mjs
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn yarn install --frozen-lockfile --non-interactive --ignore-optional --registry https://registry.npmjs.org
COPY . .
# Restore the narrowed manifests after copying source so federation shares runtime libraries only.
RUN node scripts/prepare-docker.mjs && npm run build:docker

FROM nginx:stable-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
