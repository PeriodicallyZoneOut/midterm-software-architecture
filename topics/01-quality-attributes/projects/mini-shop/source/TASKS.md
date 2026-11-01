# Checklist theo giai đoạn

Chỉ đánh dấu sau khi có triển khai hoặc kết quả xác minh. Nhật ký: docs/VERIFICATION.md.

## Giai đoạn 1 — Thiết kế
- [x] Chốt phạm vi, use case và ngoài phạm vi.
- [x] Đặc tả API, schema, ownership và xử lý lỗi.
- [x] Lập test plan, tiêu chí nghiệm thu.

## Giai đoạn 2 — Nền tảng
- [x] Workspace npm, TypeScript strict, lockfile.
- [x] Dockerfile độc lập, Compose sáu container, env/volume/network.
- [x] Bootstrap schema/seed idempotent và healthcheck.

## Giai đoạn 3 — Backend
- [x] Products CRUD tối thiểu và internal resolve.
- [x] Orders snapshot, tính tiền server, transaction.
- [x] Idempotency replay/conflict/concurrent race.
- [x] Gateway whitelist, timeout, requestId, lỗi JSON.
- [x] Logging, graceful shutdown, DB recovery.

## Giai đoạn 4 — Frontend
- [x] Catalog/search/cart/localStorage.
- [x] Checkout validation, key replay sau lỗi/reload.
- [x] List/detail đơn và pagination.
- [x] Quản trị tạo/sửa/bật tắt sản phẩm.
- [x] Loading/empty/error, responsive và accessible labels.

## Giai đoạn 5 — Verify loop
- [x] Build toàn bộ và unit test.
- [x] API integration trên MariaDB thật.
- [x] E2E browser desktop/mobile.
- [x] Fault isolation: stop Products, đọc đơn cũ, từ chối đơn mới.
- [x] Recovery sau khi restart Products/database.
- [x] Persistence sau down/up, không xóa volume.
- [x] Rebuild Products không restart Orders.
- [x] Kiểm tra database ownership/network.
- [x] Failure injection xác minh rollback order và items, retry cùng key.
- [x] Ghi lỗi phát hiện, fix và kết quả chạy lại.

## Giai đoạn 6 — Bàn giao
- [x] README chạy/dừng/test/demo/troubleshooting.
- [x] Kết quả kiểm thử thực tế và giới hạn còn lại.
