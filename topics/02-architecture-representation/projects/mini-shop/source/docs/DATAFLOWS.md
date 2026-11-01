# Mini Shop — Dataflow theo từng use case

Sơ đồ đối chiếu với code thực tế trong `services/`, `frontend/src/main.tsx`, cấu hình Nginx và Compose. Không có message broker, event bus hay database dùng chung trong bản demo này.

**Cách đọc:** mũi tên liền là request/lệnh; mũi tên nét đứt là response/kết quả; `alt` là nhánh điều kiện; `loop` là thao tác lặp; vùng transaction chỉ thuộc Orders DB. Các bước phía frontend diễn ra trong trình duyệt, Nginx chỉ phục vụ file tĩnh và reverse proxy.

**Quy tắc chung:** Nginx giữ nguyên `/api`; Gateway bỏ `/api` trước khi chuyển đến service. Gateway tạo hoặc nhận `X-Request-Id`, chuyển tiếp xuống service; Orders truyền cùng ID khi gọi Products. Gateway không kết nối database. Orders gọi Products trực tiếp qua HTTP nội bộ, không đi vòng qua Gateway.

## 00 — Tổng quan đường đi và quyền sở hữu dữ liệu

```mermaid
flowchart TB
    U[Người dùng] --> B[React trong trình duyệt]
    B <-->|Giỏ hàng và pending request| LS[(localStorage)]
    B -->|HTTP localhost:8080| N[Nginx / frontend container :80]
    N -->|HTML, CSS, JavaScript| B
    subgraph BACK[Docker network: backend]
      N -->|/api/*| G[API Gateway :3000]
      G -->|/products và /products/:id| P[Products Service :3001]
      G -->|/orders và /orders/:id| O[Orders Service :3002]
      O -->|POST /internal/products/resolve, timeout 3s| P
    end
    subgraph PD[Docker network: products-data]
      P -->|SQL bằng products_app| PDB[(MariaDB Products :3306 / bảng products)]
      PDB --- PV[Volume products-data]
    end
    subgraph OD[Docker network: orders-data]
      O -->|SQL bằng orders_app| ODB[(MariaDB Orders :3306 / orders + order_items)]
      ODB --- OV[Volume orders-data]
    end
    classDef data fill:#e5f1e7,stroke:#44845a,color:#183d25;
    classDef service fill:#e9efff,stroke:#5677b3,color:#1d3154;
    class PDB,ODB,LS data;
    class G,P,O service;
```

Chỉ `frontend` publish cổng host `127.0.0.1:8080` mặc định. Hai MariaDB đều dùng cổng 3306 **bên trong container khác nhau**, không xung đột MariaDB host. Chỉ Products tham gia network Products DB; chỉ Orders tham gia network Orders DB. `order_items.product_id` là tham chiếu logic, không có foreign key sang Products DB.

## 01 — Xem và tìm kiếm sản phẩm

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    participant B as React / Catalog
    participant N as Nginx
    participant G as Gateway
    participant P as Products
    participant D as Products DB
    U->>B: Mở trang sản phẩm
    B->>N: GET /api/products
    N->>G: GET /api/products
    G->>P: GET /products + X-Request-Id
    P->>D: SELECT * FROM products ORDER BY created_at,id
    D-->>P: Các sản phẩm, gồm cả inactive
    P->>P: Map price_vnd thành priceVnd, is_active thành boolean
    P-->>G: 200 JSON items
    G-->>N: 200 JSON + X-Request-Id
    N-->>B: Danh sách sản phẩm
    B->>B: Chỉ hiện isActive=true
    B-->>U: Card tên, mô tả, giá VND
    U->>B: Nhập từ khóa tìm kiếm
    B->>B: Lọc tên trong dữ liệu đã tải
    B-->>U: Danh sách đã lọc hoặc trạng thái trống
    Note over B,D: Tìm kiếm hiện tại chạy local, không phát sinh SQL/API mới
