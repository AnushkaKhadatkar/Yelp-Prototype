# Week 4 JMeter Load Testing

This guide covers the required Week 4 performance runs at:

- `100` users
- `200` users
- `300` users
- `400` users
- `500` users

Using the plan:

- `jmeter/week4-load-suite.jmx`

## Endpoints covered

- `POST /auth/user/login`
- `GET /restaurants` (search)
- `POST /restaurants/{restaurant_id}/reviews` (Kafka flow path)

## Prerequisites

- API base host/port reachable from the machine running JMeter.
- Test user exists and can log in.
- `RESTAURANT_ID` points to an existing restaurant.
- If testing AWS, use your public API/ingress host.

## Recommended CLI runs

From repo root:

```bash
mkdir -p jmeter/results/week4
```

Run each concurrency level separately:

```bash
jmeter -n -t jmeter/week4-load-suite.jmx -JTHREADS=100 -JRAMP_UP=30 -JLOOPS=2 -JBASE_HOST=localhost -JBASE_PORT=8001 -l jmeter/results/week4/load-100.csv
jmeter -n -t jmeter/week4-load-suite.jmx -JTHREADS=200 -JRAMP_UP=45 -JLOOPS=2 -JBASE_HOST=localhost -JBASE_PORT=8001 -l jmeter/results/week4/load-200.csv
jmeter -n -t jmeter/week4-load-suite.jmx -JTHREADS=300 -JRAMP_UP=60 -JLOOPS=2 -JBASE_HOST=localhost -JBASE_PORT=8001 -l jmeter/results/week4/load-300.csv
jmeter -n -t jmeter/week4-load-suite.jmx -JTHREADS=400 -JRAMP_UP=75 -JLOOPS=2 -JBASE_HOST=localhost -JBASE_PORT=8001 -l jmeter/results/week4/load-400.csv
jmeter -n -t jmeter/week4-load-suite.jmx -JTHREADS=500 -JRAMP_UP=90 -JLOOPS=2 -JBASE_HOST=localhost -JBASE_PORT=8001 -l jmeter/results/week4/load-500.csv
```

If target is EKS/ALB:

- Set `-JBASE_HOST=<alb-dns-name>`
- Set `-JBASE_PORT=80` (or `443` with `-JBASE_PROTOCOL=https`)

## Metrics to record in report

For each concurrency level, capture:

- Average response time (ms)
- Throughput (requests/sec)
- Error rate (%)

Also include:

- JMeter Summary Report screenshot
- Results Tree or aggregate output screenshot
- Response-time vs concurrency graph

## Suggested analysis talking points

- Where latency starts increasing sharply
- Whether throughput plateaus
- Which endpoint fails first (login/search/review)
- Suspected bottleneck: CPU, DB, Kafka worker lag, or network/ingress
