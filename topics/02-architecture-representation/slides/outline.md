# Dàn ý Bộ Slide Đơn giản & Trực quan — Chủ đề 2: Architecture Representation

* **Phong cách thiết kế:** Tối giản, nhiều khoảng trắng (whitespace), mỗi slide chỉ tập trung vào **3 khối thẻ (Input $\rightarrow$ Xử lý $\rightarrow$ Output)** hoặc **3–4 gạch đầu dòng ngắn gọn**, dễ hiểu ngay cho cả lớp.
* **Tổng số lượng:** **12 slides** ($\le 15$ slides).
* **Quy chuẩn Thiết kế:**
  * **Bảng màu:** Nền xám kem nhạt (`#F7F6F2`), Thẻ trắng (`#FFFFFF`), Thẻ nhấn xám than đậm (`#131B2E`), Chữ đen (`#111318`) và **1 màu nhấn duy nhất Xanh Cyan (`#00A896`)**.
  * **Kiểu chữ:** Tiêu đề slide `Playfair Display` (**36**), Tiêu đề mục/thẻ `Playfair Display` (**26**), Nội dung & bullet `Nunito` (**16–18**).

---

## Chi tiết Từng Slide (12 Slides)

### Slide 1: Trang bìa — Architecture Representation
* **Nội dung:**
  * Chủ đề 2: Biểu diễn và Tái dựng Kiến trúc Phần mềm.
  * Dự án thực nghiệm: **Mini Shop Microservices** (4 Workspaces · 6 Containers · 2 MariaDB).
  * Mục tiêu: Giúp cả lớp nắm được cách biểu diễn kiến trúc từ bức tranh tổng thể xuống tới code và container thực tế.

### Slide 2: Tư duy Cốt lõi — Phân biệt View, Notation & C4 Model
* **Bố cục:** 3 hộp thẻ ngang nối mũi tên (`View` $\rightarrow$ `Notation` $\rightarrow$ `C4 + 4+1`).
* **Nội dung & Biểu đồ:**
  * **Thẻ 1 — View (Góc nhìn):** Trả lời mối quan tâm của 5 nhóm Stakeholders. *4 biểu đồ UML ngẫu nhiên không phải là 4 Views.*
  * **Thẻ 2 — Notation (Ký hiệu):** Công cụ vẽ (Boxes & Arrows, Sequence, ER) kèm chú giải và nhãn giao thức.
  * **Thẻ 3 — C4 + 4+1 Views:** C4 phóng đại cấu trúc tĩnh (4 tầng); 4+1 mô tả hành vi runtime (timeout, transaction).

### Slide 3: Tổng quan Dự án Thực nghiệm — Mini Shop Microservices
* **Bố cục:** Slide bullet thoáng (theo mẫu ảnh 2).
* **Nội dung:**
  * Hệ thống thương mại điện tử chạy trên Docker Compose gồm **6 containers** và **3 mạng cô lập**.
  * Chia làm **3 tầng chính**:
    * **Tầng Giao diện & Cổng vào:** React SPA (`localStorage`) + Nginx (`:8080`) + API Gateway (`:3000`).
    * **Tầng Dịch vụ Nghiệp vụ:** `Products Service (:3001)` và `Orders Service (:3002)` viết bằng Node.js/Express + TypeScript.
    * **Tầng Dữ liệu Độc lập:** 2 container MariaDB 11.8 riêng biệt (`products-db`, `orders-db`).

### Slide 4: C4 Level 1 (System Context) & 4+1 Logical View
* **Bố cục:** 3 hộp thẻ ngang nối mũi tên (`Actors & SPA` $\rightarrow$ `API Gateway` $\rightarrow$ `2 Miền Nghiệp vụ`).
* **Nội dung & Biểu đồ:**
  * **Người dùng & SPA:** Khách hàng (giỏ tối đa **20 món**, SL **1–99**) và Admin giao tiếp qua cổng duy nhất `:8080`.
  * **API Gateway (`:3000`):** Kiểm tra whitelist `/api/products*` và `/api/orders*`, gắn `X-Request-Id`, chặn `/internal/*`, timeout **8s**.
  * **2 Miền Nghiệp vụ:** `Products` (quản lý 5 SP mẫu) và `Orders` (quản lý đơn hàng, gọi nội bộ sang Products với timeout **3s**).