```

API dùng chung cho catalog và admin. Admin giữ cả sản phẩm ngừng bán. Nếu API lỗi, frontend hiển thị lỗi và nút thử lại. `GET /api/products/:id` cũng có trong backend: Products validate UUID, SELECT theo ID, trả 200 hoặc 404; frontend hiện chưa có màn hình chi tiết sản phẩm riêng.

## 02 — Thêm, sửa số lượng và xóa giỏ hàng

```mermaid
sequenceDiagram
    autonumber
    actor U as Người dùng
    participant B as React / Cart state
    participant L as localStorage
    U->>B: Nhấn Thêm trên card đã tải
    B->>B: Thêm dòng hoặc tăng quantity tối đa 99
    B->>L: Lưu mini-cart gồm ID, tên, giá hiển thị, quantity
    B-->>U: Cập nhật badge và thông báo
    U->>B: Mở giỏ, sửa quantity hoặc xóa dòng
    B->>B: Cập nhật state và tính tạm tính
    B->>L: Lưu mini-cart mới
    U->>B: Reload trang
    B->>L: Đọc mini-cart
    L-->>B: JSON giỏ đã lưu
    B->>B: Parse và kiểm tra dữ liệu cơ bản
    B-->>U: Khôi phục giỏ hoặc giỏ trống nếu dữ liệu lỗi
    Note over U,L: Không gọi Gateway, service hay database khi chỉ thay đổi giỏ
```

Giá trong giỏ chỉ phục vụ hiển thị; Orders sẽ lấy lại giá từ Products khi đặt hàng. Giỏ chỉ thuộc trình duyệt hiện tại, chưa đồng bộ nhiều thiết bị. Đơn giới hạn 20 dòng sản phẩm khác nhau.

## 03 — Quản trị: tạo sản phẩm

```mermaid
sequenceDiagram
    autonumber
    actor A as Người quản trị demo
    participant B as React / Admin
    participant N as Nginx
    participant G as Gateway
    participant P as Products
    participant D as Products DB
    A->>B: Nhập tên, mô tả, giá, trạng thái
    B->>N: POST /api/products, JSON form
    N->>G: Chuyển request
    G->>P: POST /products
    P->>P: Validate createInput, tạo UUID
    alt Dữ liệu không hợp lệ
      P-->>G: 400 VALIDATION_ERROR
      G-->>N: 400 JSON
      N-->>B: Thông báo lỗi, không ghi DB
    else Dữ liệu hợp lệ
      P->>D: INSERT INTO products
      D-->>P: Ghi thành công
      P->>D: SELECT sản phẩm theo UUID mới
      D-->>P: Bản ghi sản phẩm
      P-->>G: 201 Product
      G-->>N: 201 Product
      N-->>B: Đã lưu sản phẩm
      B->>N: GET /api/products để tải lại danh mục
      Note over N,D: Lặp lại luồng đọc danh sách ở UC01
    end
```

Chỉ Products DB thay đổi; Orders không nhận sự kiện và Orders DB không bị cập nhật. Đây là quản trị demo local, chưa có bước xác thực/kiểm tra role.

## 04 — Quản trị: sửa giá, tên hoặc ngừng bán

```mermaid
sequenceDiagram
    autonumber
    participant B as React / Admin
    participant N as Nginx
    participant G as Gateway
    participant P as Products
    participant D as Products DB
    B->>N: PATCH /api/products/:id, các trường cần sửa
    N->>G: Chuyển request
    G->>P: PATCH /products/:id
    P->>P: Validate UUID, body không rỗng, whitelist field
    P->>D: SELECT * FROM products WHERE id=?
    alt Không có sản phẩm
      D-->>P: Không có dòng
      P-->>G: 404 PRODUCT_NOT_FOUND
      G-->>N: 404
      N-->>B: Hiển thị lỗi
    else Có sản phẩm
      D-->>P: Bản ghi hiện tại
      P->>D: UPDATE chỉ những cột được gửi
      D-->>P: Thành công
      P->>D: SELECT bản ghi sau cập nhật
      D-->>P: Giá, tên, trạng thái mới
      P-->>G: 200 Product
      G-->>N: 200 Product
      N-->>B: Lưu thành công, tải lại danh mục
    end
    Note over B,D: Body sai hoặc rỗng trả 400 trước SQL
