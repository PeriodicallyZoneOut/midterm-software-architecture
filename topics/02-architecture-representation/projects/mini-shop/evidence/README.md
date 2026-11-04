# Evidence — Mini Shop (Chủ đề 2: Architecture Representation)

Thư mục này lưu bằng chứng kiểm chứng runtime (log, report, screenshot) trên môi trường máy của người phụ trách Chủ đề 2.

## 1. Bằng chứng lịch sử có sẵn trong `source/docs/` (Làm đối chiếu cơ sở)

* [`source/docs/VERIFICATION.md`](../source/docs/VERIFICATION.md): Tổng hợp kết quả kiểm chứng build, unit test, API integration, transaction rollback, stack lifecycle và browser E2E.
* [`source/docs/build-unit-verification.log`](../source/docs/build-unit-verification.log): Log `npm run verify` (build 4 workspaces + 5 unit tests).
* [`source/docs/api-verification.log`](../source/docs/api-verification.log): Log `npm run test:api` (kiểm chứng CRUD products, snapshot giá khi đổi giá sản phẩm, idempotency replay `200`, conflict `409`, chặn `/internal/*`).
* [`source/docs/transaction-verification.log`](../source/docs/transaction-verification.log): Log `npm run test:transaction` (kiểm chứng rollback nguyên tử khi lỗi ở dòng `order_items` thứ 2).
* [`source/docs/stack-verification.log`](../source/docs/stack-verification.log): Log `npm run test:stack` (kiểm chứng stop/start `products`, fault isolation và redeploy độc lập).
* [`source/docs/screenshots/`](../source/docs/screenshots/): Ảnh chụp giao diện Catalog, Cart, Order Detail và Admin.

## 2. Quy trình thu thập Evidence mới trên máy cá nhân trước buổi thi

Khi bật **Docker Desktop**, chạy các lệnh sau từ `topics/02-architecture-representation/projects/mini-shop/source` để xuất log mới nhất vào thư mục `evidence/` này:

```powershell
cd e:\KTPM\midterm-software-architecture\topics\02-architecture-representation\projects\mini-shop\source

# 1. Khởi động stack và lưu trạng thái container
docker compose up --build -d --wait
docker compose ps > ..\evidence\01-docker-compose-ps.txt

# 2. Chạy kiểm thử tự động (sau khi đã chạy npm ci) và lưu log
npm run verify > ..\evidence\02-verify-unit.log 2>&1
npm run test:api > ..\evidence\03-test-api.log 2>&1
npm run test:transaction > ..\evidence\04-test-transaction.log 2>&1
npm run test:stack > ..\evidence\05-test-stack.log 2>&1

# 3. Lưu log truy vết X-Request-Id xuyên qua 3 services
docker compose logs --tail=60 gateway orders products > ..\evidence\06-request-id-trace.log
```
