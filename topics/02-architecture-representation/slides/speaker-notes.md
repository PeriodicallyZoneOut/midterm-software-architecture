# Speaker Notes — Chủ đề 2: Architecture Representation (14 Slides Chiến lược)

Tài liệu lời dẫn thuyết trình khớp 1-1 với **14 slides** trong [`outline.md`](outline.md) và hai bản trình chiếu trong [`exports/`](exports/).

---

## Chặng 1: Tư duy Nền tảng cho Người Mới Bắt đầu (Slides 1–2)

### Slide 1: Trang bìa — Architecture Representation: Từ Sơ đồ Đến Thực thi
* "Xin chào thầy và cả lớp. Hôm nay em đại diện nhóm trình bày **Chủ đề 2: Architecture Representation — Biểu diễn và Tái dựng Kiến trúc**."
* "Mục tiêu của bài trình bày này là giúp bất kỳ ai trong lớp — kể cả khi chưa từng đọc code của dự án **Mini Shop** — cũng nắm được bức tranh chiến lược: làm sao đi từ các sơ đồ kiến trúc chuẩn xuống đúng từng dòng lệnh (`file:line`), từng container Docker (**6 containers, 3 mạng, 2 volumes**) và kiểm chứng bằng bằng chứng thực nghiệm."

### Slide 2: Tư duy Chiến lược — View vs. Notation vs. C4 Zoom Level
* "Trước hết, chúng ta cần làm rõ một hiểu lầm rất phổ biến: **Vẽ 4 biểu đồ UML ngẫu nhiên KHÔNG PHẢI là có 4 Views**."
* "Theo chuẩn ISO 42010:
  * **View (Góc nhìn)** là cách nhìn hệ thống để trả lời mối quan tâm (**Concerns**) của một nhóm **Stakeholder** cụ thể (trong bài có **5 nhóm Stakeholders**).
  * **Notation (Ký hiệu)** chỉ là công cụ hình học để vẽ (Boxes & Arrows, Sequence, ER).
  * Trên slide là 2 biểu đồ đối chiếu: Bên trái là **C4 Model** giúp phóng đại cấu trúc tĩnh qua 4 tầng (Context $\rightarrow$ Container $\rightarrow$ Component $\rightarrow$ Code); bên phải là **4+1 View Model của Kruchten** bổ sung góc nhìn hành vi động lúc runtime (Logical, Development, Process, Physical xoay quanh hạt nhân **+1 Scenarios**)."

---

## Chặng 2: Giải phẫu Cấu trúc Tĩnh bằng C4 + 4+1 (Slides 3–5)

### Slide 3: C4 Level 1 (System Context) & Ma trận Stakeholder/Concern
* "Ở cấp phóng đại ngoài cùng — **C4 Level 1 (System Context)**: Hệ thống Mini Shop mở duy nhất một cổng **`127.0.0.1:8080`** phục vụ **2 tác nhân**:
  * **Khách hàng (Customer):** Duyệt danh mục, quản lý giỏ hàng (tối đa **20 mặt hàng**, số lượng mỗi mặt hàng từ **1 đến 99**), đặt hàng và tra cứu đơn.
  * **Quản trị viên (Store Admin):** Thêm/sửa sản phẩm (giá từ **1 đến 1.000.000.000 VND**), bật hoặc ngừng kinh doanh sản phẩm.
* Phía trình duyệt sử dụng `Browser LocalStorage` để lưu giỏ hàng (`mini-cart`) và khóa chống trùng đang chờ (`mini-pending`)."

### Slide 4: 4+1 Logical View & C4 Level 2 (Container Diagram)
* "Khi mở hộp đen hệ thống ra, slide này đặt cạnh nhau 2 biểu đồ:
  * **Biểu đồ 1 (Trái — 4+1 Logical View):** Chia hệ thống thành **2 Bounded Contexts** độc lập là **Catalog Domain (`Products`)** và **Ordering Domain (`Orders`)**, đứng sau tầng biên `API Edge`.
  * **Biểu đồ 2 (Phải — C4 Level 2 Container):** Ánh xạ thành **7 khối thực thi** (`Browser SPA` + **6 Docker Containers**). Khi khách đặt hàng, `orders:3002` gọi trực tiếp `products:3001` qua API nội bộ `POST /internal/products/resolve` (tối đa **20 UUIDs**, timeout **3 giây**), không đi vòng lại qua `gateway:3000`."