```

Frontend admin hiện gửi đủ bốn trường; backend PATCH hỗ trợ cập nhật từng phần. `isActive=false` ẩn sản phẩm khỏi catalog sau khi tải lại và khiến checkout mới trả 409 nếu giỏ còn chứa sản phẩm đó. **Đơn đã tạo giữ nguyên snapshot**, vì luồng này không ghi Orders DB. Các SQL của thao tác sửa sản phẩm không được bọc trong một transaction nhiều câu lệnh riêng.

## 05 — Tạo đơn mới thành công: dataflow đầy đủ

```mermaid
sequenceDiagram
    autonumber
    participant B as React / Checkout
    participant L as localStorage
    participant N as Nginx
    participant G as Gateway
    participant O as Orders
    participant OD as Orders DB
    participant P as Products
    participant PD as Products DB
    B->>B: Validate form, lấy productId và quantity
    B->>L: Lưu mini-pending gồm body và Idempotency-Key
    B->>N: POST /api/orders + Idempotency-Key
    Note over B,N: Body chỉ gồm customerName, customerEmail, items
    N->>G: Chuyển nguyên request /api/orders
    G->>O: POST /orders + key + X-Request-Id
    O->>O: Validate, chuẩn hóa tên/email, SHA-256 canonical body
    O->>OD: SELECT id,request_hash WHERE idempotency_key=?
    OD-->>O: Chưa có key
    O->>P: POST /internal/products/resolve, ids[], cùng requestId
    P->>PD: SELECT products WHERE id IN (...)
    PD-->>P: ID, tên, giá hiện tại, trạng thái
    P-->>O: 200 items
    O->>O: Kiểm tra active, tính subtotal và total bằng giá server
    rect rgb(231, 243, 235)
      Note over O,OD: Một transaction cục bộ trên cùng connection
      O->>OD: BEGIN
      O->>OD: INSERT orders với key UNIQUE, hash, total
      loop Mỗi mặt hàng
        O->>OD: INSERT order_items, snapshot tên và đơn giá
      end
      O->>OD: COMMIT
      OD-->>O: Ghi toàn bộ thành công
    end
    O->>OD: SELECT orders theo ID
    OD-->>O: Header đơn hàng
    O->>OD: SELECT order_items WHERE order_id=?
    OD-->>O: Các dòng snapshot
    O-->>G: 201 Order kèm items
    G-->>N: 201 Order
    N-->>B: Đặt hàng thành công
    B->>L: Xóa mini-pending, lưu giỏ trống
    B->>B: Chuyển /orders/:id và tải chi tiết theo UC07
```

Giá chốt là giá Products trả về tại lần resolve. Orders **chỉ đọc Products qua API**, không trực tiếp truy vấn Products DB. Không có bước trừ tồn kho hay ghi ngược Products. Lời gọi HTTP diễn ra **trước BEGIN**, tránh giữ transaction trong thời gian chờ mạng.

## 06 — Xem danh sách đơn và phân trang

```mermaid
sequenceDiagram
    autonumber
    participant B as React / Orders list
    participant N as Nginx
    participant G as Gateway
    participant O as Orders
    participant D as Orders DB
    B->>N: GET /api/orders?page=1&pageSize=10
    N->>G: Giữ query string
    G->>O: GET /orders?page=1&pageSize=10
    O->>O: Validate page và pageSize
    O->>D: SELECT orders ORDER BY created_at DESC,id DESC LIMIT ? OFFSET ?
    D-->>O: Các header của trang hiện tại
    O->>D: SELECT COUNT(*) AS total FROM orders
    D-->>O: Tổng số đơn
    O-->>G: 200 items,total,page,pageSize
    G-->>N: 200 JSON
    N-->>B: Hiển thị danh sách và nút chuyển trang
    B->>N: GET /api/orders?page=2&pageSize=10
    Note over N,D: Lặp lại với OFFSET của trang tiếp theo
