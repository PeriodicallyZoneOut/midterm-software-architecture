# 04 — Kiểm chứng, Quyết định Kiến trúc (ADRs) & Bộ Câu hỏi Vấn đáp (Mini Shop)

Tài liệu này tổng hợp:
1. Bảng ma trận kiểm chứng các giả thuyết kiến trúc (Verification Matrix).
2. Các quyết định kiến trúc cốt lõi và đánh đổi (Architecture Decision Records & Trade-offs).
3. Bộ **10 câu hỏi và câu trả lời vấn đáp** bám sát mã nguồn và bằng chứng runtime.

---

## 1. Bảng Kiểm chứng Thuộc tính Kiến trúc (Verification Matrix)

| # | Giả thuyết / Thuộc tính Kiến trúc | Cách kiểm tra (Lệnh / Thao tác) | Kết quả Kỳ vọng (Expected) | Kết quả Thực tế từ Code & Test (Actual) | Vị trí Bằng chứng (Evidence) | Giới hạn (Limitations) |
|---|---|---|---|---|---|---|
| **V1** | **Database-per-Service & Price Snapshot:** Đổi giá sản phẩm không làm thay đổi lịch sử đơn hàng đã đặt | 1. Đặt đơn hàng với SP giá `89.000 ₫`.<br/>2. Gọi `PATCH /api/products/:id` đổi giá lên `150.000 ₫`.<br/>3. Gọi `GET /api/orders/:id`. | Đơn hàng cũ vẫn hiển thị `unitPriceVnd: 89000`; catalog hiển thị giá mới `150000`. | `order_items` lưu cứng `product_name` và `unit_price_vnd` lúc tạo đơn; không JOIN bảng `products`. | • `services/orders/src/index.ts:46`<br/>• `tests/api.test.ts`<br/>• `docs/api-verification.log` | Tăng dung lượng lưu trữ do lặp lại tên và đơn giá sản phẩm trong từng dòng `order_items`. |
| **V2** | **Idempotency & Conflict Detection:** Retry cùng `Idempotency-Key` không tạo đơn trùng; dùng lại key cho giỏ hàng khác bị chặn | 1. Gửi 2 lần `POST /api/orders` cùng `Idempotency-Key` và cùng body.<br/>2. Gửi lần 3 cùng `Idempotency-Key` nhưng đổi `quantity`. | Lần 1: `201 Created`.<br/>Lần 2: `200 OK` (cùng `order.id`).<br/>Lần 3: `409 IDEMPOTENCY_CONFLICT`. | Hàm `replay(key, hash)` đối chiếu SHA-256 `request_hash`; DB có `UNIQUE(idempotency_key)`. | • `services/orders/src/index.ts:17-22, 32-33`<br/>• `services/orders/src/domain.ts:7`<br/>• `tests/unit.test.ts`, `tests/api.test.ts` | Khóa `idempotency_key` hiện lưu vĩnh viễn trong bảng `orders`, chưa có cơ chế TTL dọn dẹp theo thời gian. |
| **V3** | **Local Transaction Atomicity:** Lỗi khi ghi dòng mặt hàng thứ 2 phải rollback toàn bộ đơn hàng | Chạy `npm run test:transaction` (`scripts/verify-transaction.mjs`) | Không có bản ghi mồ côi nào trong bảng `orders` hay `order_items`. | Khối `catch` gọi `await conn.rollback()` hủy toàn bộ giao dịch trên `orders-db`. | • `services/orders/src/index.ts:43-51`<br/>• `scripts/verify-transaction.mjs`<br/>• `docs/transaction-verification.log` | Chỉ đảm bảo ACID trong phạm vi `orders-db` (không có distributed transaction 2PC sang DB khác). |
| **V4** | **Fault Isolation (Cô lập lỗi):** Khi `products` sập, khách vẫn xem được đơn hàng cũ; tạo đơn mới báo lỗi nhanh trong $\le 3\text{s}$ | Chạy `docker compose stop products` rồi gọi `GET /api/orders` và `POST /api/orders`. | `GET /api/orders` trả `200 OK`.<br/>`POST /api/orders` trả `503 PRODUCTS_UNAVAILABLE` trong $\le 3\text{s}$. | `GET /orders` chỉ đọc `orders-db`; `POST /orders` dùng `AbortSignal.timeout(3000)` khi gọi `products`. | • `services/orders/src/index.ts:25-38`<br/>• `scripts/verify-stack.mjs`<br/>• `docs/stack-verification.log` | Trong thời gian `products` dừng, khách hàng không thể tạo đơn hàng mới (do gọi HTTP đồng bộ). |
| **V5** | **Independent Deployment (Triển khai độc lập):** Build và deploy lại `products` không làm gián đoạn hay restart `orders` | Chạy `docker compose up -d --build --no-deps --wait products` | Container `products` được recreate; `orders` giữ nguyên uptime và PID. | Mỗi service có container riêng và không chia sẻ process hay DB. | • `compose.yaml:48-76`<br/>• `scripts/verify-stack.mjs` | Nếu thay đổi breaking contract của `/internal/products/resolve`, vẫn cần phối hợp phiên bản giữa 2 service. |
| **V6** | **API Boundary Protection:** Chặn truy cập trực tiếp `/internal/*` từ phía client ngoài | Gọi `POST http://localhost:8080/api/internal/products/resolve` | Trả về `404 NOT_FOUND` từ API Gateway. | Regex whitelist của Gateway chỉ cho phép `/^\/api\/(products\|orders)(?:\/[a-fA-F0-9-]+)?$/`. | • `services/gateway/src/index.ts:5-6`<br/>• `tests/api.test.ts` | Các container cùng nằm trong mạng `backend` vẫn có thể gọi trực tiếp nhau (chưa có mTLS nội bộ). |

