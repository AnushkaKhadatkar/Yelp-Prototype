# Lab 2 — Kubernetes (namespace `yelp-lab2`)

## No Kubernetes in Docker Desktop? Use Kind (recommended)

[Kind](https://kind.sigs.k8s.io/) runs a real Kubernetes API using Docker containers — you do **not** need the Docker Desktop “Kubernetes” toggle.

1. Install: `brew install kind kubectl` (macOS) or see [Kind installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).
2. From the repo root:

```bash
bash scripts/kind-yelp-lab2.sh
```

3. Build the image, load it into Kind, and apply manifests. Files in `k8s/base/` are prefixed (`00-namespace.yaml`, …) so the **namespace** is created before other resources.

```bash
cd backend
docker build -t yelp-lab2-backend:latest -f docker/restaurant-service/Dockerfile .
kind load docker-image yelp-lab2-backend:latest --name yelp-lab2
cd ..
kubectl apply -f k8s/base/
```

4. Verify: `kubectl get pods -n yelp-lab2` (expect `Running` for `mongodb` and all four API pods; first start may take a minute while images pull.)

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

## Verify backend uses MongoDB in Kubernetes

Use this to show that APIs run against the in-cluster MongoDB and that `MONGODB_URI` / `MONGODB_DB_NAME` come from the ConfigMap and Secret (`k8s/base/02-configmap.yaml`, `k8s/base/01-secret.yaml`), not from a local `.env` on your machine.

**1. Pods and Services**

```bash
kubectl get pods,svc -n yelp-lab2
```

Expect `mongodb` and the four backend pods in `Running`, plus Services `mongodb` (27017) and the four APIs (8000).

**2. Environment inside a backend pod**

```bash
kubectl exec -n yelp-lab2 deploy/user-service -- printenv MONGODB_URI MONGODB_DB_NAME
```

Expect `mongodb://mongodb:27017/yelp_db` and `yelp_db` (Service DNS name `mongodb` inside the namespace).

**3. Optional: Mongo ping over HTTP**

After rebuilding the backend image and reloading it into the cluster, port-forward any backend Service. `GET /health/db` runs `ping` against the same database the app uses (`backend/main.py`):

```bash
kubectl port-forward -n yelp-lab2 svc/user-service 8001:8000
curl -s http://127.0.0.1:8001/health/db
```

**Important:** If you run `kubectl rollout restart` (or pods are replaced), **stop the old port-forward (Ctrl+C) and start a new one.** A stale forward often still accepts TCP on your laptop but talks to a dead pod, which shows up as `curl: (52) Empty reply from server`. Confirm the tunnel with `curl -s http://127.0.0.1:8001/` first (should return JSON from `GET /`).

**4. End-to-end: API write → document in Mongo**

Signups are handled by `user-service`. Forward it, create a user with a **unique** email, then query Mongo in the cluster:

```bash
kubectl port-forward -n yelp-lab2 svc/user-service 8001:8000
```

```bash
curl -s -X POST "http://127.0.0.1:8001/auth/user/signup" \
  -H "Content-Type: application/json" \
  -d '{"name":"K8s Proof","email":"your-unique-email@example.com","password":"password123"}'
```

```bash
kubectl exec -n yelp-lab2 deploy/mongodb -- mongosh yelp_db --quiet \
  --eval 'db.users.find({email:"your-unique-email@example.com"}).toArray()'
```

If port `8001` is already in use on your machine, pick another local port in the `port-forward` command (e.g. `18001:8000`) and use that port in the `curl` URLs.

**5. Data scope**

The MongoDB Pod in the cluster is separate from `docker compose` MongoDB on your host. To load migrated data into cluster Mongo, port-forward `svc/mongodb` to localhost and run `migrate_mysql_to_mongo.py` with `MONGODB_URI=mongodb://127.0.0.1:27017` while the forward is active. Signup alone is enough to prove writes without migration.

## Secrets

`k8s/base/01-secret.yaml` ships placeholder values. For anything beyond local dev, create a real secret (or use Sealed Secrets / external secret manager) and avoid committing production credentials.

## MySQL → Mongo migration

**Full dataset (recommended):** use `seed_data.py` so MySQL gets **15 users, 60 restaurants**, and **3–8 reviews per restaurant** (same idea as the original script). Tables must already exist (run `mysql_lab1_minimal_seed.sql` once if this is a brand-new database).

```bash
cd backend
pip install -r requirements.txt   # includes Faker
export MYSQL_HOST=127.0.0.1 MYSQL_PORT=3307 MYSQL_USER=yelp MYSQL_PASSWORD=yelppass MYSQL_DATABASE=yelp_db
python seed_data.py --fresh
```

All seeded users share password `password123` (override with `SEED_USER_PASSWORD`).

**Tiny sample only (2 restaurants):**

```bash
mysql -h 127.0.0.1 -P 3307 -uyelp -pyelppass yelp_db < scripts/mysql_lab1_minimal_seed.sql
```

Then migrate while MongoDB is running (e.g. `docker compose up mongodb`):

```bash
export DATABASE_URL='mysql+pymysql://USER:PASS@HOST:3307/yelp_db'
export MONGODB_URI='mongodb://127.0.0.1:27017'
export MONGODB_DB_NAME='yelp_db'
cd backend && python scripts/migrate_mysql_to_mongo.py
```

The script prints MySQL row counts first and **does not wipe Mongo** if `users` is empty (unless you pass `--allow-empty`).

Sessions use a TTL index on `expires_at` in the `sessions` collection; login creates a document keyed by JWT `jti`.

## Troubleshooting: `kubectl` connection refused (`localhost:8080`)

That means **no Kubernetes API server** is reachable with your current kubeconfig (the default “no cluster” config points at `http://localhost:8080`).

Do one of the following:

1. **Docker Desktop** — Settings → **Kubernetes** → enable Kubernetes, wait until it shows **running**, then run:
   `kubectl cluster-info`
2. **Minikube** — `minikube start`, then:
   `kubectl config use-context minikube`
3. **Kind / other** — use the context that tool prints after cluster creation.

Verify before `kubectl apply`:

```bash
kubectl cluster-info
kubectl get nodes
```

If these work, `kubectl apply -f k8s/base/` should succeed.