```

Không đọc `order_items` cho màn hình danh sách; không gọi Products. Hai SELECT danh sách/count không ở cùng transaction snapshot nên có thể lệch nhẹ khi có đơn được tạo đồng thời. Đây là giới hạn của pagination hiện tại, không phải dữ liệu được cache ở Gateway.

## 07 — Xem chi tiết đơn và giá snapshot

```mermaid
sequenceDiagram
    autonumber
    participant B as React / Order detail
    participant N as Nginx
    participant G as Gateway
    participant O as Orders
    participant D as Orders DB
    B->>N: GET /api/orders/:id
    N->>G: Chuyển request
    G->>O: GET /orders/:id
    O->>O: Validate UUID
    O->>D: SELECT * FROM orders WHERE id=?
    alt Đơn không tồn tại
      D-->>O: Không có dòng
      O-->>G: 404 ORDER_NOT_FOUND
      G-->>N: 404
      N-->>B: Hiển thị lỗi
    else Có đơn
      D-->>O: Tên/email, total, trạng thái, thời gian
      O->>D: SELECT order_items WHERE order_id=? ORDER BY product_id
      D-->>O: productName, unitPriceVnd, quantity, subtotalVnd
      O-->>G: 200 Order + items
      G-->>N: 200 JSON
      N-->>B: Hiển thị đơn bằng dữ liệu snapshot
    end
    Note over B,D: Không gọi Products, vẫn đọc được khi Products dừng
```

Khi reload trực tiếp `/orders/:id`, Nginx trả `index.html` bằng SPA fallback, React khởi động rồi gọi API như sơ đồ. Đường dẫn trang và đường dẫn `/api/orders/:id` có vai trò khác nhau.

## 08 — Gửi lại đơn sau mất phản hồi: idempotency

```mermaid
sequenceDiagram
    autonumber
    participant B as React / Checkout
    participant L as localStorage
    participant N as Nginx
    participant G as Gateway
    participant O as Orders
    participant D as Orders DB
    Note over O,D: Lần đầu đã COMMIT đơn thành công theo UC05
    O-->>G: 201 Order
    G-->>N: 201 Order
    N--xB: Phản hồi bị mất trước khi browser nhận
    Note over B,L: Giỏ và mini-pending vẫn còn vì chưa xác nhận thành công
    B->>L: Reload / thử lại, đọc body và key cũ
    L-->>B: Cùng payload, cùng Idempotency-Key
    B->>N: POST /api/orders với key cũ
    N->>G: Chuyển request
    G->>O: POST /orders
    O->>O: Chuẩn hóa input, tính hash
    O->>D: SELECT id,request_hash WHERE key=?
    D-->>O: Đơn đã tạo và hash cũ
    alt Hash trùng
      O->>D: SELECT orders và order_items theo ID cũ
      D-->>O: Snapshot đơn cũ
      O-->>G: 200 cùng Order ID
      G-->>N: 200
      N-->>B: Nhận đơn cũ, xóa pending và giỏ
    else Cùng key nhưng hash khác
      O-->>G: 409 IDEMPOTENCY_CONFLICT
      G-->>N: 409
      N-->>B: Hiển thị xung đột
    end
    Note over O,D: Không resolve Products và không INSERT đơn mới khi replay
```

Gateway không tự retry POST. Frontend giữ key khi body không đổi; thay đổi nội dung sẽ sinh key mới. Nhánh 409 cùng key/body khác chủ yếu bảo vệ client khác hoặc request API thủ công. Replay vẫn có thể thành công khi Products đang tắt.

## 09 — Hai yêu cầu tạo đơn đồng thời cùng key

```mermaid
sequenceDiagram
    autonumber
    participant C as Client qua Nginx và Gateway
    participant A as Orders / request A
    participant B as Orders / request B
    participant D as Orders DB
    participant P as Products API
    C->>A: POST /orders, key K
    C->>B: POST /orders, key K
    A->>D: Tìm key K
    D-->>A: Chưa có
    B->>D: Tìm key K
    D-->>B: Chưa có
    A->>P: Resolve sản phẩm
    P-->>A: Giá hiện tại
    B->>P: Resolve sản phẩm
    P-->>B: Giá hiện tại
    A->>D: BEGIN, INSERT orders với key K
    B->>D: BEGIN, INSERT orders với key K
    Note over B,D: UNIQUE key khiến request B chờ transaction A
    A->>D: INSERT items rồi COMMIT
    D-->>B: ER_DUP_ENTRY sau khi A commit
    B->>D: ROLLBACK, release connection
    B->>D: Tìm lại key K và so hash
    D-->>B: Đơn A đã commit
    A-->>C: 201 Order mới
    alt Cùng hash
      B->>D: Đọc header và items của đơn A
      D-->>B: Order snapshot
      B-->>C: 200 cùng Order ID
    else Hash khác
      B-->>C: 409 IDEMPOTENCY_CONFLICT
    end