### Slide 5: 4+1 Development View & C4 Level 3–4 (Workspaces & Code)
* "Ở góc nhìn của lập trình viên (**Development View & C4 Level 3–4**):
  * **Biểu đồ 1 (Trái):** Repo tổ chức dạng Monorepo gồm **4 NPM Workspaces** (`@mini/frontend`, `@mini/gateway`, `@mini/products`, `@mini/orders`). Điểm thiết kế rất đáng chú ý là **Shared-Nothing Runtime Code**: 3 backend không import chung thư viện nội bộ lúc runtime mà mỗi service tự đóng gói `http.ts` (**31 dòng**) và `db.ts` (**8 dòng**) riêng, được build qua multi-stage `Dockerfile` với tham số `ARG SERVICE` và chạy dưới quyền `USER node`.
  * **Biểu đồ 2 (Phải — C4 Level 3 & 4):** Đi sâu vào bên trong `Orders Service` tới tận hàm `requestHash()` (sắp xếp `items` theo `productId` rồi băm **SHA-256 64 ký tự hex**) và hàm `priceOrder()` tại `services/orders/src/domain.ts:7-11`."

---

## Chặng 3: Hành vi Động & Triển khai Vật lý (Slides 6–9)

### Slide 6: 4+1 Process View (Phần 1) — Đặt hàng & Chuỗi Timeout ($3\text{s} < 8\text{s} < 10\text{s}$)
* "Chuyển sang hành vi động lúc runtime (**Process View**), biểu đồ Sequence 10 bước trên slide thể hiện 2 nguyên lý quan trọng:
  1. **Chuỗi Timeout 3 tầng ($3\text{s} < 8\text{s} < 10\text{s}$):** `Orders` gọi `Products` chỉ chờ **3.000 ms** (`orders/src/index.ts:35`), nhỏ hơn mức **8.000 ms** của `Gateway` (`gateway/src/index.ts:11`) và **10.000 ms** của `Nginx` (`nginx.conf:10`). Nhờ đó, nếu `Products` bị treo, `Orders` chủ động bắt lỗi trước và trả về JSON `503 PRODUCTS_UNAVAILABLE` rõ ràng.
  2. **Không giữ khóa DB khi chờ mạng:** `Orders` gọi HTTP sang `Products` ở bước 5–7 xong xuôi rồi mới lấy kết nối từ pool (**5 connections**) để mở **Local ACID Transaction** ở bước 8–9."

### Slide 7: 4+1 Process View (Phần 2) — Replay, Conflict & Cô lập Lỗi
* "Biểu đồ phân nhánh trên Slide 7 giải thích cách `Orders Service` xử lý các tình huống bất thường:
  * **Nhánh 1 (Retry hợp lệ — `200 OK`):** Khi mạng chập chờn làm khách bấm gửi lại cùng `Idempotency-Key` (**8–100 ký tự**) và cùng giỏ hàng, hàm `replay()` khớp mã băm SHA-256 và trả về ngay đơn hàng cũ (**0 lần** gọi sang `Products`, **0 đơn trùng**).
  * **Nhánh 2 (Khác nội dung — `409 IDEMPOTENCY_CONFLICT`):** Cùng key nhưng khách đã đổi số lượng/mặt hàng $\rightarrow$ chặn ngay.
  * **Nhánh 3 (Products sập — `503` trong $\le 3\text{s}$):** Tạo đơn mới báo lỗi nhanh trong 3 giây, nhưng **luồng đọc đơn hàng cũ (`GET /api/orders*`) vẫn hoạt động 100% (`200 OK`)** vì chỉ đọc từ `orders-db`."

### Slide 8: 4+1 Physical / Deployment View — 6 Containers, 3 Mạng & Healthcheck
* "Ở góc nhìn triển khai vật lý (`compose.yaml`):
  * **Biểu đồ 1 (Trái):** Hệ thống có **3 mạng Docker**. Chỉ `frontend` mở cổng `127.0.0.1:8080` ra máy host. Hai mạng dữ liệu `orders-data` và `products-data` đều đặt cờ `internal: true`. Container `orders` không tham gia mạng `products-data`, nên về mặt mạng vật lý, `orders` không thể kết nối tới `products-db:3306`.
  * **Biểu đồ 2 (Phải):** Chuỗi khởi động **4 bậc** theo `condition: service_healthy`. Bậc dưới phải vượt qua healthcheck (`SELECT 1` và retry kết nối DB tối đa **30 lần x 2 giây**) thì bậc trên mới bắt đầu nhận traffic."