---

## 2. Ghi nhận Quyết định Kiến trúc & Đánh đổi (Architecture Decisions & Trade-offs)

| Quyết định Kiến trúc (ADR) | Lý do lựa chọn (Why) | Giải pháp thay thế (Alternatives) | Thuộc tính chất lượng (QA) đạt được | Chi phí / Đánh đổi (Trade-offs) |
|---|---|---|---|---|
| **ADR-01: Database-per-Service (2 MariaDB tách biệt trên 2 mạng internal)** | Đảm bảo ranh giới sở hữu dữ liệu tuyệt đối giữa `Products` và `Orders`; tránh coupling ở tầng schema SQL. | Shared Database (1 MariaDB chung cho cả 2 service) hoặc Monolith. | **Modifiability**, **Fault Isolation**, **Deployability**. | Không thể JOIN SQL hoặc dùng Foreign Key giữa `order_items` và `products`; tốn RAM chạy 2 instance MariaDB. |
| **ADR-02: Giao tiếp HTTP Đồng bộ (`POST /internal/products/resolve`) thay vì Event Broker / Saga** | Luồng đặt hàng chỉ ghi vào duy nhất `orders-db` (không trừ kho bên `products-db`), nên không cần giao dịch phân tán nhiều bước (Saga). | Event-Driven Architecture (RabbitMQ/Kafka) nhân bản bảng `products` sang `orders-db`. | **Simplicity**, **Consistency** (luôn lấy đúng giá và trạng thái `isActive` mới nhất ngay lúc đặt). | **Availability coupling khi ghi:** Nếu `Products Service` đang down, `POST /orders` sẽ trả lỗi `503` (tuy nhiên `GET /orders` vẫn hoạt động 100%). |
| **ADR-03: Lưu Snapshot (`product_name`, `unit_price_vnd`) trong bảng `order_items`** | Bảo toàn tính đúng đắn lịch sử hóa đơn khi Admin thay đổi tên/giá sản phẩm và giúp đọc đơn hàng không cần gọi sang `Products`. | Chỉ lưu `product_id` và gọi sang `Products` mỗi khi hiển thị đơn hàng, hoặc lưu bảng lịch sử giá theo thời gian (`product_price_history`). | **Data Integrity**, **Read Performance**, **Availability** cho luồng xem đơn. | Dư thừa dữ liệu có chủ đích (denormalization) trong bảng `order_items`. |
| **ADR-04: Idempotency Key kết hợp SHA-256 Canonical Payload Hash** | Chống tạo đơn trùng khi mạng chập chờn hoặc client retry, đồng thời phát hiện lỗi client dùng lại cùng một key cho nội dung giỏ hàng khác. | Không dùng Idempotency Key (dễ trùng đơn) hoặc chỉ kiểm tra key mà không kiểm tra hash (dễ âm thầm bỏ qua thay đổi giỏ hàng). | **Reliability**, **Correctness**, **Concurrency Safety** (nhờ `UNIQUE` index + bắt `ER_DUP_ENTRY`). | Phía client phải sinh và quản lý vòng đời `Idempotency-Key`; server tốn thêm 1 bước băm SHA-256 và kiểm tra DB. |
| **ADR-05: Chuỗi Timeout phân tầng ($3\text{s} < 8\text{s} < 10\text{s}$)** | Để dịch vụ bên trong (`Orders` gọi `Products` 3s) chủ động bắt lỗi và trả thông điệp JSON rõ ràng trước khi Gateway (8s) hoặc Nginx (10s) cắt kết nối. | Để timeout mặc định (thường 30s–60s hoặc vô hạn) hoặc đặt timeout bằng nhau ở mọi tầng. | **Responsiveness**, **Resilience** (tránh treo cạn kiệt connection pool). | Nếu DB/mạng bị khựng tạm thời quá 3 giây, request tạo đơn sẽ bị hủy sớm và yêu cầu người dùng bấm thử lại. |