```

Hai participant Orders là **hai request handler**, không hàm ý có hai container Orders. Sơ đồ minh họa một thứ tự xen kẽ hợp lệ; request thắng không cố định. Trong test, 6 request cùng key tạo đúng một đơn. Nếu A rollback thay vì commit, B có thể tiếp tục insert thành công. Gateway/Nginx được gộp vào client ở sơ đồ này để tập trung vào race database.

## 10 — Checkout lỗi do Products hoặc sản phẩm không hợp lệ

```mermaid
sequenceDiagram
    autonumber
    participant B as React / Checkout
    participant N as Nginx
    participant G as Gateway
    participant O as Orders
    participant D as Orders DB
    participant P as Products
    participant PD as Products DB
    B->>N: POST /api/orders với key mới
    N->>G: Chuyển request
    G->>O: POST /orders
    O->>D: Tìm idempotency key
    D-->>O: Chưa tồn tại
    O->>P: POST /internal/products/resolve
    alt Products không kết nối được hoặc timeout 3s
      Note over O,P: fetch lỗi, hoặc AbortSignal hủy request
      O-->>G: 503 PRODUCTS_UNAVAILABLE
    else Products hoạt động
      P->>PD: SELECT sản phẩm theo ids
      PD-->>P: Kết quả truy vấn
      alt Thiếu ít nhất một ID
        P-->>O: 404 PRODUCT_NOT_FOUND
        O-->>G: 404 PRODUCT_NOT_FOUND
      else Đủ ID nhưng có sản phẩm inactive
        P-->>O: 200 items có isActive=false
        O-->>G: 409 PRODUCT_INACTIVE
      else Products trả lỗi HTTP khác
        P-->>O: HTTP không thành công
        O-->>G: 503 PRODUCTS_UNAVAILABLE
      end
    end
    G-->>N: Giữ status và JSON lỗi của Orders
    N-->>B: Hiện lỗi, cho phép sửa giỏ hoặc thử lại
    Note over O,D: Chưa BEGIN, không có INSERT orders/order_items
```

Nhánh này chỉ mô tả các tình huống lỗi; đủ sản phẩm active sẽ đi tiếp UC05. Trường hợp Orders/Gateway không đáp ứng: Gateway có timeout 8 giây và trả `503 SERVICE_UNAVAILABLE`; Nginx chờ upstream 10 giây, ánh xạ 502/504 sang JSON 503. Mất response không chứng minh transaction chưa commit: client phải giữ key để retry an toàn theo UC08.

## 11 — Lỗi ghi item: rollback toàn bộ đơn

```mermaid
sequenceDiagram
    autonumber
    participant B as React qua Nginx
    participant G as Gateway
    participant O as Orders
    participant D as Orders DB
    Note over O,D: Validate, kiểm tra key và resolve Products đã thành công
    rect rgb(255, 240, 233)
      O->>D: BEGIN
      O->>D: INSERT orders
      D-->>O: Thành công, chưa commit
      O->>D: INSERT item thứ nhất
      D-->>O: Thành công, chưa commit
      O->>D: INSERT item thứ hai
      D-->>O: SQL error, ví dụ trigger test SIGNAL 45000
      O->>D: ROLLBACK
      D-->>O: Hủy order và item thứ nhất
    end
    O->>O: Release connection, chuyển lỗi tới middleware
    O-->>G: 500 INTERNAL_ERROR cho lỗi trigger test
    G-->>B: Trả lỗi qua Nginx
    Note over B,D: Không giữ idempotency key từ transaction đã rollback
    B->>G: Retry cùng body và key, qua Nginx
    G->>O: POST /orders
    O->>D: Tìm key
    D-->>O: Chưa tồn tại
    Note over O,D: Sau khi gỡ nguyên nhân lỗi, chạy lại UC05
    O-->>G: 201 Order sau lần ghi thành công
    G-->>B: Thành công qua Nginx
