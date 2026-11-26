# Day 14 — Mission Answers

## Trạng thái
Đã triển khai Part 6, chạy Docker và đo eval/load test. Kết quả đầy đủ xem reports-readiness.txt và BENCHMARK_REPORT.md. Chưa có tài khoản cloud nên chưa có URL public.

## Part 1
### 1.1 Anti-patterns
Hardcode API key và database URL; in secret ra log; cố định port; bind localhost; bật reload; thiếu health/readiness, xác thực và quản lý shutdown.
### 1.2 Chạy basic
Route thực tế nhận query parameter: POST /ask?question=Hello, không nhận JSON body như ví dụ trong đề. Một request thành công không chứng minh production-ready.
### 1.3 So sánh
| Feature | Develop | Production | Ý nghĩa |
|---|---|---|---|
| Config | Hardcode | Env | Cùng image chạy nhiều môi trường |
| Health | Thiếu | Health/readiness | Phân biệt sống và sẵn sàng |
| Log | print, lộ key | JSON | Lọc sự kiện, không log secret |
| Shutdown | Chưa quản lý | Drain rồi đóng tài nguyên | Hạn chế mất request |

## Part 2
### 2.1 Dockerfile
Base python:3.11; WORKDIR /app. Copy requirements trước để cache layer dependency khi chỉ code thay đổi. CMD là lệnh/đối số mặc định có thể thay; ENTRYPOINT đặt executable để nhận các đối số.
### 2.2–2.3 Image
Part 6 multi-stage cài dependency vào /install rồi copy runtime cần thiết sang slim; user không phải root, HEALTHCHECK gọi /health, exec uvicorn nhận SIGTERM. Image Part 6: 238 MB theo script chấm; docker stop exit 0 sau 2,1 giây trên Windows Docker Desktop.

Đã build cả hai Dockerfile Part 2: develop 1.667.800.303 bytes (1.667,80 MB thập phân), production 239.815.504 bytes (239,82 MB), giảm khoảng 85,62%. Dữ liệu gốc: `reports/part2-image-sizes.txt`; log build lưu cùng thư mục. Kích thước đo theo `docker image inspect .Size`, không phải dung lượng nén tải qua mạng.
### 2.4 Compose
Agent dùng redis://redis:6379/0, depends_on Redis healthy. Volume và appendonly giữ dữ liệu Redis khi tạo lại container.

## Part 3
### 3.1–3.2 — Render deployment
- Public URL: https://nam-day14-agent.onrender.com
- Deployed from branch `main` with Root Directory `06-lab-complete`; service status is successful. Redis is configured in Render.
- Verified: `/health` returns 200, `/ready` returns 200, and `POST /ask` without `X-API-Key` returns 401. `/` returns 404 because the API has no root handler.
- Dashboard and endpoint evidence: `screenshots/render-dashboard.jpg`, `screenshots/running.png`, `screenshots/ready.png`, `screenshots/test-auth.png`.
- Verified authenticated `/ask` success (200) and live rate limiting (429) with `tools/verify_render_api.ps1`; the key stays private in Render.
- Keep `AGENT_API_KEY` and `REDIS_URL` in Render Environment settings, never in Git. Confirm `AGENT_API_KEY` is present; if missing, add it and wait for redeploy before testing authenticated requests.
### 3.3 Cloud Run
Cloud Build chạy pytest, build image tag commit/latest, push registry rồi deploy Cloud Run. service.yaml đặt concurrency, tài nguyên, min/max instance và secret từ Secret Manager. Shell mẫu test thiếu set -e nên exit code pytest có thể bị echo che mất; pipeline thật cần fail ngay khi test lỗi.

## Part 4
### 4.1 API key
X-API-Key được so sánh constant-time; thiếu/sai hoặc config key rỗng trả 401. Không log key.
### 4.2 JWT
JWT chứa claims, thời điểm hết hạn và chữ ký; API key thường định danh ứng dụng. Cần kiểm tra thuật toán cho phép, exp, issuer/audience theo cấu hình.
### 4.3 Rate limit
Sliding window Redis sorted set; key băm từ API key. Lua dùng thời gian Redis, remove/count/add nguyên tử. Vượt giới hạn trả 429 với Retry-After 60 giây bảo thủ. State dùng chung qua worker/restart.
### 4.4 Cost guard
Chi phí input/output token cộng Redis theo ngày/tháng UTC. Hết budget trả 402. Token mock được ước lượng từ ký tự. Check trước và record sau có thể vượt budget bởi request đồng thời; production thật cần reservation và đối soát usage.

## Part 5
### 5.1 Health
/health trả 200 khi process sống; /ready ping Redis, lỗi trả 503. /ask mất Redis trả 503, không bỏ qua guard.
### 5.2 Shutdown
Uvicorn quản lý signal, đợi request đang chạy; lifespan đóng Redis sau drain. Docker exec chuyển signal tới server PID 1. Windows bỏ qua runtime SIGTERM; xem kết quả Linux riêng nếu có.
### 5.3 Stateless
Rate limit và cost ở Redis, không nằm trong RAM worker. user_id không cho né quota API key.
### 5.4–5.5 Load balancing
Nginx phân phối request qua instance, Redis giữ quota dùng chung. Benchmark 1/3 replica và CSV nằm trong BENCHMARK_REPORT.md/benchmark-results khi hoàn tất.

## Part 6 — Output chấm
Xem reports-readiness.txt và reports/readiness-linux.txt nếu có. Script chấm và golden dataset giữ nguyên.

## AI log
- Yêu cầu: đọc hướng dẫn, hoàn thiện lab và tiếp tục sau khi cài Docker.
- AI hỗ trợ: code Part 6; KB JWT/HPA; eval/load test; sửa Dockerfile production; chạy Docker, scaling, chaos; soạn báo cáo và sửa UTF-8.
- Kiểm tra tự động: script chấm, JSON/CSV, logs và ảnh UI thực tế. Không bịa bằng chứng cloud.
- Người học chưa xác nhận tự kiểm tra hay giải thích code; cần đọc code, chạy lại và bổ sung phần tự kiểm tra trước khi nộp.

## Kết quả chấm đầy đủ trên Linux — 2026-11-26

```text
  📋 Checklist Deliverable
     ✅ Dockerfile (multi-stage, < 500 MB)
     ✅ docker-compose.yml (agent + redis)
     ✅ .dockerignore
     ✅ Health check endpoint (GET /health)
     ✅ Readiness endpoint (GET /ready)
     ✅ API Key authentication
     ✅ Rate limiting
     ✅ Cost guard
     ✅ Config từ environment variables
     ✅ Structured logging
     ✅ Graceful shutdown
     ✅ Public URL ready (Railway / Render config)
----------------------------------------------------------------
  Result: 12/12 tiêu chí đạt · 43/43 checks passed
  🎉 PASS 12/12 — PRODUCTION READY! Deploy nào!
================================================================


```

## Part 3 ? B?ng ch?ng deploy Render

Ng?y 2026-11-26, ki?m tra public service: `/health` tr? HTTP 200 `{"status":"ok"}`; `/ready` tr? HTTP 200 `{"status":"ready"}` sau khi th?m `REDIS_URL`. ???ng d?n g?c `/` tr? 404 v? ?ng d?ng ch? cung c?p API routes. URL v? l?nh ki?m tra xem DEPLOYMENT.md.
