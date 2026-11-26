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
- `/` returns HTTP 404 by design; use `/health`, `/ready`, or `/ask`.
- Authenticated `/ask` success and live 429 rate-limit response remain to be checked with the key kept in Render. The key is not stored in this repository.

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

The verification script keeps the key in memory only, prints status codes, and never writes the key to a file. It sends up to 15 small mock requests and stops after the first HTTP 429.

## Environment variables
Render has `PORT`, `REDIS_URL`, `AGENT_API_KEY`, and `LOG_LEVEL` configured. `REDIS_URL` and `AGENT_API_KEY` are private values held in Render; they are excluded from this repository.

## Evidence
- [Render deployment dashboard](screenshots/render-dashboard.jpg)
- [Service running](screenshots/running.png)
- [Readiness](screenshots/ready.png)
- [Missing API key returns 401](screenshots/test-auth.png)
- Grafana and Jaeger evidence: see `screenshots/`.
