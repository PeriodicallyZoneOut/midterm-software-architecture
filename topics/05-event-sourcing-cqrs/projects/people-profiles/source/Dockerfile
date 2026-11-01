FROM node:22-bookworm-slim@sha256:4b150b48b4116e2a22f2c39cc27025fbf4f153e2078fd3b14d159fdb5c7279da
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts --no-audit --no-fund
COPY --chown=node:node domain.js store.js server.js read-db.js adapter.js mq.js mq-schema.js init-db.js publisher.js consumer.js read-consumer.js email-consumer.js seed-preview.js ./
COPY --chown=node:node public ./public
COPY --chown=node:node test ./test
USER node
ENV HOST=0.0.0.0 PORT=3003
EXPOSE 3003
CMD ["node", "server.js"]
