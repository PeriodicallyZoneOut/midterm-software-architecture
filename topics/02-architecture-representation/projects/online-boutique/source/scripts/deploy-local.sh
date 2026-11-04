#!/usr/bin/env bash
# Deploy the checked-in release images to a dedicated local Kind cluster.
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CLUSTER_NAME=online-boutique
NAMESPACE=online-boutique
STATE_DIR="$PROJECT_DIR/.local-demo"
PORT="${PORT:-8080}"

missing=0
for tool in docker kind kubectl; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'Missing dependency: %s\n' "$tool" >&2
    missing=1
  fi
done
if (( missing )); then
  printf 'On Arch Linux, install dependencies with: yay -S --needed docker kind kubectl\n' >&2
  exit 1
fi
if ! docker info >/dev/null; then
  printf 'Docker must be running and accessible to your current user.\n' >&2
  printf 'For socket permission denied, see docs/local-deployment.md (Docker group setup).\n' >&2
  exit 1
fi
if [[ ! "$PORT" =~ ^[0-9]{1,5}$ ]] || (( 10#$PORT < 1 || 10#$PORT > 65535 )); then
  printf 'PORT must be an integer from 1 to 65535.\n' >&2
  exit 1
fi

mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"
export KUBECONFIG="$STATE_DIR/kubeconfig"
export KIND_EXPERIMENTAL_PROVIDER=docker

# Native file copying also avoids unsupported nested OverlayFS inside the node.
if [[ "$(docker info --format '{{.Driver}}')" == native ]]; then
  export KIND_EXPERIMENTAL_CONTAINERD_SNAPSHOTTER="${KIND_EXPERIMENTAL_CONTAINERD_SNAPSHOTTER:-native}"
fi

clusters="$(kind get clusters)"
if ! grep -Fxq "$CLUSTER_NAME" <<< "$clusters"; then
  if ! kind create cluster --name "$CLUSTER_NAME" --kubeconfig "$KUBECONFIG" --wait 180s --retain; then
    logs_dir="$STATE_DIR/kind-logs-$(date +%Y%m%d-%H%M%S)"
    kind export logs --name "$CLUSTER_NAME" "$logs_dir" || true
    printf 'Cluster creation failed. Retained node and exported logs to %s\n' "$logs_dir" >&2
    printf 'Inspect the logs before removing the failed cluster with: kind delete cluster --name %s\n' "$CLUSTER_NAME" >&2
    exit 1
  fi
else
  kind export kubeconfig --name "$CLUSTER_NAME" --kubeconfig "$KUBECONFIG"
  if ! kubectl --context "kind-$CLUSTER_NAME" --request-timeout=15s get nodes; then
    printf 'Existing demo cluster is unhealthy; inspect it before deleting and recreating it.\n' >&2
    exit 1
  fi
fi

# Always select the demo context explicitly, even if another cluster is current.
kube() {
  kubectl --context "kind-$CLUSTER_NAME" "$@"
}
diagnostics() {
  kube -n "$NAMESPACE" get pods -o wide || true
  kube -n "$NAMESPACE" get events --sort-by=.lastTimestamp || true
}
trap diagnostics ERR

kube create namespace "$NAMESPACE" --dry-run=client -o yaml | kube apply -f -
kube -n "$NAMESPACE" apply -f "$PROJECT_DIR/release/kubernetes-manifests.yaml"
kube -n "$NAMESPACE" rollout status deployment --timeout=600s
kube -n "$NAMESPACE" get pods
printf '\nOpen http://localhost:%s once forwarding starts. Keep this terminal open.\n' "$PORT"
printf 'Press Ctrl+C to stop forwarding; the demo cluster will keep running.\n'
exec kubectl --context "kind-$CLUSTER_NAME" -n "$NAMESPACE" \
  port-forward --address 127.0.0.1 service/frontend "$PORT:80"
