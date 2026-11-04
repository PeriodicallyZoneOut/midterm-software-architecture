# Runbook Demo — Mini Shop (Chủ đề 2: Architecture Representation)

Tài liệu hướng dẫn từng bước khởi chạy, thực hiện kịch bản live demo khi vấn đáp, thu thập bằng chứng (evidence) và khôi phục hệ thống.

---

## 1. Môi trường, Thư mục làm việc & Cổng (Prerequisites)

* **Thư mục làm việc (Working Directory):**
  ```powershell
  cd e:\KTPM\midterm-software-architecture\topics\02-architecture-representation\projects\mini-shop\source
  ```
* **Yêu cầu công cụ:**
  * Docker Desktop đang chạy (Docker Engine v24+ & Docker Compose v2).
  * Node.js 24+ (nếu chạy các script test tự động trên máy host).
* **Cấu hình `.env` (tạo từ `.env.example` nếu chưa có):**
  ```powershell
  if (!(Test-Path .env)) { Copy-Item .env.example .env }
  ```
  * Nội dung mặc định trong `.env`:
    * `PRODUCTS_DB_PASSWORD=local-products-demo`
    * `ORDERS_DB_PASSWORD=local-orders-demo`
    * `PRODUCTS_ROOT_PASSWORD=local-products-root`
    * `ORDERS_ROOT_PASSWORD=local-orders-root`
    * `WEB_PORT=8080` *(Nếu cổng 8080 đang bận bởi ứng dụng khác, đổi thành `WEB_PORT=18080`)*
* **Bảng Cổng & Mạng (Ports & Networks):**
  * **Host Port duy nhất:** `http://127.0.0.1:8080` (Container `frontend` Nginx).
  * **Internal Ports (trong mạng Docker `backend`):** `gateway:3000`, `products:3001`, `orders:3002`.
  * **Internal DB Ports:** `products-db:3306` (mạng `products-data`), `orders-db:3306` (mạng `orders-data`).

---

## 2. Khởi động & Kiểm tra Sẵn sàng (Build, Start & Readiness)

```powershell
# 1. Build và khởi chạy toàn bộ 6 containers, chờ đến khi tất cả healthy
docker compose up --build -d --wait

# 2. Kiểm tra trạng thái 6 containers (Tất cả phải hiện "Up ... (healthy)")
docker compose ps

# 3. Kiểm tra nhanh API qua cổng 8080
curl.exe -s http://127.0.0.1:8080/api/products
```

**Kết quả kỳ vọng:** `docker compose ps` hiển thị 6 container (`frontend`, `gateway`, `products`, `orders`, `products-db`, `orders-db`) đều `(healthy)`; lệnh `curl` trả về JSON danh sách 5 sản phẩm mẫu.

---

## 3. Kịch bản Live Demo Khi Vấn đáp (5–7 phút)

