# Lab 2 — Kubernetes (namespace `yelp-lab2`)

## Build the backend image

From the `backend/` directory:

```bash
docker build -t yelp-lab2-backend:latest -f docker/restaurant-service/Dockerfile .
```

On Minikube, load the image into the cluster:

```bash
minikube image load yelp-lab2-backend:latest
```

(Docker Desktop Kubernetes can use locally built images directly if the builder shares the daemon.)

## Apply manifests

From the repository root:

```bash
kubectl apply -f k8s/base/
```

## Verify

```bash
kubectl get pods -n yelp-lab2
kubectl get svc -n yelp-lab2
kubectl logs -n yelp-lab2 deploy/mongodb --tail=50
kubectl logs -n yelp-lab2 deploy/restaurant-service --tail=50
```

Port-forward an API (example):

```bash
kubectl port-forward -n yelp-lab2 svc/restaurant-service 8003:8000
curl http://127.0.0.1:8003/
```

## Secrets

`k8s/base/secret.yaml` ships placeholder values. For anything beyond local dev, create a real secret (or use Sealed Secrets / external secret manager) and avoid committing production credentials.

## MySQL → Mongo migration

Run against your Lab 1 MySQL while MongoDB is reachable (local or port-forward). Example:

```bash
export DATABASE_URL='mysql+pymysql://USER:PASS@HOST:3306/yelp_db'
export MONGODB_URI='mongodb://127.0.0.1:27017'
export MONGODB_DB_NAME='yelp_db'
cd backend && python scripts/migrate_mysql_to_mongo.py
```

Sessions use a TTL index on `expires_at` in the `sessions` collection; login creates a document keyed by JWT `jti`.
