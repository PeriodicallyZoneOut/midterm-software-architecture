#!/usr/bin/env bash
# Add the Hello feature to the existing local demo cluster.
set -Eeuo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME=online-boutique
NAMESPACE="${NAMESPACE:-online-boutique}"
export KUBECONFIG="${KUBECONFIG:-$PROJECT_DIR/.local-demo/kubeconfig}"
export KIND_EXPERIMENTAL_PROVIDER=docker

for tool in docker kind kubectl python; do
  command -v "$tool" >/dev/null || { printf 'Missing dependency: %s\n' "$tool" >&2; exit 1; }
done
docker info >/dev/null
kube() {
  kubectl --context "kind-$CLUSTER_NAME" -n "$NAMESPACE" "$@"
}
if ! kube --request-timeout=15s get nodes; then
  printf 'Start a healthy local cluster first with: bash scripts/deploy-local.sh\n' >&2
  exit 1
fi
diagnostics() {
  kube get pods,pvc || true
  kube get events --sort-by=.lastTimestamp || true
}
trap diagnostics ERR

docker build -t frontend:hello-local "$PROJECT_DIR/src/frontend"
docker build -t helloservice:hello-local "$PROJECT_DIR/src/helloservice"
kind load docker-image --name "$CLUSTER_NAME" frontend:hello-local helloservice:hello-local

kube create namespace "$NAMESPACE" --dry-run=client -o yaml | kube apply -f -
if [[ -z "$(kube get secret hello-db-credentials --ignore-not-found -o name)" ]]; then
  python - <<'PY' | kube create -f -
import json
import secrets
print(json.dumps({
    "apiVersion": "v1", "kind": "Secret",
    "metadata": {"name": "hello-db-credentials"},
    "type": "Opaque",
    "stringData": {"password": secrets.token_urlsafe(32),
                   "root-password": secrets.token_urlsafe(32)},
}))
PY
fi
kube apply -k "$PROJECT_DIR/kustomize/hello-local"
kube rollout status statefulset/hello-db --timeout=300s
# Fixed local image tags must restart existing pods after the new images are loaded.
kube rollout restart deployment/frontend deployment/helloservice
kube rollout status deployment/helloservice --timeout=180s
kube rollout status deployment/frontend --timeout=180s
printf '\nHello is deployed. Open the home page and click Get Hello.\n'
printf 'If needed, start forwarding in another terminal:\n'
printf 'KUBECONFIG=%q kubectl --context kind-%s -n %q port-forward service/frontend 8080:80\n' \
  "$KUBECONFIG" "$CLUSTER_NAME" "$NAMESPACE"
