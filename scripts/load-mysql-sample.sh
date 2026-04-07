#!/usr/bin/env bash
# Pipe mysql_lab1_minimal_seed.sql into a running MySQL container (Docker Compose project "yelp-prototype" or any container with image mysql).
# Usage from repo root: bash scripts/load-mysql-sample.sh [container_name]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SQL="$ROOT/backend/scripts/mysql_lab1_minimal_seed.sql"

MYSQL_USER="${MYSQL_USER:-yelp}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-yelppass}"
MYSQL_DATABASE="${MYSQL_DATABASE:-yelp_db}"

if [[ -n "${1:-}" ]]; then
  CID="$1"
else
  CID="$(docker ps --filter "ancestor=mysql:8.0" -q | head -1)"
  if [[ -z "$CID" ]]; then
    CID="$(docker ps --filter "ancestor=mysql:8" -q | head -1)"
  fi
  if [[ -z "$CID" ]]; then
    echo "No running MySQL container found. Start MySQL (e.g. docker compose with mysql service), or pass container id:"
    echo "  bash scripts/load-mysql-sample.sh <container_id_or_name>"
    exit 1
  fi
fi

echo "Loading sample data into container $CID (user=$MYSQL_USER db=$MYSQL_DATABASE)..."
docker exec -i "$CID" mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < "$SQL"
echo "Done. Run migration from backend: python scripts/migrate_mysql_to_mongo.py"