### Slide 9: +1 Scenarios — 5 Kịch bản Kết nối Xuyên suốt 4 Views
* "Bảng ma trận trên Slide 9 chính là góc nhìn **+1 Scenarios**: 5 kịch bản từ duyệt sản phẩm (`S01`), đặt hàng snapshot (`S02`), đổi giá xem lại đơn cũ (`S03`), retry/conflict key (`S04`) đến đánh sập `Products` (`S05`) kết nối toàn bộ 4 góc nhìn trên với đúng `file:line` và file kiểm thử tự động."

---

## Chặng 4: Dữ liệu, Bảo mật, Ánh xạ Code & Thực nghiệm (Slides 10–14)

### Slide 10: Database Schema / Data Model — Database-per-Service, Snapshot & Idempotency
* "Trên Slide 10 là **2 biểu đồ ER tách biệt theo ranh giới Database**:
  * **Biểu đồ ER 1 (`products-db`):** Bảng `products` (**7 cột**, **5 sản phẩm mẫu**).
  * **Biểu đồ ER 2 (`orders-db`):** Bảng `orders` (**8 cột**) và `order_items` (**7 cột**).
  * **3 điểm nhấn cốt lõi:** (1) Không có Foreign Key vật lý xuyên DB (`product_id` chỉ là tham chiếu UUID logic); (2) Đóng băng **Snapshot** `product_name` và `unit_price_vnd` vào `order_items` ngay lúc mua để hóa đơn lịch sử bất biến khi Admin đổi giá; (3) Cột `idempotency_key COLLATE ascii_bin UNIQUE` đi kèm `request_hash CHAR(64)`."

### Slide 11: Security View & Concurrency View (Race Condition)
* "Slide 11 gồm 2 biểu đồ giải quyết bài toán Bảo mật và Đồng thời:
  * **Biểu đồ 1 (Trái — Security Trust Boundaries):** Chỉ rõ **6 kiểm soát ĐÃ CÓ THẬT trong code** (Server-side pricing dùng Zod `.strict()`, Gateway whitelist chặn `/api/internal/*` trả `404`, Prepared SQL, giới hạn JSON **32KB**, `USER node`, mạng DB `internal: true`) và **2 đề xuất mở rộng** (ký hiệu nét đứt: JWT/RBAC cho `/admin` và mTLS nội bộ).
  * **Biểu đồ 2 (Phải — Concurrency Race Condition):** Nếu 2 request `R1` và `R2` trùng `Idempotency-Key` đến vào đúng cùng một mili-giây và cùng lọt qua bước `SELECT` ban đầu: `R1` commit trước giữ khóa `UNIQUE`; `R2` chạm lỗi `ER_DUP_ENTRY` của InnoDB $\rightarrow$ code tại `orders/src/index.ts:48-52` bắt `ER_DUP_ENTRY`, gọi `conn.rollback()` rồi gọi lại `replay(K1, hash)` để trả về đúng đơn hàng `O1` vừa tạo (`200 OK`)."

### Slide 12 & Slide 13: Thẻ Component (1–5) theo Quy cách 10 Mục `INVENTORY.md`
* "Trên Slide 12 và Slide 13 là bảng tổng hợp đầy đủ **10 mục quy chuẩn** theo `docs/INVENTORY.md` (Mục 8) cho toàn bộ 5 thành phần: `Browser SPA`, `Frontend Nginx`, `API Gateway`, `Products Service + products-db` và `Orders Service + orders-db`. Bất kỳ hộp nào xuất hiện trên các sơ đồ trước đều được ánh xạ chi tiết từ Trách nhiệm, Contract, State, Luồng chính, Giao thức, Xử lý lỗi, `file:line`, Container/Port cho tới Bằng chứng Demo và Trade-off."

### Slide 14: Đánh đổi Kiến trúc (Trade-offs) & Kịch bản 5 Bước Live Demo
* "Cuối cùng, Slide 14 tổng kết **5 Quyết định Kiến trúc (ADRs)**: hệ thống chủ động dùng **Local ACID Transaction + Data Snapshot + Sync HTTP** thay vì Saga hay Event Sourcing vì thao tác đặt hàng chỉ ghi vào duy nhất `orders-db`. Ngay sau đây, em xin chuyển sang thực hiện 5 bước Live Demo trực tiếp."
