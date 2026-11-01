# Mô hình kiến trúc C4 — Mini Shop (Lab 01)

Tài liệu này chuẩn hóa kiến trúc hệ thống **Mini Shop Microservices** theo phương pháp **C4 Model** (Context, Container, Component, Code). Mô hình C4 giúp trực quan hóa kiến trúc phần mềm ở các cấp độ phóng to (zoom levels) khác nhau từ bối cảnh kinh doanh đến chi tiết thành phần mã nguồn.

---

## 1. C4 Level 1: System Context Diagram (Bối cảnh hệ thống)

Biểu đồ bối cảnh hệ thống mô tả mối quan hệ giữa người dùng (Actors) và hệ thống Mini Shop trong phạm vi tổng thể, cùng với các ranh giới ngoại vi.

### 1.1. Sơ đồ System Context

```mermaid
flowchart TB
    subgraph Users["Người dùng (Actors)"]
        Customer["👤 Khách hàng (Customer)<br/>[Person]<br/>Duyệt sản phẩm, quản lý giỏ hàng, đặt hàng và tra cứu đơn hàng."]
        Admin["👤 Quản trị viên (Store Admin)<br/>[Person]<br/>Thêm mới, sửa giá/tên, bật/ngừng kinh doanh sản phẩm."]
    end

    subgraph SystemBoundary["Hệ thống Mini Shop Microservices [Software System]"]
        MiniShop["🛒 Mini Shop Platform<br/>[Software System]<br/>Hệ thống thương mại điện tử kiến trúc Microservices phân tán.<br/>Cung cấp catalog, giỏ hàng, quản lý đơn hàng snapshot và quản trị sản phẩm."]
    end

    subgraph ClientEnv["Môi trường phía Client (Trình duyệt)"]
        BrowserStorage[("💾 Trình duyệt LocalStorage<br/>[External Storage]<br/>Lưu trữ giỏ hàng và Idempotency Key tạm thời.")]
    end

    Customer -->|Duyệt catalog, tạo đơn hàng qua HTTP :8080| MiniShop
    Customer -.->|Đọc / ghi giỏ hàng offline cục bộ| BrowserStorage
    Admin -->|Quản trị danh mục sản phẩm qua HTTP :8080| MiniShop
```

### 1.2. Bảng mô tả thành phần Bối cảnh

| Phần tử | Loại | Vai trò & Trách nhiệm |
|---|---|---|
| **Khách hàng (Customer)** | Person | Người mua hàng trực tuyến: tìm kiếm sản phẩm, quản lý giỏ hàng, thực hiện checkout và tra cứu trạng thái/chi tiết đơn hàng. |
| **Quản trị viên (Store Admin)** | Person | Nhân viên vận hành cửa hàng: tạo sản phẩm mới, cập nhật giá niêm yết, đổi tên/mô tả hoặc ngừng kinh doanh sản phẩm. |
| **Mini Shop Platform** | Software System | Hệ thống phần mềm chính của đồ án Lab 01, chạy hoàn toàn trên Docker Compose cục bộ, cung cấp toàn bộ API và giao diện Web. |
| **Trình duyệt LocalStorage** | External Client Storage | Vùng nhớ lưu trữ trạng thái giỏ hàng và Idempotency Key pending tại máy người dùng để chống mất dữ liệu khi reload hoặc rớt mạng. |

---

## 2. C4 Level 2: Container Diagram (Mô hình Container ứng dụng)

Mô hình Container phân tách hệ thống thành các khối thực thi độc lập (dịch vụ, ứng dụng frontend, cơ sở dữ liệu), xác định giao thức giao tiếp và phân vùng mạng (network isolation).

### 2.1. Sơ đồ Container

