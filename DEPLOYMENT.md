# Deployment

Chưa triển khai cloud: người học chưa có tài khoản Railway/Render. Không có URL hoặc ảnh deploy public.

## Cấu hình đã chuẩn bị
Root directory: 06-lab-complete. Build Dockerfile; healthcheck /health. Tạo Redis trên nền tảng, đặt REDIS_URL và AGENT_API_KEY bí mật. Đặt ENVIRONMENT=production, RATE_LIMIT_PER_MINUTE=10, DAILY_BUDGET_USD=1, MONTHLY_BUDGET_USD=10. PORT do nền tảng cấp. Không đưa secret vào repo.

## Kiểm tra sau deploy
```powershell
$base = Read-Host 'Public URL'
Invoke-WebRequest "$base/health"
Invoke-WebRequest "$base/ready"
# Thiếu key: 401
Invoke-WebRequest "$base/ask" -Method Post -ContentType 'application/json' -Body '{"question":"Hello"}'
# Đặt AGENT_API_KEY trong phiên terminal, có key: 200
Invoke-WebRequest "$base/ask" -Method Post -Headers @{'X-API-Key'=$env:AGENT_API_KEY} -ContentType 'application/json' -Body '{"question":"Hello"}'
```

Sau khi deploy, lưu dashboard.png, running.png, test.png vào screenshots. Ảnh giám sát local không thay thế ảnh deploy public.
