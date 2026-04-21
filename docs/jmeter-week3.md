# Week 3 JMeter Smoke Test

Initial JMeter smoke plan for Week 3 is at:

- `jmeter/week3-login-smoke.jmx`

## What it does

- Runs one thread group with `10` users and `10s` ramp-up.
- Sends `POST /auth/user/login` requests to `http://${BASE_HOST}:${BASE_PORT}`.
- Uses variables for host, port, email, and password.

## Default variables

- `BASE_HOST=localhost`
- `BASE_PORT=8001`
- `LOGIN_EMAIL=testuser@example.com`
- `LOGIN_PASSWORD=password123`

## Run from CLI

```bash
jmeter -n -t jmeter/week3-login-smoke.jmx -l jmeter/week3-login-results.csv
```

Then open JMeter GUI and load the `.jmx` + result CSV for screenshots.