```mermaid
flowchart TB
    Customer[Khách hàng]
    Admin[Quản trị viên]

    subgraph ClientSide[Phía Client - Trình duyệt web]
        SPA[Single-Page Application: React 19 + Vite]
        LocalStorage[(LocalStorage: Giỏ hàng và pending key)]
        SPA <-->|Đọc và ghi giỏ hàng| LocalStorage
    end

    Customer -->|Duyệt catalog và mua hàng| SPA
    Admin -->|Quản trị sản phẩm| SPA
    SPA -->|HTTP localhost:8080| Nginx[Web Server: Nginx 1.27 / Port 8080]

    subgraph NetBackend[Docker Network: backend]
        Nginx -->|Proxy /api/*| Gateway[API Gateway :3000]
        Gateway -->|/api/products/*| Products[Products Service :3001]
        Gateway -->|/api/orders/*| Orders[Orders Service :3002]
        Orders -->|POST /internal/products/resolve, timeout 3s| Products
    end

    subgraph NetProductsData[Docker Network: products-data internal]
        Products -->|SQL bằng products_app| ProductsDB[(MariaDB Products :3306 / Bảng products)]
        ProductsDB --- PV[Volume: products-data]
    end

    subgraph NetOrdersData[Docker Network: orders-data internal]
        Orders -->|SQL bằng orders_app| OrdersDB[(MariaDB Orders :3306 / Bảng orders và order_items)]
        OrdersDB --- OV[Volume: orders-data]
    end

    classDef data fill:#e5f1e7,stroke:#44845a,color:#183d25;
    classDef service fill:#e9efff,stroke:#5677b3,color:#1d3154;
    class ProductsDB,OrdersDB,LocalStorage data;
    class Gateway,Products,Orders service;
```

### 2.2. Bảng phân tích chi tiết các Container

| Container | Công nghệ | Cổng & Network | Trách nhiệm kiến trúc |
|---|---|---|---|
| **Single-Page Application (SPA)** | React 19, TypeScript, Vite | Trình duyệt Client | Render giao diện người dùng, điều hướng client-side, quản lý giỏ hàng và xử lý retry idempotent khi mất mạng. |
| **frontend (Nginx)** | Nginx 1.27 Alpine | `127.0.0.1:8080:80` (host)<br/>Network: `backend` | Đóng vai trò Reverse Proxy duy nhất mở ra máy host; phân phối file HTML/JS/CSS tĩnh và chuyển tiếp các request `/api/*` vào Gateway. |
| **gateway** | Node.js 24, TypeScript | Port `3000`<br/>Network: `backend` | Điểm vào tập trung (API Gateway pattern): định tuyến whitelist, phát sinh/chuyển tiếp `X-Request-Id`, áp đặt timeout 8s, ẩn hoàn toàn các API `/internal/*`. |
| **products** | Node.js 24, TypeScript | Port `3001`<br/>Networks: `backend`, `products-data` | Quản lý vòng đời sản phẩm, seed dữ liệu ban đầu, cung cấp endpoint nội bộ `/internal/products/resolve` để snapshot giá cho Orders. |
| **orders** | Node.js 24, TypeScript | Port `3002`<br/>Networks: `backend`, `orders-data` | Tiếp nhận checkout, phối hợp gọi Products để chốt giá snapshot, kiểm soát Idempotency Key chống trùng lặp và điều phối Database Transaction cục bộ. |
| **products-db** | MariaDB 11.8 InnoDB | Port `3306` (nội bộ)<br/>Network: `products-data` | Cơ sở dữ liệu riêng của Products Service. Lưu trên volume `products-data`. Không mở port ra host. |
| **orders-db** | MariaDB 11.8 InnoDB | Port `3306` (nội bộ)<br/>Network: `orders-data` | Cơ sở dữ liệu riêng của Orders Service. Lưu trên volume `orders-data`. Không mở port ra host. |

---

## 3. C4 Level 3: Component Diagrams (Mô hình thành phần bên trong Service)

Cấp độ này đi sâu vào cấu trúc module mã nguồn của từng Microservice backend:

### 3.1. Thành phần của Products Service (`services/products`)