```

Sơ đồ mô tả lỗi statement **trước COMMIT** và rollback thành công. Lỗi mạng đúng lúc COMMIT có thể khiến client không biết kết quả; retry cùng key vẫn là cách phân giải. Không cần rollback Products DB vì checkout chỉ đọc dữ liệu ở đó. Bài test `verify-transaction.mjs` thực sự chặn item thứ hai, xác nhận số order/item không tăng và sau đó retry thành công.

## 12 — Healthcheck và readiness theo service

```mermaid
sequenceDiagram
    autonumber
    participant H as Docker healthchecks
    participant G as Gateway
    participant P as Products
    participant PD as Products DB
    participant O as Orders
    participant OD as Orders DB
    H->>G: GET /health/ready trên cổng nội bộ 3000
    G-->>H: 200 nếu process phục vụ được request
    H->>P: GET /health/ready trên cổng nội bộ 3001
    P->>PD: SELECT 1
    PD-->>P: Thành công hoặc lỗi kết nối
    P-->>H: 200 khi DB truy cập được, non-200 khi lỗi
    H->>O: GET /health/ready trên cổng nội bộ 3002
    O->>OD: SELECT 1
    OD-->>O: Thành công hoặc lỗi kết nối
    O-->>H: 200 khi DB truy cập được, non-200 khi lỗi
    Note over O,OD: Orders readiness không kiểm tra Products
    Note over H,G: Gateway readiness không xác nhận mọi upstream đều healthy
```

`/health/live` chỉ cho biết process trả lời; `/health/ready` ở service database kiểm tra SELECT 1. Docker healthcheck không đi qua Gateway public. Frontend có healthcheck HTTP `/`; mỗi MariaDB chạy `healthcheck.sh --connect --innodb_initialized`. Khi startup, Compose chờ database healthy rồi service, Gateway, frontend. Thứ tự startup không tạo ra sự phụ thuộc bắt buộc cho mọi use case khi runtime.

## Bảng tóm tắt data ownership theo use case

| Use case | Gateway | Products | Products DB | Orders | Orders DB | localStorage |
|---|---|---|---|---|---|---|
| Xem sản phẩm | Route | Truy vấn/map | Đọc | — | — | — |
| Tìm kiếm sau tải | — | — | — | — | — | — |
| Sửa giỏ | — | — | — | — | — | Đọc/ghi giỏ |
| Tạo/sửa sản phẩm | Route | Validate/ghi | Đọc + ghi | — | — | — |
| Đặt đơn mới | Route | Resolve | Đọc | Validate/tính tiền | Đọc key + ghi transaction + đọc kết quả | Pending + xóa giỏ khi thành công |
| Xem đơn | Route | — | — | Truy vấn snapshot | Đọc | — |
| Replay key đã có | Route | — | — | So hash/trả snapshot | Chỉ đọc | Đọc pending |
| Race key mới | Route | Resolve từng request nếu cần | Đọc | Transaction + replay loser | UNIQUE/commit/rollback | Tùy client |

## Liên kết code và bằng chứng

- [Gateway routing và timeout](../services/gateway/src/index.ts)
- [Products API, SELECT/INSERT/UPDATE](../services/products/src/index.ts)
- [Orders transaction, replay, resolve và truy vấn đơn](../services/orders/src/index.ts)
- [Validation, hash và tính tiền](../services/orders/src/domain.ts)
- [Frontend và localStorage](../frontend/src/main.tsx)
- [Nginx](../frontend/nginx.conf), [Compose](../compose.yaml)
- [Kết quả kiểm thử](VERIFICATION.md)