### Slide 5: 4+1 Development View & C4 Level 3–4 (Tổ chức Code)
* **Bố cục:** Slide bullet thoáng (theo mẫu ảnh 2).
* **Nội dung:**
  * Mã nguồn tổ chức dạng Monorepo gồm **4 NPM Workspaces**: `@mini/frontend`, `@mini/gateway`, `@mini/products`, `@mini/orders`.
  * **Nguyên lý Shared-Nothing lúc Runtime:**
    * Các backend không dùng chung thư viện nội bộ lúc chạy (mỗi service tự có `http.ts` 31 dòng và `db.ts` 8 dòng riêng).
    * Đóng gói bằng **Multi-stage Dockerfile** (`ARG SERVICE`), hạ quyền chạy dưới `USER node`.
    * Sửa và build lại `Products` không bao giờ làm hỏng hay bắt buộc khởi động lại `Orders`.

### Slide 6: 4+1 Process View (Phần 1) — Luồng Đặt hàng & Chuỗi Timeout
* **Bố cục:** 3 hộp thẻ ngang nối mũi tên (`Input Đặt hàng` $\rightarrow$ `Xử lý & Timeout` $\rightarrow$ `Output Giao dịch`).
* **Nội dung & Biểu đồ:**
  * **Input (Từ Trình duyệt):** Gửi `POST /api/orders` kèm `Idempotency-Key` (8–100 ký tự) và danh sách `{productId, quantity}`.
  * **Xử lý (Chuỗi Timeout 3s < 8s < 10s):**
    * Nginx chờ Gateway **10s**; Gateway chờ Orders **8s**; Orders gọi Products resolve giá **3s**.
    * Kiểm tra sản phẩm đang bán (`isActive=true`) và tính tổng tiền tại server (`priceOrder`).
  * **Output (Local ACID Transaction):** Ghi nguyên tử vào bảng `orders` và `order_items` trên `orders-db`, trả về `201 Created`.

### Slide 7: 4+1 Process View (Phần 2) — Chống Trùng Đơn & Cô lập Lỗi
* **Bố cục:** 3 hộp thẻ ngang (`Retry Hợp lệ (200)` $\cdot$ `Xung đột Body (409)` $\cdot$ `Products Sập (503)`).
* **Nội dung & Biểu đồ:**
  * **Retry Hợp lệ (`200 OK`):** Gửi lại cùng `Idempotency-Key` và cùng giỏ hàng (khớp mã băm SHA-256) $\rightarrow$ Trả ngay đơn cũ, không tạo đơn thứ 2.
  * **Xung đột Dữ liệu (`409 Conflict`):** Dùng lại key cũ nhưng đổi số lượng/mặt hàng $\rightarrow$ Bị chặn bởi `IDEMPOTENCY_CONFLICT`.
  * **Khi `Products` Sập (`503` vs `200`):** Đặt đơn mới báo lỗi `503` sau **3 giây**; nhưng **xem lại đơn hàng cũ vẫn hoạt động 100% (`200 OK`)**.

### Slide 8: 4+1 Physical / Deployment View — Cô lập Mạng Docker
* **Bố cục:** 3 hộp thẻ ngang tương ứng 3 mạng Docker trong `compose.yaml`.
* **Nội dung & Biểu đồ:**
  * **Mạng 1 — `backend` (Bridge):** Nối `frontend (:8080->80)`, `gateway (:3000)`, `products (:3001)` và `orders (:3002)`.
  * **Mạng 2 — `products-data` (`internal: true`):** Chỉ nối `products` với `products-db (:3306)` và volume `products-data`.
  * **Mạng 3 — `orders-data` (`internal: true`):** Chỉ nối `orders` với `orders-db (:3306)` và volume `orders-data`. Container `orders` không thể kết nối sang `products-db`.