```mermaid
flowchart TB
    subgraph ProductsService["Products Service (Node.js/TypeScript :3001)"]
        direction TB
        HttpServer["Products HTTP Router<br/><b>[src/index.ts & src/http.ts]</b><br/>Lắng nghe HTTP, điều hướng request, gắn RequestId, xử lý route công khai và nội bộ."]
        
        Validator["Validation Layer<br/><b>[Zod Schemas]</b><br/>Kiểm tra tính hợp lệ của createInput, patchInput, resolveInput; từ chối unknown fields."]
        
        CatalogController["Catalog Controller<br/><b>[src/index.ts]</b><br/>Xử lý nghiệp vụ: GET danh sách (active/all), GET chi tiết, POST tạo mới, PATCH cập nhật sản phẩm."]
        
        ResolverController["Internal Product Resolver<br/><b>[src/index.ts]</b><br/>Xử lý POST /internal/products/resolve cho Orders Service; kiểm tra trạng thái active và trả về giá snapshot."]
        
        HealthComponent["Healthcheck Component<br/><b>[src/index.ts]</b><br/>Phản hồi /health/live (process) và /health/ready (SELECT 1 DB)."]
        
        ProductRepo["Product Repository & DB Manager<br/><b>[src/db.ts]</b><br/>Quản lý Connection Pool mysql2, DDL khởi tạo schema v1, seed 5 sản phẩm mẫu, thực thi Prepared Statements."]
    end

    GatewayInput["API Gateway / Orders Service"] -->|HTTP Requests| HttpServer
    HttpServer -->|Validate dữ liệu| Validator
    HttpServer -->|Nghiệp vụ Catalog| CatalogController
    HttpServer -->|Nghiệp vụ Resolve nội bộ| ResolverController
    HttpServer -->|Health Probe| HealthComponent
    CatalogController -->|CRUD sản phẩm| ProductRepo
    ResolverController -->|Batch query theo IDs| ProductRepo
    HealthComponent -->|Ping kết nối| ProductRepo
    ProductRepo -->|SQL Query / Prepared Statements| ProductsDB[("Products DB (MariaDB)")]
```

### 3.2. Thành phần của Orders Service (`services/orders`)

```mermaid
flowchart TB
    subgraph OrdersService["Orders Service (Node.js/TypeScript :3002)"]
        direction TB
        HttpServer["Orders HTTP Router<br/><b>[src/index.ts & src/http.ts]</b><br/>Lắng nghe HTTP :3002, kiểm tra Content-Length (<=32KB), parse JSON, điều phối luồng."]
        
        OrderDomain["Domain Calculation Engine<br/><b>[src/domain.ts]</b><br/>Tính subtotal, tính tổng tiền safe integer, chuẩn hóa canonical request payload và tính hash SHA-256."]
        
        IdempotencyManager["Idempotency Controller<br/><b>[src/index.ts]</b><br/>Kiểm tra Idempotency-Key: đối chiếu SHA-256 hash, xử lý replay đơn cũ (200) hoặc báo lỗi xung đột (409)."]
        
        ProductClient["Products HTTP Client<br/><b>[src/index.ts]</b><br/>Gửi POST /internal/products/resolve với AbortSignal timeout 3s; xử lý lỗi 404, 409 inactive, 503."]
        
        TransactionManager["Order Transaction Manager<br/><b>[src/db.ts]</b><br/>Quản lý DB Connection, mở Transaction: INSERT bảng orders, lặp INSERT bảng order_items, COMMIT hoặc ROLLBACK khi lỗi."]
        
        OrderReader["Order Query Component<br/><b>[src/db.ts]</b><br/>Truy vấn danh sách đơn hàng có phân trang (page, pageSize) và truy vấn chi tiết đơn kèm snapshot items."]
    end

    GatewayInput["API Gateway"] -->|POST /api/orders, GET /api/orders/*| HttpServer
    HttpServer -->|Tính toán & Canonical hash| OrderDomain
    HttpServer -->|Kiểm tra Key & Replay| IdempotencyManager
    HttpServer -->|Truy vấn dữ liệu| OrderReader
    IdempotencyManager -->|Resolve giá snapshot| ProductClient
    ProductClient -->|HTTP POST timeout 3s| ProductsServiceExt["Products Service (:3001)"]
    IdempotencyManager -->|Tạo đơn nguyên tử| TransactionManager
    TransactionManager -->|BEGIN -> INSERT -> COMMIT / ROLLBACK| OrdersDB[("Orders DB (MariaDB)")]
    OrderReader -->|SELECT có phân trang| OrdersDB
```

