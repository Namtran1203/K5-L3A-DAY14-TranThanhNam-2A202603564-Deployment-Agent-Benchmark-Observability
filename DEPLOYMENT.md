# Deployment Information

## Public URL
https://nam-day14-agent.onrender.com

## Platform
Render Web Service, Docker runtime. Repository branch: `main`. Root Directory: `06-lab-complete`.

## Runtime configuration
`AGENT_API_KEY` is configured in Render as a generated secret. `REDIS_URL` points to the Render Key Value internal URL. Do not copy either secret into this repository.

## Verified endpoints (2026-11-26)
- `GET /health` ? HTTP 200, `{"status":"ok"}`
- `GET /ready` ? HTTP 200, `{"status":"ready"}`
- Before Redis was configured, `/ready` returned 503. After setting `REDIS_URL` and redeploying, it returned 200.
- `GET /` returns 404 because the API has no root route; use `/health` and `/ready` instead.

## Test commands (PowerShell)
```powershell
$base = 'https://nam-day14-agent.onrender.com'
Invoke-WebRequest "$base/health"
Invoke-WebRequest "$base/ready"
# Missing key should return 401:
Invoke-WebRequest "$base/ask" -Method Post -ContentType 'application/json' -Body '{"question":"Hello"}'
# For an authenticated check, use the API key stored in Render without printing or committing it.
```

## Screenshots
Local Grafana and Prometheus evidence is in `screenshots/`. Render service dashboard and authenticated `/ask` screenshot have not been captured yet.