---

## 3. Bộ 10 Câu hỏi & Trả lời Vấn đáp Chuyên sâu (Kèm Trích dẫn Code)

### Câu 1: Sự khác biệt giữa 4+1 View Model và C4 Model là gì? Tại sao trong bài lại dùng cả hai?
* **Trả lời:**
  * **C4 Model** phân rã kiến trúc theo **4 cấp độ phóng đại cấu trúc tĩnh (Zoom Levels)**: System Context (L1) $\rightarrow$ Container (L2) $\rightarrow$ Component (L3) $\rightarrow$ Code (L4). Nó giúp người xem đi từ bức tranh tổng thể xuống từng file code rất trực quan.
  * **4+1 View Model** phân tách kiến trúc theo **các mối quan tâm (Concerns) của các Stakeholders khác nhau**: Logical View (chức năng/domain), Development View (tổ chức package/build), Process View (luồng chạy, đồng thời, timeout, transaction), Physical/Deployment View (container, network, volume) và dùng **+1 Scenarios** để kiểm chứng sự liên kết giữa 4 views.
  * Kết hợp cả hai giúp vừa có độ phóng đại cấu trúc rõ ràng (C4), vừa không bỏ sót hành vi động lúc runtime như timeout $3\text{s}/8\text{s}/10\text{s}$, transaction rollback và race condition (Process View trong 4+1).

### Câu 2: Hãy chỉ rõ trên code cách một hộp trên sơ đồ (ví dụ `Orders Service`) ánh xạ tới source code và container đang chạy?
* **Trả lời:**
  * Trên sơ đồ Container/Logical: Hộp `Orders Service (:3002)`.
  * Trong `compose.yaml:62-76`: Dịch vụ `orders` được build từ `Dockerfile` gốc với `args: {SERVICE: orders}`, chạy cổng nội bộ `3002`, nối vào 2 mạng `backend` và `orders-data`.
  * Trong mã nguồn `services/orders/src/`:
    * `index.ts:24-54`: Khai báo các HTTP handlers `GET /health/ready`, `GET /orders`, `GET /orders/:id`, `POST /orders`.
    * `domain.ts:3-11`: Chứa Zod schema `orderInput`, `keyInput`, hàm băm `requestHash()` và hàm tính tiền `priceOrder()`.
    * `db.ts:1-8`: Khởi tạo MySQL connection pool (`connectionLimit: 5`) kết nối tới `orders-db:3306`.

### Câu 3: Tại sao giữa bảng `order_items` và bảng `products` không có khóa ngoại (Foreign Key)? Nếu xóa hoặc sửa sản phẩm thì đơn hàng cũ có bị ảnh hưởng không?
* **Trả lời:**
  * Hệ thống áp dụng mẫu **Database-per-Service**: bảng `products` nằm trong container `products-db` (mạng `products-data`), còn bảng `order_items` nằm trong container `orders-db` (mạng `orders-data`). Hai database chạy trên hai MySQL server tách biệt nên không thể và không được phép tạo Foreign Key vật lý xuyên service.
  * Cột `order_items.product_id` (`services/orders/src/index.ts:9`) chỉ là tham chiếu logic (UUID).
  * Khi tạo đơn, `Orders Service` đã lưu **Snapshot** tên (`product_name`) và đơn giá (`unit_price_vnd`) vào `order_items`. Ngoài ra, `Products Service` không cung cấp API xóa cứng (`DELETE`), mà chỉ cho phép cập nhật hoặc chuyển `is_active = false` (`PATCH /products/:id`). Do đó, đơn hàng cũ luôn giữ nguyên vẹn tên và giá tại thời điểm mua.