### 3.3. Thành phần của API Gateway (`services/gateway`)

```mermaid
flowchart TB
    subgraph APIGateway["API Gateway (Node.js/TypeScript :3000)"]
        direction TB
        HttpListener["HTTP Listener & Security Filter<br/><b>[src/index.ts]</b><br/>Tiếp nhận request từ Nginx; chặn ngay các đường dẫn cấm (/internal/*, /health/*)."]
        
        TracingMiddleware["Distributed Tracing Middleware<br/><b>[src/http.ts]</b><br/>Đọc header X-Request-Id từ client hoặc tự sinh UUID mới; chuyển tiếp header tới các downstream services."]
        
        ProxyRouter["Reverse Proxy Router<br/><b>[src/index.ts]</b><br/>Định tuyến whitelist: /api/products/* -> Products Service, /api/orders/* -> Orders Service."]
        
        TimeoutHandler["Timeout & Error Normalizer<br/><b>[src/http.ts]</b><br/>Thiết lập timeout 8s cho upstream; chuyển đổi lỗi mạng thành JSON chuẩn: {error: {code, message}, requestId}."]
    end

    NginxExt["Nginx Frontend"] -->|HTTP /api/*| HttpListener
    HttpListener --> TracingMiddleware
    TracingMiddleware --> ProxyRouter
    ProxyRouter --> TimeoutHandler
    TimeoutHandler -->|HTTP :3001| ProductsExt["Products Service"]
    TimeoutHandler -->|HTTP :3002| OrdersExt["Orders Service"]
```

---

## 4. C4 Level 4: Code & Data Entity Model (Mô hình Dữ liệu)

Mô hình dữ liệu vật lý thể hiện rõ nguyên lý **Database-per-Service**: hai cơ sở dữ liệu hoàn toàn độc lập, không có khóa ngoại (Foreign Key) vật lý xuyên qua ranh giới dịch vụ.

```mermaid
erDiagram
    PRODUCTS {
        string id PK
        string name
        string description
        bigint price_vnd
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ORDERS {
        string id PK
        string customer_name
        string customer_email
        bigint total_vnd
        string status
        string idempotency_key
        string request_hash
        datetime created_at
    }

    ORDER_ITEMS {
        string id PK
        string order_id FK
        string product_id
        string product_name
        bigint unit_price_vnd
        int quantity
        bigint subtotal_vnd
    }

    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : references
```

### Chi tiết các trường dữ liệu theo Schema vật lý