### Bước 1: Chứng minh Luồng Đặt hàng Chuẩn & Truy vết `X-Request-Id` (Logical + Process View)
1. Mở trình duyệt tại **[http://localhost:8080](http://localhost:8080)**.
2. Thêm 1–2 sản phẩm vào giỏ hàng $\rightarrow$ Vào **Giỏ hàng** $\rightarrow$ Nhập Họ tên, Email $\rightarrow$ Nhấn **"Xác nhận đặt hàng"**.
3. Quan sát màn hình chuyển sang trang **Chi tiết đơn hàng (`/orders/:id`)**.
4. Mở terminal chạy lệnh xem log:
   ```powershell
   docker compose logs --tail=30 gateway orders products
   ```
5. **Điểm chỉ cho giảng viên:**
   * Cùng một mã `requestId` xuất hiện ở cả 3 service: `gateway` (`POST /api/orders`), `orders` (`POST /orders`), và `products` (`POST /internal/products/resolve`).
   * Đối chiếu code: `services/gateway/src/http.ts:8-12` và `services/orders/src/index.ts:35`.

---

### Bước 2: Chứng minh Database-per-Service & Price Snapshot (Data Model View)
1. Ghi nhớ đơn giá sản phẩm trong đơn hàng vừa tạo ở Bước 1 (ví dụ: *Sổ tay Everyday* giá `89.000 ₫`).
2. Trên giao diện web, mở mục **Quản lý (`/admin/products`)** $\rightarrow$ Nhấn **Sửa** sản phẩm *Sổ tay Everyday* $\rightarrow$ Đổi giá thành `199.000 ₫` $\rightarrow$ Nhấn **Lưu sản phẩm**.
3. Mở lại mục **Đơn hàng (`/orders`)** $\rightarrow$ Bấm vào đơn hàng đã tạo ở Bước 1.
4. **Kết quả quan sát & Giải thích kiến trúc:**
   * Trang **Sản phẩm** hiển thị giá mới `199.000 ₫` (đọc từ `products-db`).
   * Trang **Chi tiết đơn hàng cũ** vẫn giữ nguyên giá `89.000 ₫` (đọc từ cột snapshot `unit_price_vnd` trong bảng `order_items` của `orders-db`).
   * Đối chiếu code: `services/orders/src/domain.ts:8-11` (`priceOrder`) và `services/orders/src/index.ts:46`.

---

### Bước 3: Chứng minh Idempotency Key & Phát hiện Xung đột Payload (Process + Concurrency View)
Chạy trực tiếp trên PowerShell để giảng viên thấy rõ HTTP Status và Response:

```powershell
# Đặt 1 Idempotency-Key cố định cho ca thử nghiệm
$KEY = "demo-idemp-key-20261103"
$BODY1 = '{"customerName":"The Anh","customerEmail":"theanh@example.com","items":[{"productId":"10000000-0000-4000-8000-000000000001","quantity":1}]}'
$BODY2 = '{"customerName":"The Anh","customerEmail":"theanh@example.com","items":[{"productId":"10000000-0000-4000-8000-000000000001","quantity":5}]}'

# Lần 1: Tạo đơn mới -> Kỳ vọng HTTP 201 Created
curl.exe -i -X POST http://127.0.0.1:8080/api/orders -H "Content-Type: application/json" -H "Idempotency-Key: $KEY" -d $BODY1

# Lần 2: Gửi lại Y HỆT Key và Body (Retry) -> Kỳ vọng HTTP 200 OK và trả về CÙNG Order ID
curl.exe -i -X POST http://127.0.0.1:8080/api/orders -H "Content-Type: application/json" -H "Idempotency-Key: $KEY" -d $BODY1

# Lần 3: Dùng lại CÙNG Key nhưng đổi quantity thành 5 -> Kỳ vọng HTTP 409 Conflict (IDEMPOTENCY_CONFLICT)
curl.exe -i -X POST http://127.0.0.1:8080/api/orders -H "Content-Type: application/json" -H "Idempotency-Key: $KEY" -d $BODY2
```
* **Điểm chỉ cho giảng viên:** Hàm `requestHash()` (`services/orders/src/domain.ts:7`) và `replay()` (`services/orders/src/index.ts:17-22`).

---

### Bước 4: Chứng minh Cô lập Lỗi (Fault Isolation) & Timeout 3 Giây Khi `Products` Sập
1. Dừng container `products`:
   ```powershell
   docker compose stop products
   ```
2. **Kiểm tra 1 — Đọc đơn hàng cũ vẫn sống bình thường:**
   * Trên trình duyệt, vào mục **Đơn hàng** và bấm xem chi tiết đơn $\rightarrow$ **Hoạt động 100% (`200 OK`)** vì `orders` chỉ đọc `orders-db`.
3. **Kiểm tra 2 — Đặt đơn hàng mới báo lỗi có kiểm soát:**
   * Thử đặt một đơn hàng mới $\rightarrow$ Nhận thông báo lỗi `503 PRODUCTS_UNAVAILABLE` (*"Dịch vụ sản phẩm chưa sẵn sàng. Vui lòng thử lại."*) mà không làm sập `orders` hay treo trình duyệt.
4. **Khôi phục `products`:**
   ```powershell
   docker compose start products
   docker compose ps
   ```
   * Sau khi `products` healthy trở lại, bấm **"Xác nhận đặt hàng"** lần nữa trên trình duyệt $\rightarrow$ Đơn hàng được tạo thành công với cùng `Idempotency-Key` đang lưu trong `localStorage(mini-pending)`.

---

### Bước 5: Chứng minh Triển khai Độc lập (Independent Deployment) & Bảo vệ Endpoint Nội bộ
```powershell
# 1. Thử gọi trực tiếp API nội bộ từ bên ngoài qua Gateway -> Kỳ vọng bị chặn 404 NOT_FOUND
curl.exe -i -X POST http://127.0.0.1:8080/api/internal/products/resolve -H "Content-Type: application/json" -d '{"ids":["10000000-0000-4000-8000-000000000001"]}'

# 2. Build và redeploy riêng container products mà không làm restart orders
docker compose up -d --build --no-deps --wait products
docker compose ps
```

---

## 4. Chạy Bộ Kiểm thử Tự động & Thu thập Evidence

```powershell
# Cài đặt dependencies trên host (chỉ cần chạy 1 lần)
npm ci

# 1. Build TypeScript cả 4 workspaces + chạy Unit Tests (domain logic, hash, pricing)
npm run verify

# 2. Chạy Integration API Tests qua Nginx -> Gateway -> Services -> MariaDB
npm run test:api

# 3. Kiểm chứng Transaction Rollback khi lỗi ở dòng order_items thứ 2
npm run test:transaction

# 4. Kiểm chứng vòng đời Docker Stack (stop/start/persistence/independent deploy)
npm run test:stack
```

---

## 5. Dừng Hệ thống An toàn (Giữ nguyên Dữ liệu Volume)

```powershell
# Dừng các container nhưng GIỮ NGUYÊN dữ liệu trong 2 volumes products-data và orders-data
docker compose down
```
> **Lưu ý:** Tuyệt đối **không** dùng cờ `-v` (`docker compose down -v`) nếu muốn giữ lại các đơn hàng và sản phẩm đã tạo trong buổi demo.