### Câu 4: Tại sao `Orders Service` không tin tưởng giá sản phẩm do Frontend gửi lên mà phải gọi `/internal/products/resolve`?
* **Trả lời:**
  * Trình duyệt (Client) thuộc vùng không tin cậy (Untrusted Zone): người dùng có thể sửa `localStorage` (`mini-cart`) hoặc dùng công cụ như `curl`/Postman gửi giá `1 VND`.
  * Vì vậy, tại `services/orders/src/domain.ts:3`, schema `orderInput` sử dụng `.strict()` chỉ chấp nhận `{productId, quantity}`. Nếu client gửi thêm trường `priceVnd`, Zod lập tức trả lỗi `400 VALIDATION_ERROR`.
  * `Orders Service` bắt buộc gọi nội bộ `POST http://products:3001/internal/products/resolve` (`services/orders/src/index.ts:35`) để lấy giá niêm yết chính thức từ `products-db` và tính tổng tiền bằng hàm `priceOrder()` ở phía server.

### Câu 5: Cơ chế `Idempotency-Key` hoạt động như thế nào từ Frontend xuống tới Database? Tại sao cần thêm cột `request_hash`?
* **Trả lời:**
  * **Ở Frontend (`frontend/src/main.tsx:38-40`):** Khi bấm đặt hàng, SPA lưu `{body, key}` vào `localStorage.getItem('mini-pending')`. Nếu request bị lỗi mạng và người dùng bấm thử lại mà giỏ hàng không đổi (`pending?.body === body`), SPA gửi lại đúng `Idempotency-Key` cũ.
  * **Ở Backend (`services/orders/src/index.ts:17-22, 32-33`):** `Orders Service` tính mã băm SHA-256 của payload đã chuẩn hóa thứ tự items (`requestHash(input)` tại `domain.ts:7`).
  * **Vai trò của `request_hash`:** Nếu client gửi lại cùng một `Idempotency-Key` với cùng nội dung (`request_hash === hash`), server trả về `200 OK` kèm đơn hàng cũ. Nhưng nếu client vô tình (hoặc cố tình) dùng lại `Idempotency-Key` cũ cho một giỏ hàng đã bị thay đổi số lượng/sản phẩm (`request_hash !== hash`), server phát hiện ngay và trả về `409 IDEMPOTENCY_CONFLICT` thay vì trả nhầm đơn hàng cũ.

### Câu 6: Điều gì xảy ra nếu 2 request có cùng `Idempotency-Key` đến `Orders Service` vào đúng cùng một mili-giây (Race Condition)?
* **Trả lời:**
  * Giả sử cả 2 request đều chạy qua hàm `replay(key, hash)` (`SELECT id FROM orders WHERE idempotency_key=?`) khi đơn chưa kịp tạo và cùng nhận kết quả `null`.
  * Cả 2 cùng gọi `Products` và mở transaction thực hiện `INSERT INTO orders`.
  * Tại `orders-db`, cột `idempotency_key` có ràng buộc `UNIQUE` (`services/orders/src/index.ts:8`). InnoDB chỉ cho phép 1 transaction commit thành công; transaction thứ 2 sẽ bị ném lỗi `ER_DUP_ENTRY`.
  * Tại `services/orders/src/index.ts:48-52`, khối `catch` bắt đúng `err.code === 'ER_DUP_ENTRY'`, gọi `conn.rollback()`, đặt cờ `duplicate = true`, sau đó gọi lại `await replay(key, hash)` để đọc đơn hàng vừa được request thứ nhất commit và trả về cho client. Không bao giờ có 2 đơn trùng được tạo ra.

