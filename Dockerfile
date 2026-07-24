# ⚡ Hermes — AI Marketing Engine
FROM node:22-alpine

WORKDIR /app

# Install dependencies first (layer-cached)
COPY package.json ./
RUN npm install --omit=dev

# App source
COPY server.js ./
COPY hermes ./hermes
COPY web ./web

# knowledge/ and data/ are volume-mounted at runtime (see docker-compose.yml)
RUN mkdir -p knowledge data

ENV HERMES_PORT=8321
EXPOSE 8321

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD wget -qO- http://127.0.0.1:8321/api/status || exit 1

CMD ["node", "server.js"]
