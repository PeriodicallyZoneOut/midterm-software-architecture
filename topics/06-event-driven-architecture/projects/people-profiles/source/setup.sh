#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
docker run --rm --user "$(id -u):$(id -g)" --volume "$PWD:/work" --workdir /work \
  node:22-bookworm-slim@sha256:4b150b48b4116e2a22f2c39cc27025fbf4f153e2078fd3b14d159fdb5c7279da node init-secrets.js
exec docker compose -p people-kurrent up -d --build --wait