### Câu 7: Tại sao hệ thống thiết lập 3 mức timeout khác nhau: 3 giây, 8 giây và 10 giây?
* **Trả lời:**
  * `Orders` $\rightarrow$ `Products`: `3000ms` (`services/orders/src/index.ts:35`).
  * `Gateway` $\rightarrow$ `Orders`/`Products`: `8000ms` (`services/gateway/src/index.ts:11`).
  * `Nginx` $\rightarrow$ `Gateway`: `10s` (`frontend/nginx.conf:10`).
  * Đây là nguyên tắc **Timeout Cascading (Timeout lồng nhau tăng dần từ trong ra ngoài)**: dịch vụ gọi sâu nhất phải timeout sớm nhất để kịp bắt lỗi, giải phóng tài nguyên và trả về mã lỗi nghiệp vụ cụ thể (`503 PRODUCTS_UNAVAILABLE`) cho tầng ngoài, tránh việc tầng ngoài cắt kết nối trước làm mất thông tin ngữ cảnh lỗi.

### Câu 8: Hệ thống này có sử dụng mẫu Saga hay Event Sourcing không? Tại sao?
* **Trả lời:**
  * **Không.** Trong phạm vi nghiệp vụ hiện tại của Mini Shop, thao tác tạo đơn hàng chỉ thay đổi dữ liệu trên **một database duy nhất** là `orders-db` (chỉ đọc giá từ `Products`, không trừ tồn kho bên `products-db`).
  * Do chỉ ghi vào 1 DB, một **Local ACID Transaction** (`beginTransaction` $\rightarrow$ `INSERT orders` $\rightarrow$ `INSERT order_items` $\rightarrow$ `commit`) là đủ đảm bảo tính nguyên tử 100% mà không cần phức tạp hóa bằng Saga hay Message Broker.
  * Việc lưu `unit_price_vnd` trong `order_items` là kỹ thuật **Data Snapshot**, không phải Event Sourcing (vì trạng thái được lưu trực tiếp bằng các dòng hiện hành, không dựng lại bằng cách fold chuỗi sự kiện).

### Câu 9: Làm thế nào để ngăn người dùng bên ngoài gọi trực tiếp vào API nội bộ `/internal/products/resolve` hoặc truy cập thẳng vào Database?
* **Trả lời:**
  * **Ở tầng Container & Network (`compose.yaml`):** Chỉ duy nhất container `frontend` (Nginx) publish port `127.0.0.1:8080:80` ra máy host. Các container `gateway`, `products`, `orders`, `products-db`, `orders-db` không mở bất kỳ port nào ra host. Hai mạng DB (`products-data`, `orders-data`) được cấu hình `internal: true`.
  * **Ở tầng API Gateway (`services/gateway/src/index.ts:5`):** Gateway kiểm tra whitelist bằng biểu thức chính quy `/^\/api\/(products|orders)(?:\/[a-fA-F0-9-]+)?$/`. Do đó, mọi request tới `/api/internal/products/resolve` đều không khớp regex và bị hàm `finishApp()` trả về `404 NOT_FOUND`.

### Câu 10: Nếu số lượng đơn hàng và sản phẩm tăng lên gấp 100 lần, những điểm nghẽn (bottlenecks) nào trong kiến trúc hiện tại sẽ lộ ra và hướng nâng cấp là gì?
* **Trả lời:**
  1. **API `GET /products` chưa có phân trang (`services/products/src/index.ts:19`):** Hiện đang `SELECT * FROM products` và lọc tìm kiếm trên trình duyệt. Khi có hàng chục nghìn sản phẩm, cần bổ sung phân trang (`LIMIT/OFFSET` hoặc cursor) và tìm kiếm ở tầng SQL/Full-text index.
  2. **Cuộc gọi đồng bộ `Orders` $\rightarrow$ `Products` lúc Checkout:** Mỗi đơn mới đều gọi HTTP sang `Products`. Có thể giảm tải bằng cách cache ngắn hạn thông tin sản phẩm hoặc nhân bản bất đồng bộ (Async Replication qua Event) danh mục sản phẩm sang `Orders` nếu cần chịu tải cao và tách sự phụ thuộc runtime.
  3. **Bảng `orders` giữ `idempotency_key` vô thời hạn:** Cần có cơ chế TTL hoặc bảng lưu khóa idempotency riêng có chính sách dọn dẹp định kỳ.
