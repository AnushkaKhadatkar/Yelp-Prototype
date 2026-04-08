#!/usr/bin/env bash
# Create a local Kubernetes cluster with Kind (works with plain Docker — no Docker Desktop K8s required).
# Usage: from repo root, bash scripts/kind-yelp-lab2.sh
set -euo pipefail

CLUSTER_NAME="${KIND_CLUSTER_NAME:-yelp-lab2}"

if ! command -v kind >/dev/null 2>&1; then
  echo "kind is not installed. Install it, then re-run:"
  echo "  macOS:  brew install kind"
  echo "  see:   https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
  exit 1
fi

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is not installed. Install via Docker Desktop tools or: brew install kubectl"
  exit 1
fi

if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  echo "Kind cluster '$CLUSTER_NAME' already exists."
else
  echo "Creating Kind cluster '$CLUSTER_NAME'..."
  kind create cluster --name "$CLUSTER_NAME"
fi

echo "kubectl context:"
kubectl config current-context
kubectl cluster-info
kubectl get nodes

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo ""
echo "Build and load backend image into Kind:"
echo "  cd \"$ROOT/backend\" && docker build -t yelp-lab2-backend:latest -f docker/restaurant-service/Dockerfile ."
echo "  kind load docker-image yelp-lab2-backend:latest --name $CLUSTER_NAME"
echo ""
echo "Apply manifests:"
echo "  kubectl apply -f \"$ROOT/k8s/base/\""