| Bảng (Database) | Cột | Kiểu SQL | Ràng buộc | Ý nghĩa kiến trúc |
|---|---|---|---|---|
| **products** *(Products DB)* | `id` | `CHAR(36)` | PK | UUID v4 định danh sản phẩm |
| | `name` | `VARCHAR(150)` | NOT NULL | Tên sản phẩm |
| | `description` | `TEXT` | NULL | Mô tả chi tiết |
| | `price_vnd` | `BIGINT UNSIGNED` | NOT NULL | Giá bán niêm yết hiện tại |
| | `is_active` | `BOOLEAN` | DEFAULT true | Trạng thái kinh doanh |
| | `created_at` / `updated_at` | `DATETIME(3)` | NOT NULL | Dấu thời gian (timestamp) |
| **orders** *(Orders DB)* | `id` | `CHAR(36)` | PK | UUID v4 định danh đơn hàng |
| | `customer_name` | `VARCHAR(100)` | NOT NULL | Tên người nhận |
| | `customer_email` | `VARCHAR(254)` | NOT NULL | Email người nhận |
| | `total_vnd` | `BIGINT UNSIGNED` | NOT NULL | Tổng tiền thanh toán an toàn (Safe Integer) |
| | `status` | `VARCHAR(20)` | NOT NULL | Trạng thái (`COMPLETED`) |
| | `idempotency_key` | `VARCHAR(100)` | UNIQUE | Khóa chống trùng đơn hàng |
| | `request_hash` | `CHAR(64)` | NOT NULL | SHA-256 canonical hash của payload |
| | `created_at` | `DATETIME(3)` | NOT NULL | Thời điểm tạo đơn |
| **order_items** *(Orders DB)* | `id` | `CHAR(36)` | PK | UUID v4 định danh dòng mặt hàng |
| | `order_id` | `CHAR(36)` | FK | Liên kết bảng `orders` (CASCADE DELETE nội bộ) |
| | `product_id` | `CHAR(36)` | NOT NULL | **Tham chiếu logic** sang Products (không tạo FK vật lý) |
| | `product_name` | `VARCHAR(150)` | NOT NULL | **Snapshot** tên sản phẩm tại thời điểm mua |
| | `unit_price_vnd` | `BIGINT UNSIGNED` | NOT NULL | **Snapshot** đơn giá tại thời điểm mua |
| | `quantity` | `INT` | NOT NULL | Số lượng (1–99) |
| | `subtotal_vnd` | `BIGINT UNSIGNED` | NOT NULL | Thành tiền dòng mặt hàng |

### Điểm nhấn thiết kế dữ liệu Microservices:
1. **Zero Cross-DB Foreign Keys:** `order_items.product_id` chỉ lưu mã định danh logic kiểu chuỗi, không tạo `FOREIGN KEY` sang `products.id` vì hai bảng nằm ở 2 container MariaDB khác nhau.
2. **Price & Name Snapshot:** Cột `product_name` và `unit_price_vnd` trong `order_items` lưu lại dữ liệu ngay tại thời điểm thanh toán. Dù Quản trị viên có đổi giá hoặc đổi tên sản phẩm ở `products`, dữ liệu lịch sử đơn hàng ở `orders` vẫn được bảo toàn nguyên vẹn.

---

## 5. Ma trận ánh xạ các đặc trưng Microservices vào C4 Model

| Đặc trưng Microservices | Vị trí thể hiện trong C4 Model | Cách hiện thực trong Lab 01 |
|---|---|---|
| **Database-per-service** | C4 Level 2 (Container) & Level 4 (Data) | Hai container MariaDB riêng biệt (`products-db`, `orders-db`) trên hai network Docker độc lập (`products-data`, `orders-data`). |
| **API Gateway Pattern** | C4 Level 2 (Container) & Level 3 (Gateway) | Container `gateway` làm cổng tập trung, che giấu cấu trúc mạng nội bộ, quản lý timeout và chuyển tiếp `X-Request-Id`. |
| **Independent Deployment** | C4 Level 2 (Container) | Các container có Dockerfile/build args riêng, triển khai độc lập bằng `docker compose up -d --build --no-deps products` mà không gián đoạn Orders. |
| **Fault Isolation** | C4 Level 2 & Level 3 (Components) | Khi `products` ngừng hoạt động, `orders` vẫn phục vụ đọc đơn cũ (HTTP 200). Thao tác tạo đơn mới trả về lỗi 503 có kiểm soát trong 3s/8s. |
| **Idempotent Consumer** | C4 Level 3 (Orders Components) | Component `Idempotency Controller` dùng SHA-256 hash và unique key trong DB để đảm bảo an toàn khi client retry hoặc gửi trùng lặp. |
| **Local Transaction Atomicity** | C4 Level 3 (Orders Transaction Manager) | Sử dụng transaction nội bộ trong phạm vi `orders-db` (ghi `orders` và các `order_items`). Tự động ROLLBACK sạch sẽ nếu có lỗi phát sinh. |
