#!/usr/bin/env bash
# Verifies the frontend container can reach backend services by Docker DNS name.
# Usage (from repo root): docker compose up -d --build && bash scripts/verify-frontend-compose-network.sh
set -euo pipefail

docker compose exec -T frontend curl -sf "http://user-service:8000/" | grep -q "user"
docker compose exec -T frontend curl -sf "http://owner-service:8000/" | grep -q "owner"
docker compose exec -T frontend curl -sf "http://restaurant-service:8000/" | grep -q "restaurant"
docker compose exec -T frontend curl -sf "http://review-service:8000/" | grep -q "review"

echo "OK: frontend container reached all four API services on the compose network."