### Slide 9: Database Schema — Database-per-Service & Snapshot Giá
* **Bố cục:** 3 hộp thẻ ngang (`products-db` $\rightarrow$ `Snapshot khi Mua` $\rightarrow$ `orders-db`).
* **Nội dung & Biểu đồ:**
  * **Bảng `products` (7 cột):** Lưu giá niêm yết hiện hành (`price_vnd`) và trạng thái `is_active` của 5 sản phẩm mẫu.
  * **Cơ chế Snapshot (Không FK xuyên DB):** Khi khách đặt hàng, `Orders` sao chép tên (`product_name`) và đơn giá (`unit_price_vnd`) tại thời điểm mua sang `order_items`.
  * **Bảng `orders` & `order_items` (15 cột):** Không dùng Foreign Key sang `products-db`. Khi Admin đổi giá sản phẩm, hóa đơn cũ vẫn giữ nguyên giá lúc mua.

### Slide 10: Security View & Concurrency View (Xử lý Đồng thời)
* **Bố cục:** Slide bullet thoáng (theo mẫu ảnh 2).
* **Nội dung:**
  * **Các cơ chế bảo mật ĐÃ CÓ THẬT trong code:**
    * Không tin giá từ Client (Zod `.strict()` chỉ nhận `productId` và `quantity`, gửi kèm giá bị lỗi `400`).
    * Gateway chặn tuyệt đối `/api/internal/*` từ ngoài (trả `404`); giới hạn JSON **32KB**; dùng Prepared SQL.
  * **Xử lý Race Condition (2 request trùng key đến cùng mili-giây):**
    * Cột `idempotency_key UNIQUE` trong MariaDB chặn request thứ 2 bằng lỗi `ER_DUP_ENTRY` $\rightarrow$ tự động `rollback()` và gọi lại `replay()` trả về đúng đơn hàng đầu tiên.
  * **Giới hạn & Đề xuất mở rộng:** Bổ sung xác thực JWT/RBAC cho trang `/admin/products`.

### Slide 11: Ánh xạ Component (Hộp Sơ đồ $\rightarrow$ Code $\rightarrow$ Container $\rightarrow$ Demo)
* **Bố cục:** 3 hộp thẻ ngang đại diện cho quy cách 10 mục trong `INVENTORY.md`.
* **Nội dung & Biểu đồ:**
  * **Tầng Giao diện & Biên (`SPA` + `Nginx` + `Gateway`):** `main.tsx:10-50`, `nginx.conf:1-20`, `gateway/src/index.ts:1-17` $\rightarrow$ Container `frontend (:8080)` & `gateway (:3000)`.
  * **Tầng Sản phẩm (`Products` + `products-db`):** `products/src/index.ts:1-36`, `db.ts:1-8` (pool **5 conns**, retry **30x2s**) $\rightarrow$ Container `products (:3001)` & `products-db (:3306)`.
  * **Tầng Đơn hàng (`Orders` + `orders-db`):** `orders/src/index.ts:1-57`, `domain.ts:1-11` (`requestHash`, `priceOrder`) $\rightarrow$ Container `orders (:3002)` & `orders-db (:3306)`.

### Slide 12: Đánh đổi Kiến trúc (Trade-offs) & 5 Bước Live Demo
* **Bố cục:** 3 hộp thẻ ngang (`Đánh đổi Kiến trúc` $\rightarrow$ `Vì sao không dùng Saga?` $\rightarrow$ `5 Bước Live Demo`).
* **Nội dung:**
  * **Đánh đổi (Trade-offs):** Chấp nhận lặp lại tên/giá trong `order_items` và chạy 2 MariaDB để đổi lấy tính độc lập schema và đọc đơn hàng tự chủ 100%.
  * **Không gọi nhầm là Saga / Event Sourcing:** Vì thao tác đặt hàng chỉ ghi vào duy nhất `orders-db`, một **Local ACID Transaction** là đủ và đơn giản nhất.
  * **5 Bước Live Demo:** (1) Xem log `X-Request-Id` ở 3 services; (2) Đổi giá Admin kiểm chứng Snapshot; (3) Test `curl` Idempotency `201 -> 200 -> 409`; (4) `stop products` kiểm chứng cô lập lỗi; (5) Deploy độc lập `products`.
