# Deployment Information

## Public service
- URL: https://nam-day14-agent.onrender.com
- Platform: Render Web Service (Docker)
- Repository branch: `main`; Render Root Directory: `06-lab-complete`
- Current service plan: Free instance; it may sleep while idle.

## Verified public endpoints (2026-11-26)
- `GET /health` → HTTP 200, `{"status":"ok"}`
- `GET /ready` → HTTP 200, `{"status":"ready"}` (Redis is connected)
- `POST /ask` without `X-API-Key` → HTTP 401, `{"detail":"Invalid API key"}`
- `POST /ask` with `AGENT_API_KEY` → HTTP 200; repeated calls eventually returned HTTP 429 in the live rate-limit check.
- `/` returns HTTP 404 by design; use `/health`, `/ready`, or `/ask`.
- The API key is stored in Render and is not included in this repository.

## Test commands (PowerShell)
```powershell
$base = 'https://nam-day14-agent.onrender.com'
Invoke-WebRequest "$base/health"
Invoke-WebRequest "$base/ready"
# This request should return 401 without X-API-Key:
Invoke-WebRequest "$base/ask" -Method Post -ContentType 'application/json' -Body '{"user_id":"test","question":"Hello"}'
# To verify a valid key and the 10 requests/minute limit, enter it at a hidden prompt:
.\tools\verify_render_api.ps1
```

The verification script asks for the `AGENT_API_KEY` value using a hidden prompt, keeps it in memory only, prints status codes, and never writes the key to a file. It sends up to 15 small mock requests and stops after the first HTTP 429. Run it after confirming that the variable exists and the redeploy is live.

## Environment variables
`REDIS_URL` is configured in Render and `/ready` confirms Redis is reachable. Confirm that `AGENT_API_KEY` also exists under the service's Environment settings. If it is missing, add that exact variable with a long, random value, save the change, and wait for the service to redeploy. Keep the value in Render; do not commit it. `PORT` is supplied by Render, and `LOG_LEVEL` can remain at its default.

## Evidence
- [Render deployment dashboard](screenshots/render-dashboard.jpg)
- [Service running](screenshots/running.png)
- [Readiness](screenshots/ready.png)
- [Missing API key returns 401](screenshots/test-auth.png)
- Grafana and Jaeger evidence: see `screenshots/`.
