# 02 — Component Mapping & Quy cách Thẻ Component đưa vào Slide (Mini Shop)

Tài liệu này cung cấp:
1. **Bảng ánh xạ tổng thể (Master Component Mapping)**: Đi trực tiếp từ từng **"Hộp" trên sơ đồ** $\rightarrow$ **Biểu tượng mã nguồn (`file:line`, handler, model)** $\rightarrow$ **Runtime container, network, port** $\rightarrow$ **Kịch bản demo & bằng chứng kiểm chứng**.
2. **Quy cách chuẩn cho mỗi Component đưa vào Slide** (theo đúng mục 8 trong [`docs/INVENTORY.md`](../../../../docs/INVENTORY.md#L148-L153)) kèm **Thẻ Component (Component Cards)** đầy đủ 10 mục cho toàn bộ các thành phần của Mini Shop.

---

## PHẦN 1: BẢNG ÁNH XẠ TỔNG THỂ (DIAGRAM BOX $\rightarrow$ CODE SYMBOL $\rightarrow$ RUNTIME $\rightarrow$ DEMO EVIDENCE)

> *Mọi đường dẫn file mã nguồn dưới đây tính từ thư mục `topics/02-architecture-representation/projects/mini-shop/source/`.*

| # | Hộp trên sơ đồ (Diagram Box) | Trách nhiệm cốt lõi | Biểu tượng mã nguồn (`file:line`, Handler, Model) | Runtime Container, Network & Port | State sở hữu | Kịch bản Demo & Bằng chứng kiểm chứng |
|---|---|---|---|---|---|---|
| **1** | **Browser SPA** *(Client UI)* | Render Catalog, Giỏ hàng, Đơn hàng, Admin; giữ giỏ hàng & `Idempotency-Key` chờ; lọc tìm kiếm client-side | • `frontend/src/main.tsx:10-13` (`api<T>()`)<br/>• `main.tsx:14` (`savedCart()`)<br/>• `main.tsx:18-26` (`App`, `add()`)<br/>• `main.tsx:27-35` (`Catalog`)<br/>• `main.tsx:36-43` (`Cart`, `submit()`)<br/>• `main.tsx:45-46` (`Orders`, `Detail`)<br/>• `main.tsx:47-50` (`Admin`, `save()`) | • Chạy trong trình duyệt người dùng<br/>• Tải từ `http://127.0.0.1:8080`<br/>• Gọi cùng origin `/api/*` | `localStorage`:<br/>• `mini-cart`<br/>• `mini-pending` (`{body, key}`)<br/>• `mini-name`, `mini-email` | • Mở `http://localhost:8080`, thêm giỏ hàng, F5 trình duyệt giỏ vẫn còn.<br/>• `tests/browser.spec.ts` |
| **2** | **Frontend Web / Reverse Proxy** *(Nginx)* | Phục vụ bundle tĩnh SPA (`dist/`); fallback `/index.html`; proxy `/api/` sang `gateway:3000`; chuẩn hóa lỗi 502/504 thành JSON 503 | • `frontend/nginx.conf:1-20`<br/>• `nginx.conf:7-13` (`location /api/`, `proxy_read_timeout 10s`)<br/>• `nginx.conf:14-18` (`location = /upstream-unavailable`)<br/>• `frontend/Dockerfile:1-13` | • Container: `frontend` (`nginx:alpine`)<br/>• Port: Host `127.0.0.1:8080` $\rightarrow$ Container `:80`<br/>• Network: `backend` | Stateless (chỉ phục vụ static files trong `/usr/share/nginx/html`) | • `curl -i http://localhost:8080/api/products`<br/>• Stop `gateway` $\rightarrow$ Nginx trả JSON 503 `SERVICE_UNAVAILABLE`. |
| **3** | **API Gateway** *(Edge Service)* | Điểm vào API duy nhất; whitelist route `/api/(products\|orders)`; gắn/chuyển tiếp `X-Request-Id` và `Idempotency-Key`; chặn `/internal/*`; áp timeout 8s | • `services/gateway/src/index.ts:3` (`GET /health/ready`)<br/>• `services/gateway/src/index.ts:4-14` (Whitelist regex & `fetch` proxy `AbortSignal.timeout(8000)`)<br/>• `services/gateway/src/http.ts:5-31` (`makeApp`, `finishApp`, `HttpError`) | • Container: `gateway` (`node:24-alpine`)<br/>• Internal Port: `3000` (không mở ra host)<br/>• Network: `backend` | Stateless | • Xem `docker compose logs gateway orders products` thấy cùng `requestId`.<br/>• Gọi `/api/internal/products/resolve` qua `:8080` bị chặn `404 NOT_FOUND`. |
| **4** | **Products Service** *(Catalog Microservice)* | Quản lý CRUD sản phẩm; tự động tạo bảng & seed 5 mặt hàng; cung cấp API nội bộ `/internal/products/resolve` cho Orders chốt giá | • `services/products/src/index.ts:6-9` (`productInput`, `createInput`, `patchInput`, `idInput`)<br/>• `index.ts:12-16` (`bootstrap` DDL + seed 5 items)<br/>• `index.ts:19-27` (`GET/POST/PATCH /products*`)<br/>• `index.ts:28-33` (`POST /internal/products/resolve`)<br/>• `services/products/src/db.ts:1-8` (`pool`, `bootstrap`) | • Container: `products` (`node:24-alpine`)<br/>• Internal Port: `3001`<br/>• Networks: `backend`, `products-data` | Sở hữu logic miền sản phẩm; kết nối tới `products-db` (`connectionLimit: 5`) | • Thêm/sửa giá sản phẩm tại `/admin/products`.<br/>• Deploy độc lập: `docker compose up -d --build --no-deps --wait products`. |
| **5** | **Products DB** *(MariaDB 11.8)* | Lưu trữ bền vững danh mục sản phẩm và giá niêm yết hiện hành | • DDL tại `services/products/src/index.ts:13` (`CREATE TABLE IF NOT EXISTS products(...)`)<br/>• Cấu hình tại `compose.yaml:77-85` | • Container: `products-db` (`mariadb:11.8`)<br/>• Internal Port: `3306`<br/>• Network: `products-data` (`internal: true`)<br/>• Volume: `products-data` | Bảng `products` (`id`, `name`, `description`, `price_vnd`, `is_active`, `created_at`, `updated_at`) | • Dữ liệu giữ nguyên sau `docker compose down` & `up -d`.<br/>• Cô lập mạng: `orders` không thể kết nối `products-db`. |
| **6** | **Orders Service** *(Ordering Microservice)* | Tiếp nhận đặt hàng; kiểm tra `Idempotency-Key` & băm `requestHash`; gọi `Products` lấy snapshot giá (timeout 3s); thực thi SQL transaction tạo đơn | • `services/orders/src/domain.ts:3-11` (`orderInput`, `keyInput`, `requestHash`, `priceOrder`)<br/>• `services/orders/src/index.ts:17-22` (`replay()`)<br/>• `index.ts:25-30` (`GET /orders`, `GET /orders/:id`)<br/>• `index.ts:31-54` (`POST /orders`, fetch resolve 3s, SQL transaction) | • Container: `orders` (`node:24-alpine`)<br/>• Internal Port: `3002`<br/>• Networks: `backend`, `orders-data` | Sở hữu logic miền đơn hàng; kết nối tới `orders-db` (`connectionLimit: 5`) | • Đặt đơn hàng $\rightarrow$ Đổi giá SP $\rightarrow$ Xem lại đơn cũ giá không đổi.<br/>• Stop `products` $\rightarrow$ Xem đơn cũ vẫn `200 OK`, tạo đơn mới báo `503` sau $\le 3\text{s}$. |
| **7** | **Orders DB** *(MariaDB 11.8)* | Lưu trữ bền vững đơn hàng, chi tiết mặt hàng snapshot và khóa `idempotency_key` duy nhất | • DDL tại `services/orders/src/index.ts:8-9` (`CREATE TABLE IF NOT EXISTS orders`, `order_items`)<br/>• Cấu hình tại `compose.yaml:86-94` | • Container: `orders-db` (`mariadb:11.8`)<br/>• Internal Port: `3306`<br/>• Network: `orders-data` (`internal: true`)<br/>• Volume: `orders-data` | Bảng `orders` (có `UNIQUE idempotency_key`, `request_hash`) và bảng `order_items` (snapshot `product_name`, `unit_price_vnd`) | • `npm run test:transaction`: lỗi ở item thứ 2 tự động rollback sạch bảng `orders`.<br/>• `npm run test:api`: kiểm tra replay & conflict 409. |

---

## PHẦN 2: QUY CÁCH CHO MỖI COMPONENT ĐƯA VÀO SLIDE (THEO `docs/INVENTORY.md` MỤC 8)

### 2.1. Khung quy cách 10 mục bắt buộc trên Slide & Speaker Notes

Theo quy định tại [`docs/INVENTORY.md` (Mục 8, dòng 148–153)](../../../../docs/INVENTORY.md#L148-L153):

> **Quy tắc trình bày mỗi Component trên Slide:**
> Mỗi component đưa vào slide cần một **thẻ giải thích (Component Card)** đi theo đúng chuỗi 10 mục:
> 1. **Trách nhiệm (Responsibility)** $\rightarrow$
> 2. **Đầu vào / Đầu ra và Contract (Input/Output & Contract)** $\rightarrow$
> 3. **State sở hữu (Owned State)** $\rightarrow$
> 4. **Thuật toán / Luồng chính (Core Algorithm / Main Flow)** $\rightarrow$
> 5. **Dependency / Giao thức (Dependencies & Protocols)** $\rightarrow$
> 6. **Failure / Retry / Concurrency (Xử lý lỗi, thử lại & đồng thời)** $\rightarrow$
> 7. **File và Symbol nguồn (`file:line` & symbols)** $\rightarrow$
> 8. **Container / Service / DB tương ứng (Runtime Mapping)** $\rightarrow$
> 9. **Bằng chứng Demo (Demo Evidence)** $\rightarrow$
> 10. **Trade-off (Đánh đổi kiến trúc)**.
>
> **Quy tắc trình bày mỗi Sơ đồ trên Slide:**
> * Phải kèm **đoạn giải thích bằng chữ**, **chú giải ký hiệu (legend)** và **nhãn giao thức / hướng gọi** (ví dụ: `HTTP POST /internal/products/resolve (timeout 3s)`).
> * Đánh dấu rõ: **Phần đang có thật trong code** vs **Phần dự kiến mở rộng** (dùng nét đứt hoặc màu riêng).
> * Có bảng mapping để người nghe đi được ngay từ một hộp trên hình tới file code và container đang chạy.

---

### 2.2. Bộ Thẻ Component (Component Cards) Chuẩn 10 Mục cho Slide

Dưới đây là nội dung chi tiết 10 mục cho từng component để bạn đưa thẳng vào Slide hoặc dùng khi trả lời vấn đáp:

---

#### THẺ 1: Browser SPA (`@mini/frontend`)

1. **Trách nhiệm:** Giao diện người dùng (Catalog, Giỏ hàng, Đơn hàng, Quản trị sản phẩm); lưu trữ giỏ hàng phía client và quản lý `Idempotency-Key` chờ khi đặt hàng.
2. **Đầu vào / Đầu ra & Contract:**
   * Đầu vào: Thao tác người dùng (click thêm giỏ, tìm kiếm, submit form checkout/admin).
   * Đầu ra: Các HTTP request JSON tới `/api/products`, `/api/products/:id`, `/api/orders`, `/api/orders/:id` (kèm header `Idempotency-Key` khi `POST /api/orders`).
3. **State sở hữu:** `localStorage` của trình duyệt gồm `mini-cart` (tối đa 20 mặt hàng, số lượng `1..99`), `mini-pending` (`{body, key}`), `mini-name`, `mini-email`.
4. **Thuật toán / Luồng chính:**
   * Khi tải trang: `savedCart()` lọc dữ liệu hợp lệ từ `localStorage`.
   * Tìm kiếm sản phẩm: Lọc trên mảng sản phẩm đã tải bằng `p.isActive && p.name.toLocaleLowerCase('vi').includes(...)`.
   * Khi đặt hàng (`submit`): Sắp xếp `items` theo `productId`, so sánh `body` với `mini-pending.body` trong `localStorage` — nếu trùng thì dùng lại `pending.key`, nếu khác thì tạo `crypto.randomUUID()`, gửi `POST /api/orders`, thành công mới xóa `mini-pending` và xóa giỏ.
5. **Dependency / Giao thức:** Gọi HTTP/1.1 JSON cùng origin tới Nginx (`/` và `/api/*`).
6. **Failure / Retry / Concurrency:**
   * Khóa nút bấm bằng cờ `busy` (`disabled={busy}`) chống double-click trên UI.
   * Khi request mạng lỗi hoặc nhận `503`, giữ nguyên `mini-pending` và giỏ hàng để người dùng nhấn gửi lại an toàn với cùng `Idempotency-Key`.
7. **File & Symbol nguồn:** `frontend/src/main.tsx:10-13` (`api`), `main.tsx:14` (`savedCart`), `main.tsx:18-26` (`App`), `main.tsx:27-35` (`Catalog`), `main.tsx:36-43` (`Cart`), `main.tsx:45-50` (`Orders`, `Detail`, `Admin`).
8. **Container / Service / DB tương ứng:** Được build thành static bundle trong container `frontend` (`/usr/share/nginx/html`) và thực thi trong trình duyệt của Client.
9. **Bằng chứng Demo:** Mở DevTools $\rightarrow$ Application $\rightarrow$ Local Storage xem `mini-cart` và `mini-pending`; chạy `npm run test:e2e` (`tests/browser.spec.ts`).
10. **Trade-off:** Lưu giỏ hàng ở `localStorage` giúp giảm tải backend và không cần session DB, nhưng giỏ hàng không đồng bộ giữa nhiều thiết bị/trình duyệt khác nhau.

---

#### THẺ 2: Frontend Web & Reverse Proxy (`frontend` — Nginx)

1. **Trách nhiệm:** Là cửa ngõ mạng duy nhất mở ra máy host (`127.0.0.1:8080`); phân phối tài nguyên tĩnh HTML/CSS/JS cho SPA và làm Reverse Proxy chuyển tiếp `/api/*` vào `gateway`.
2. **Đầu vào / Đầu ra & Contract:**
   * Đầu vào: HTTP request từ trình duyệt tại `127.0.0.1:8080`.
   * Đầu ra: File tĩnh hoặc proxy HTTP sang `http://gateway:3000`; nếu upstream lỗi 502/504 thì trả về `503 JSON {"error":{"code":"SERVICE_UNAVAILABLE",...}}`.
3. **State sở hữu:** Stateless (chỉ chứa file build tĩnh trong image).
4. **Thuật toán / Luồng chính:**
   * Khớp `/api/` $\rightarrow$ dùng Docker DNS resolver (`127.0.0.11 valid=5s`) phân giải động `$gateway = http://gateway:3000` và `proxy_pass`.
   * Các đường dẫn còn lại `/` $\rightarrow$ `try_files $uri $uri/ /index.html` để hỗ trợ React Router client-side routing.
5. **Dependency / Giao thức:** Phụ thuộc container `gateway` (`depends_on: gateway: service_healthy`) qua mạng `backend` bằng giao thức HTTP.
6. **Failure / Retry / Concurrency:** `proxy_read_timeout 10s`; bật `proxy_intercept_errors on` và bắt `error_page 502 504 =503 /upstream-unavailable` để frontend luôn nhận được JSON thay vì trang HTML lỗi mặc định của Nginx.
7. **File & Symbol nguồn:** `frontend/nginx.conf:1-20`, `frontend/Dockerfile:1-13`, `compose.yaml:21-34`.
8. **Container / Service / DB tương ứng:** Container `frontend` (`nginx:alpine`), port `127.0.0.1:8080:80`, network `backend`.
9. **Bằng chứng Demo:** Truy cập trực tiếp đường dẫn sâu `http://localhost:8080/orders` không bị lỗi 404 của web server; kiểm tra `docker compose ps`.
10. **Trade-off:** Phục vụ cả SPA và `/api` qua cùng một cổng Nginx giúp loại bỏ hoàn toàn độ phức tạp của CORS preflight request, nhưng mọi traffic đều đi qua thêm 1 hop proxy.

---

#### THẺ 3: API Gateway (`@mini/gateway`)

1. **Trách nhiệm:** Kiểm soát biên API (API Edge): lọc route/method theo whitelist, phát sinh/chuyển tiếp mã truy vết `X-Request-Id`, chuyển tiếp `Idempotency-Key`, áp timeout 8 giây và ẩn các endpoint nội bộ (`/internal/*`).
2. **Đầu vào / Đầu ra & Contract:**
   * Đầu vào: HTTP `GET`, `POST`, `PATCH` tới `/api/products`, `/api/products/:uuid`, `/api/orders`, `/api/orders/:uuid` (payload JSON tối đa `32kb`).
   * Đầu ra: Response JSON giữ nguyên HTTP status từ upstream kèm header `X-Request-Id`; hoặc lỗi `404 NOT_FOUND`, `400 INVALID_JSON`, `413 BODY_TOO_LARGE`, `503 SERVICE_UNAVAILABLE`.
3. **State sở hữu:** Stateless (không kết nối bất kỳ database nào).
4. **Thuật toán / Luồng chính:**
   * Middleware đầu tiên (`http.ts:7-14`) kiểm tra header `x-request-id` (nếu hợp lệ `/^[a-zA-Z0-9_-]{1,100}$/` thì giữ, không thì tạo `randomUUID()`), gắn vào `res.locals.requestId` và response header, đồng thời đo `durationMs` ghi log JSON khi kết thúc.
   * Middleware proxy (`index.ts:4-14`) kiểm tra regex `/^\/api\/(products|orders)(?:\/[a-fA-F0-9-]+)?$/` và method `['GET','POST','PATCH']`. Nếu khớp, cắt tiền tố `/api` và gọi `fetch()` tới `PRODUCTS_URL` (`:3001`) hoặc `ORDERS_URL` (`:3002`) với `AbortSignal.timeout(8000)`.
5. **Dependency / Giao thức:** Gọi HTTP đồng bộ tới `products:3001` và `orders:3002` trên mạng `backend`.
6. **Failure / Retry / Concurrency:** Nếu upstream quá 8 giây hoặc từ chối kết nối, khối `catch` ném `HttpError(503, 'Dịch vụ tạm thời không khả dụng. Vui lòng thử lại.', 'SERVICE_UNAVAILABLE')`. Không tự động retry ở Gateway để tránh nhân đôi các lệnh thay đổi trạng thái.
7. **File & Symbol nguồn:** `services/gateway/src/index.ts:1-17`, `services/gateway/src/http.ts:1-31`.
8. **Container / Service / DB tương ứng:** Container `gateway` (`node:24-alpine`), internal port `3000`, network `backend`.
9. **Bằng chứng Demo:** Gọi `curl -i http://localhost:8080/api/internal/products/resolve` nhận `404 NOT_FOUND`; xem log JSON có cùng `requestId` ở cả `gateway`, `orders`, `products`.
10. **Trade-off:** Dùng whitelist regex đơn giản giúp bảo mật bề mặt tấn công (chặn mọi route nội bộ và path lạ), nhưng khi thêm service mới cần cập nhật quy tắc định tuyến tại Gateway.

---

#### THẺ 4: Products Service (`@mini/products`) & `products-db`

1. **Trách nhiệm:** Quản lý danh mục sản phẩm (hiển thị, tạo mới, cập nhật giá/trạng thái) và cung cấp endpoint nội bộ `/internal/products/resolve` để `Orders Service` lấy thông tin sản phẩm chốt đơn.
2. **Đầu vào / Đầu ra & Contract:**
   * Public (qua Gateway): `GET /products`, `GET /products/:id`, `POST /products`, `PATCH /products/:id`.
   * Internal (chỉ từ mạng `backend`): `POST /internal/products/resolve` nhận `{ids: UUID[]}` (`1..20` phần tử), trả về `{items: Product[]}` hoặc `404 PRODUCT_NOT_FOUND` nếu thiếu bất kỳ ID nào.
3. **State sở hữu:** Sở hữu độc quyền bảng `products` trong `products-db` (MariaDB 11.8, volume `products-data`).
4. **Thuật toán / Luồng chính:**
   * Lúc khởi động (`bootstrap`): Thử kết nối DB tối đa 30 lần (cách nhau 2s), chạy `CREATE TABLE IF NOT EXISTS products(...)` và `INSERT ... ON DUPLICATE KEY UPDATE id=id` cho 5 sản phẩm mẫu có UUID cố định (`10000000-0000-4000-8000-000000000001`..`0005`).
   * Khi resolve: Kiểm tra mảng `ids` bằng Zod, truy vấn `SELECT * FROM products WHERE id IN (...)`, so sánh `rows.length !== new Set(ids).size` để phát hiện ID không tồn tại.
5. **Dependency / Giao thức:** Kết nối TCP/MySQL (`mysql2/promise`) tới `products-db:3306` qua mạng nội bộ `products-data` bằng tài khoản `products_app`.
6. **Failure / Retry / Concurrency:**
   * Connection pool giới hạn `connectionLimit: 5`, `connectTimeout: 2000ms`.
   * Các mã lỗi mất kết nối DB (`ECONNREFUSED`, `ETIMEDOUT`, ...) được `finishApp()` chuyển thành `503 DATABASE_UNAVAILABLE`.
7. **File & Symbol nguồn:** `services/products/src/index.ts:1-36`, `services/products/src/db.ts:1-8`, `services/products/src/http.ts:1-31`.
8. **Container / Service / DB tương ứng:** Container `products` (`:3001`, networks `backend` + `products-data`) và container `products-db` (`:3306`, network `products-data`, volume `products-data`).
9. **Bằng chứng Demo:** Vào trang Quản lý (`/admin/products`) sửa giá sản phẩm; chạy `docker compose up -d --build --no-deps --wait products` thấy `orders` không bị restart.
10. **Trade-off:** Trả toàn bộ danh sách sản phẩm trong `GET /products` (kể cả `isActive=false`) giúp dùng chung 1 API choทั้ง trang khách hàng và trang Admin, nhưng khi danh mục lớn sẽ cần tách API và bổ sung phân trang (pagination).

---

#### THẺ 5: Orders Service (`@mini/orders`) & `orders-db`

1. **Trách nhiệm:** Xử lý tạo đơn hàng đảm bảo tính Idempotent, lấy giá snapshot từ `Products Service`, lưu giao dịch nguyên tử (ACID local transaction) và phục vụ tra cứu lịch sử/chi tiết đơn hàng.
2. **Đầu vào / Đầu ra & Contract:**
   * `GET /orders?page=1&pageSize=10`: Trả về `{items, total, page, pageSize}`.
   * `GET /orders/:id`: Trả về đơn hàng kèm mảng `items` đã snapshot.
   * `POST /orders` (bắt buộc header `Idempotency-Key` dài 8–100 ký tự): Body `{customerName, customerEmail, items: [{productId, quantity}]}` (không nhận giá từ client). Trả về `201 Created` (đơn mới), `200 OK` (replay đơn cũ), `409 IDEMPOTENCY_CONFLICT` / `PRODUCT_INACTIVE`, `404 PRODUCT_NOT_FOUND`, hoặc `503 PRODUCTS_UNAVAILABLE`.
3. **State sở hữu:** Sở hữu độc quyền bảng `orders` và `order_items` trong `orders-db` (MariaDB 11.8, volume `orders-data`).
4. **Thuật toán / Luồng chính (`POST /orders`):**
   1. Validate body (`orderInput`, cấm trùng `productId` trong cùng 1 đơn) và header `Idempotency-Key` (`keyInput`).
   2. Tính `hash = requestHash(input)` (SHA-256 trên payload đã sắp xếp `items`).
   3. Gọi `replay(key, hash)`: nếu đã tồn tại `key` thì đối chiếu `request_hash` (khớp $\rightarrow$ trả đơn cũ `200 OK`, lệch $\rightarrow$ ném `409`).
   4. Gọi `POST http://products:3001/internal/products/resolve` với `AbortSignal.timeout(3000)` và truyền tiếp `X-Request-Id`.
   5. Kiểm tra tất cả sản phẩm phải `isActive === true`; gọi `priceOrder(input, data.items)` tính `unitPriceVnd`, `subtotalVnd`, `totalVnd`.
   6. Mở SQL Transaction trên 1 connection: `INSERT INTO orders` $\rightarrow$ lặp `INSERT INTO order_items` $\rightarrow$ `COMMIT`.
5. **Dependency / Giao thức:**
   * Gọi HTTP đồng bộ tới `products:3001` trên mạng `backend` (chỉ khi tạo đơn mới).
   * Kết nối TCP/MySQL tới `orders-db:3306` trên mạng nội bộ `orders-data` bằng tài khoản `orders_app`.
6. **Failure / Retry / Concurrency:**
   * Timeout 3 giây khi gọi `Products`: cô lập lỗi nhanh, trả `503 PRODUCTS_UNAVAILABLE`.
   * Rollback toàn phần khi bất kỳ lệnh `INSERT INTO order_items` nào thất bại.
   * Xử lý race condition 2 request trùng key chạy song song: bắt mã lỗi `ER_DUP_ENTRY` của MariaDB, `rollback()` rồi gọi lại `replay(key, hash)` để trả về đơn hàng vừa được commit.
7. **File & Symbol nguồn:** `services/orders/src/index.ts:1-57`, `services/orders/src/domain.ts:1-11`, `services/orders/src/db.ts:1-8`, `services/orders/src/http.ts:1-31`.
8. **Container / Service / DB tương ứng:** Container `orders` (`:3002`, networks `backend` + `orders-data`) và container `orders-db` (`:3306`, network `orders-data`, volume `orders-data`).
9. **Bằng chứng Demo:**
   * Kịch bản dừng `products` (`docker compose stop products`): xem lại đơn cũ vẫn `200 OK`, tạo đơn mới báo `503`.
   * Chạy `npm run test:transaction` để chứng minh rollback nguyên tử khi lỗi giữa chừng.
10. **Trade-off:** Gọi HTTP đồng bộ sang `Products` lúc tạo đơn đơn giản hơn nhiều so với Event-Driven/Saga và đảm bảo giá luôn mới nhất ngay lúc đặt, nhưng làm cho luồng `POST /orders` phụ thuộc vào tính sẵn sàng tức thời (temporal coupling) của `Products Service`.
