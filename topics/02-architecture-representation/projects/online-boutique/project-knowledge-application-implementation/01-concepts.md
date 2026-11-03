# 01. Nền tảng Biểu diễn Kiến trúc: 4+1 View Model, C4 Model & Data Model — Online Boutique

Tài liệu này tái dựng đầy đủ kiến trúc của hệ thống mã nguồn mở **Google Online Boutique (`microservices-demo`, phiên bản `v0.10.7`, commit `38e7348eb289eb5b87c0c6e8cb19ced0449dc389`)** theo tiêu chuẩn của **Mục 5 — Thế Anh (`docs/TEAM-ASSIGNMENT.md`)** và **Mục 4 (`docs/INVENTORY.md`)**.

---

## Phần 0: Stakeholder Matrix & Phân biệt View — Model — Notation — C4 Zoom Level

### 0.1. Phân biệt cốt lõi trong Biểu diễn Kiến trúc
1. **Architecture View (Góc nhìn kiến trúc):** Tập hợp các phần tử kiến trúc và quan hệ giữa chúng được chọn lọc để giải quyết một nhóm **mối quan tâm (Concerns)** cụ thể của một số **bên liên quan (Stakeholders)**.
2. **Model vs. Notation (Mô hình vs. Ký pháp):**
   - **4 UML Diagrams KHÔNG đồng nghĩa với 4 Views:** Việc vẽ một Class Diagram, Sequence Diagram, Package Diagram và Deployment Diagram không tự động tạo thành 4+1 Views nếu không chỉ rõ mối quan tâm kiến trúc (boundary, state ownership, runtime failure, network isolation).
   - **Boxes and Arrows + 4+1 Views + C4 Zoom Levels:** Trong tài liệu này, chúng ta dùng **4+1 View Model (Kruchten)** làm khung trục chính để tách bạch 5 mối quan tâm, kết hợp với **C4 Model (Simon Brown)** làm 4 cấp độ phóng đại (Zoom Levels: Context $\rightarrow$ Container $\rightarrow$ Component $\rightarrow$ Code), và bổ sung **Data Model / Security & Concurrency View**.

### 0.2. Bảng Ma trận Stakeholder & Concern (Stakeholder/Concern Matrix)

| Stakeholder (Bên liên quan) | Mối quan tâm chính (Concerns) | View giải quyết chính | Minh chứng cụ thể trong Online Boutique |
| :--- | :--- | :--- | :--- |
| **Customer (Khách mua hàng)** | Duyệt danh mục nhanh, đổi tiền tệ chính xác, giỏ hàng giữ được sản phẩm theo phiên, thanh toán mượt mà. | **Scenarios (+1)** & **Logical View** | Cookie `shop_session-id` (`src/frontend/middleware.go`), `PlaceOrder()` trả về `OrderResult` kèm mã vận đơn `shipping_tracking_id`. |
| **Software Architect / Tech Lead** | Phân ranh giới 11 dịch vụ, hợp đồng giao tiếp đa ngôn ngữ, luồng điều phối (Orchestration), khả năng chịu lỗi khi dịch vụ phụ trợ chết. | **Logical View**, **Process View**, **C4 Level 2 & 3** | Hợp đồng `protos/demo.proto` (`package hipstershop`), `checkoutservice` làm Orchestrator, `frontend` bỏ qua lỗi của `recommendationservice` và `adservice`. |
| **Developer (Backend / Polyglot Dev)** | Tổ chức mã nguồn theo 5 ngôn ngữ, cách sinh mã gRPC (codegen) từ file `.proto`, cấu trúc build Docker. | **Development View**, **C4 Level 3 & 4** | 11 thư mục độc lập trong `src/`, các script `genproto.sh`, multi-stage `Dockerfile` cho Go, C#, Node.js, Python, Java. |
| **DevOps / SRE / Operator** | Cấu hình Pod, Deployment, Service, cổng mạng, biến môi trường, health probes, giới hạn CPU/RAM và bảo mật container. | **Physical / Deployment View**, **Security View** | `release/kubernetes-manifests.yaml`: 11 Deployments + 1 Redis Deployment, `grpc` readiness/liveness probes, `securityContext` (`runAsNonRoot: true`, `readOnlyRootFilesystem: true`). |
| **Data Engineer / QA** | Trạng thái lưu ở đâu, cấu trúc dữ liệu nhị phân Protobuf trong Redis, dữ liệu tĩnh JSON và hành vi khi truy cập đồng thời. | **Data Model / Schema**, **Concurrency View** | `RedisCartStore.cs` lưu `userId -> Cart.ToByteArray()`, `products.json` (9 sản phẩm), `currency_conversion.json` (tỷ giá ECB). |

---

## Phần 1: Mô hình 4+1 Góc nhìn Kiến trúc (Kruchten's 4+1 View Model)

```mermaid
flowchart TB
    subgraph FourPlusOne["Mô hình 4+1 View (Kruchten) áp dụng cho Online Boutique"]
        LV["1. Logical View<br/>(10 Microservices nghiệp vụ + Redis<br/>Thực thi vs. Mock, Domain Ownership)"]
        DV["2. Development View<br/>(5 Ngôn ngữ: Go, C#, Node, Python, Java<br/>protos/demo.proto & Multi-stage Docker)"]
        PV["3. Process View<br/>(HTTP/1.1 ở Frontend -> gRPC HTTP/2 nội bộ<br/>Orchestration PlaceOrder & Error Handling)"]
        PhV["4. Physical / Deployment View<br/>(Kubernetes: 12 Deployments, 12 Services<br/>ClusterIP vs. LoadBalancer, Probes & Limits)"]
        SC["+1. Scenarios (Use Cases)<br/>(S1: Browse, S2: Add-to-Cart, S3: Checkout,<br/>S4: Lỗi Recommendation vs. Lỗi Redis/Catalog)"]
    end

    LV --- SC
    DV --- SC
    PV --- SC
    PhV --- SC
```

---

### 1.1. Logical View (Góc nhìn Logic)

**Mối quan tâm:** Hệ thống bao gồm những dịch vụ nghiệp vụ nào? Trách nhiệm, hợp đồng giao tiếp (gRPC Contract), quyền sở hữu dữ liệu (Data Ownership) của từng dịch vụ là gì? Dịch vụ nào xử lý trạng thái thật và dịch vụ nào là mô phỏng (Mock/Stateless)?

#### Sơ đồ Logical View
```mermaid
flowchart LR
    subgraph ClientLayer["Lớp Giao diện Người dùng"]
        Browser["Trình duyệt Web<br/>(Cookie: shop_session-id)"]
        LoadGen["Load Generator<br/>(Locust Traffic Simulator)"]
    end

    subgraph EdgeLayer["Lớp Cổng Giao tiếp (HTTP -> gRPC)"]
        FE["Frontend Service (Go)<br/>HTTP Server :8080<br/>Render HTML Templates"]
    end

    subgraph CoreDomain["Các Dịch vụ Nghiệp vụ Cốt lõi (Thực thi thật)"]
        Cat["ProductCatalogService (Go)<br/>ListProducts / GetProduct / SearchProducts"]
        Cart["CartService (C# .NET)<br/>AddItem / GetCart / EmptyCart"]
        Curr["CurrencyService (Node.js)<br/>GetSupportedCurrencies / Convert"]
        Chk["CheckoutService (Go)<br/>Orchestrator: PlaceOrder"]
        Rec["RecommendationService (Python)<br/>ListRecommendations (Lọc & lấy mẫu ngẫu nhiên)"]
        Ad["AdService (Java)<br/>GetAds (Tra cứu theo Category)"]
    end

    subgraph MockDomain["Các Dịch vụ Tích hợp Mô phỏng (Mock / Stateless)"]
        Pay["PaymentService (Node.js)<br/>Charge (Validate thẻ VISA/MasterCard -> UUID)"]
        Ship["ShippingService (Go)<br/>GetQuote / ShipOrder (Tính phí theo số lượng -> Tracking ID)"]
        Email["EmailService (Python)<br/>DummyEmailService: SendOrderConfirmation (Chỉ ghi log)"]
    end

    subgraph DataLayer["Lớp Lưu trữ Trạng thái"]
        Redis[("redis-cart (Redis Alpine)<br/>Key: user_id -> Value: Protobuf Cart")]
        ProdJSON[("products.json<br/>(In-memory 9 sản phẩm)")]
        CurrJSON[("currency_conversion.json<br/>(Tỷ giá ECB tĩnh)")]
    end

    Browser -->|"HTTP/1.1 GET/POST"| FE
    LoadGen -->|"HTTP/1.1 Traffic"| FE

    FE -->|"gRPC :3550"| Cat
    FE -->|"gRPC :7070"| Cart
    FE -->|"gRPC :7000"| Curr
    FE -->|"gRPC :5050"| Chk
    FE -->|"gRPC :8080"| Rec
    FE -->|"gRPC :9555"| Ad
    FE -->|"gRPC :50051"| Ship

    Rec -->|"gRPC :3550"| Cat

    Chk -->|"1. GetCart / 7. EmptyCart"| Cart
    Chk -->|"2. GetProduct"| Cat
    Chk -->|"3. Convert / 5. Convert"| Curr
    Chk -->|"4. GetQuote / 6. ShipOrder"| Ship
    Chk -->|"5. Charge"| Pay
    Chk -->|"8. SendOrderConfirmation"| Email

    Cart -->|"TCP :6379"| Redis
    Cat -.->|"Đọc lúc khởi động"| ProdJSON
    Curr -.->|"Đọc mỗi RPC"| CurrJSON
```

#### Phân tích chi tiết Logical View (Đối chiếu thực tế Code vs. Mock)
1. **Điểm vào duy nhất (`frontend`):** Là dịch vụ duy nhất nhận HTTP/1.1 từ trình duyệt (`GET /`, `GET /product/{id}`, `POST /cart`, `GET /cart`, `POST /cart/checkout`). `frontend` không chứa logic tính giá hay lưu trữ mà đóng vai trò **API Gateway / BFF (Backend-for-Frontend)** gọi gRPC tới 7 dịch vụ nội bộ và render HTML bằng `html/template`.
2. **Dịch vụ điều phối trung tâm (`checkoutservice`):** Đóng vai trò **Synchronous Orchestrator** cho nghiệp vụ đặt hàng (`PlaceOrder`). Nó không có database riêng mà điều phối tuần tự 6 dịch vụ khác (`cartservice`, `productcatalogservice`, `currencyservice`, `shippingservice`, `paymentservice`, `emailservice`).
3. **Phân biệt rõ Dịch vụ Thật vs. Dịch vụ Mock (Yêu cầu bắt buộc trong `TEAM-ASSIGNMENT.md` dòng 63):**
   - **Có lưu trữ / xử lý dữ liệu thật:**
     - `cartservice` (`C#`): Đọc/ghi trạng thái giỏ hàng thật vào `redis-cart` qua giao thức Redis TCP cổng `6379`.
     - `productcatalogservice` (`Go`): Đọc danh mục 9 sản phẩm từ `products.json`, thực hiện tìm kiếm chuỗi (`strings.Contains`) và tra cứu theo ID thật.
     - `currencyservice` (`Node.js`): Chuyển đổi tiền tệ toán học chính xác (`units` và `nanos`) dựa trên bảng tỷ giá Châu Âu (`currency_conversion.json`).
     - `recommendationservice` (`Python`): Gọi gRPC sang `productcatalogservice` lấy toàn bộ danh sách sản phẩm, loại trừ các sản phẩm đang có trong giỏ/trang hiện tại và lấy mẫu ngẫu nhiên tối đa 5 sản phẩm (`random.sample` tại `recommendation_server.py:79`).
     - `adservice` (`Java`): Lưu `ImmutableListMultimap<String, Ad>` trong bộ nhớ (`AdService.java:121`), trả về quảng cáo khớp với từ khóa danh mục (`context_keys`) hoặc chọn ngẫu nhiên 2 quảng cáo.
   - **Dịch vụ Mô phỏng (Mock / Stateless — không gọi cổng thanh toán, hãng vận chuyển hay SMTP thật):**
     - `paymentservice` (`Node.js`): Kiểm tra định dạng số thẻ bằng `simple-card-validator`, chỉ chấp nhận thẻ **VISA** hoặc **MasterCard** còn hạn (`charge.js:74-80`), sau đó sinh ngẫu nhiên `uuidv4()` làm `transaction_id` và ghi log — **không trừ tiền thật**.
     - `shippingservice` (`Go`): Tính phí vận chuyển giả lập theo công thức số lượng mặt hàng (`quote.go`) và sinh mã vận đơn `tracking_id` giả lập dạng chữ cái + số (`tracker.go`) — **không lưu vận đơn vào DB**.
     - `emailservice` (`Python`): Chạy ở chế độ `DummyEmailService` (`email_server.py:108-119`), khi nhận RPC `SendOrderConfirmation` chỉ ghi log `A request to send order confirmation email to ... has been received` — **không kết nối máy chủ SMTP**.

---

### 1.2. Development View (Góc nhìn Phát triển)

**Mối quan tâm:** Mã nguồn được tổ chức như thế nào? Làm sao 5 ngôn ngữ lập trình khác nhau (Go, C#, Node.js, Python, Java) có thể giao tiếp đồng nhất? Quy trình sinh mã (Codegen) và đóng gói Docker image diễn ra ra sao?

#### Sơ đồ Development View (Cấu trúc Polyglot & Hợp đồng Protobuf)
```mermaid
flowchart TB
    subgraph Contract["Hợp đồng Giao tiếp Trung tâm (Single Source of Truth)"]
        Proto["protos/demo.proto<br/>(package hipstershop: 9 gRPC Services, 29 Messages)"]
    end

    subgraph GoServices["Nhóm Ngôn ngữ Go (Static Binary, Multi-stage golang -> alpine)"]
        FE_Src["src/frontend/<br/>main.go, handlers.go, rpc.go<br/>genproto/demo.pb.go"]
        Cat_Src["src/productcatalogservice/<br/>server.go, product_catalog.go<br/>products.json, genproto/"]
        Chk_Src["src/checkoutservice/<br/>main.go, money/money.go<br/>genproto/demo.pb.go"]
        Ship_Src["src/shippingservice/<br/>main.go, quote.go, tracker.go<br/>genproto/demo.pb.go"]
    end

    subgraph DotNetServices["Nhóm C# / .NET 8 (Grpc.AspNetCore)"]
        Cart_Src["src/cartservice/src/<br/>Program.cs, Startup.cs<br/>services/CartService.cs<br/>cartstore/RedisCartStore.cs<br/>protos/Cart.proto"]
    end

    subgraph NodeServices["Nhóm Node.js (@grpc/grpc-js + @grpc/proto-loader)"]
        Curr_Src["src/currencyservice/<br/>server.js, data/currency_conversion.json<br/>proto/demo.proto (Dynamic Load)"]
        Pay_Src["src/paymentservice/<br/>index.js, server.js, charge.js<br/>proto/demo.proto (Dynamic Load)"]
    end

    subgraph PythonServices["Nhóm Python 3 (grpcio-tools -> demo_pb2.py)"]
        Email_Src["src/emailservice/<br/>email_server.py, templates/confirmation.html<br/>demo_pb2.py, demo_pb2_grpc.py"]
        Rec_Src["src/recommendationservice/<br/>recommendation_server.py<br/>demo_pb2.py, demo_pb2_grpc.py"]
        Load_Src["src/loadgenerator/<br/>locustfile.py (HTTP Client)"]
    end

    subgraph JavaServices["Nhóm Java (Gradle + protobuf-gradle-plugin)"]
        Ad_Src["src/adservice/<br/>build.gradle, src/main/java/hipstershop/AdService.java<br/>src/main/proto/demo.proto"]
    end

    Proto -->|"protoc --go_out / --go-grpc_out"| GoServices
    Proto -->|"Grpc.Tools MSBuild Compile"| Cart_Src
    Proto -->|"Runtime protoLoader.loadSync()"| NodeServices
    Proto -->|"python -m grpc_tools.protoc"| PythonServices
    Proto -->|"Gradle generateProto task"| Ad_Src
```

#### Bảng Ánh xạ Cấu trúc Mã nguồn & Cơ chế Build (`src/*`)

| Thư mục Mã nguồn | Ngôn ngữ / Runtime | Cơ chế dùng Protobuf (`demo.proto`) | Quản lý Dependency | Cấu trúc `Dockerfile` |
| :--- | :--- | :--- | :--- | :--- |
| `src/frontend/` | Go (`1.23+`) | Biên dịch trước ra `genproto/demo.pb.go` & `demo_grpc.pb.go` (`genproto.sh`) | `go.mod` / `go.sum` | Multi-stage: `golang:alpine` (`go build -o /go/bin/frontend`) $\rightarrow$ `alpine` kèm `templates/` & `static/` |
| `src/checkoutservice/` | Go (`1.23+`) | Biên dịch trước ra `genproto/demo.pb.go` | `go.mod` / `go.sum` | Multi-stage: `golang:alpine` $\rightarrow$ `alpine` (chỉ chứa 1 file thực thi `/src/checkoutservice`) |
| `src/productcatalogservice/` | Go (`1.23+`) | Biên dịch trước ra `genproto/demo.pb.go` | `go.mod` / `go.sum` | Multi-stage: `golang:alpine` $\rightarrow$ `alpine` kèm `/src/products.json` |
| `src/shippingservice/` | Go (`1.23+`) | Biên dịch trước ra `genproto/demo.pb.go` | `go.mod` / `go.sum` | Multi-stage: `golang:alpine` $\rightarrow$ `alpine` (`/src/shippingservice`) |
| `src/cartservice/src/` | C# / .NET | `cartservice.csproj` dùng `<Protobuf Include="protos\Cart.proto" GrpcServices="Both" />` sinh code lúc build | `cartservice.csproj` (NuGet) | Multi-stage: `mcr.microsoft.com/dotnet/sdk` (`dotnet publish`) $\rightarrow$ `dotnet/aspnet` |
| `src/currencyservice/` | Node.js | Nạp động lúc khởi chạy bằng `@grpc/proto-loader` (`server.js:91-103`) | `package.json` (npm) | Multi-stage: `node:alpine` cài native deps $\rightarrow$ copy `node_modules`, `server.js`, `data/`, `proto/` |
| `src/paymentservice/` | Node.js | Nạp động lúc khởi chạy bằng `@grpc/proto-loader` (`server.js:55-67`) | `package.json` (npm) | Multi-stage: `node:alpine` $\rightarrow$ copy `index.js`, `server.js`, `charge.js`, `proto/` |
| `src/recommendationservice/` | Python 3 | Sinh tĩnh `demo_pb2.py` & `demo_pb2_grpc.py` bằng `grpc_tools.protoc` | `requirements.txt` (pip) | Multi-stage: `python:slim` cài wheel $\rightarrow$ chạy `python recommendation_server.py` |
| `src/emailservice/` | Python 3 | Sinh tĩnh `demo_pb2.py` & `demo_pb2_grpc.py` | `requirements.txt` (pip) | Multi-stage: `python:slim` $\rightarrow$ chạy `python email_server.py` kèm `templates/` |
| `src/adservice/` | Java (`JDK 21`) | Gradle plugin `com.google.protobuf` sinh class `hipstershop.Demo` & `AdServiceGrpc` lúc build | `build.gradle` (Gradle) | Multi-stage: `eclipse-temurin` (`./gradlew installDist`) $\rightarrow$ runtime image chạy `/app/bin/AdService` |
| `src/loadgenerator/` | Python 3 (Locust) | Không dùng gRPC; gửi HTTP/1.1 trực tiếp tới `frontend` | `requirements.txt` | Image chứa `locustfile.py`, chạy `locust --host="http://${FRONTEND_ADDR}" --headless` |

> **Đặc trưng kiến trúc Development View:** Các microservice hoàn toàn **Share-Nothing về mặt mã nguồn thư viện** (ngay cả các dịch vụ cùng viết bằng Go như `frontend` và `checkoutservice` cũng có bản copy package `money/` riêng, được ghi chú rõ tại comment `src/checkoutservice/main.go:181-182`: *"this method is duplicated in other microservices using Go since they are not sharing packages"*). Điều này giúp mỗi dịch vụ có thể build, nâng cấp thư viện và deploy hoàn toàn độc lập, chỉ ràng buộc duy nhất qua hợp đồng `protos/demo.proto`.

---

### 1.3. Process View (Góc nhìn Tiến trình & Luồng Thời gian chạy)

**Mối quan tâm:** Ở thời điểm runtime, một thao tác của người dùng kích hoạt những lời gọi RPC nào? Thứ tự tuần tự ra sao? Dịch vụ nào giữ kết nối lâu dài (persistent gRPC channel)? Khi một dịch vụ con bị lỗi thì tiến trình xử lý và trả lỗi như thế nào?

#### Sequence 1: Luồng Duyệt Trang chủ & Xem Chi tiết Sản phẩm (`Browse Flow`)
```mermaid
sequenceDiagram
    autonumber
    actor User as Trình duyệt (User)
    participant FE as frontend (:8080)<br/>[handlers.go]
    participant Curr as currencyservice (:7000)<br/>[server.js]
    participant Cat as productcatalogservice (:3550)<br/>[product_catalog.go]
    participant Cart as cartservice (:7070)<br/>[CartService.cs]
    participant Redis as redis-cart (:6379)
    participant Rec as recommendationservice (:8080)<br/>[recommendation_server.py]
    participant Ad as adservice (:9555)<br/>[AdService.java]

    User->>FE: GET /product/OLJCESPC7Z (Cookie: shop_session-id)
    Note over FE: ensureSessionID() kiểm tra/gắn UUID vào cookie
    FE->>Cat: gRPC GetProduct(id="OLJCESPC7Z")
    Cat-->>FE: Product {id, name, price_usd: 19.99 USD, categories: ["accessories"]}
    FE->>Curr: gRPC GetSupportedCurrencies(Empty)
    Curr-->>FE: ["EUR", "USD", "JPY", "GBP", ...]
    FE->>Cart: gRPC GetCart(user_id=session_id)
    Cart->>Redis: GET <session_id>
    Redis-->>Cart: Protobuf bytes (hoặc nil)
    Cart-->>FE: Cart {user_id, items[]}
    FE->>Curr: gRPC Convert(from=19.99 USD, to_code=currentCurrency)
    Curr-->>FE: Money {currency_code, units, nanos}
    FE->>Rec: gRPC ListRecommendations(user_id, product_ids=["OLJCESPC7Z"])
    Rec->>Cat: gRPC ListProducts(Empty)
    Cat-->>Rec: ListProductsResponse (9 products)
    Rec-->>FE: ListRecommendationsResponse (tối đa 5 product_ids)
    Note over FE: Nếu Rec lỗi -> chỉ log.Warn(), KHÔNG làm hỏng trang!
    FE->>Ad: gRPC GetAds(context_keys=["accessories"])
    Ad-->>FE: AdResponse (1-2 Ads)
    Note over FE: Nếu Ad lỗi -> chỉ log.Warn(), KHÔNG làm hỏng trang!
    FE-->>User: HTTP 200 OK (Render HTML template "product")
```

#### Sequence 2: Luồng Thêm vào Giỏ hàng (`Add-to-Cart Flow`)
```mermaid
sequenceDiagram
    autonumber
    actor User as Trình duyệt (User)
    participant FE as frontend (:8080)<br/>[addToCartHandler]
    participant Cat as productcatalogservice (:3550)<br/>[GetProduct]
    participant Cart as cartservice (:7070)<br/>[AddItemAsync]
    participant Redis as redis-cart (:6379)

    User->>FE: POST /cart (product_id="OLJCESPC7Z", quantity=2)
    Note over FE: validator.AddToCartPayload.Validate() (quantity 1..10)
    FE->>Cat: gRPC GetProduct(id="OLJCESPC7Z")
    Cat-->>FE: Product (xác nhận product_id hợp lệ)
    FE->>Cart: gRPC AddItem(user_id=session_id, item={product_id, quantity=2})
    Cart->>Redis: _cache.GetAsync(userId)
    Redis-->>Cart: byte[] (Protobuf Cart hiện tại hoặc null)
    Note over Cart: Parse Protobuf -> Nếu đã có product_id thì cộng dồn Quantity,<br/>nếu chưa có thì thêm CartItem mới -> cart.ToByteArray()
    Cart->>Redis: _cache.SetAsync(userId, byte[])
    Redis-->>Cart: OK
    Cart-->>FE: Empty {}
    FE-->>User: HTTP 302 Found (Location: /cart)
```

#### Sequence 3: Luồng Đặt hàng — Điều phối Tập trung (`Checkout Orchestration Flow — PlaceOrder`)
```mermaid
sequenceDiagram
    autonumber
    actor User as Trình duyệt (User)
    participant FE as frontend (:8080)<br/>[placeOrderHandler]
    participant Chk as checkoutservice (:5050)<br/>[PlaceOrder]
    participant Cart as cartservice (:7070)
    participant Cat as productcatalogservice (:3550)
    participant Curr as currencyservice (:7000)
    participant Ship as shippingservice (:50051)
    participant Pay as paymentservice (:50051)
    participant Email as emailservice (:5000->8080)

    User->>FE: POST /cart/checkout (email, address, credit_card)
    Note over FE: validator.PlaceOrderPayload.Validate()
    FE->>Chk: gRPC PlaceOrder(PlaceOrderRequest)
    Note over Chk: 1. Sinh orderID = uuid.NewUUID() (main.go:233)
    Chk->>Cart: 2. gRPC GetCart(user_id)
    Cart-->>Chk: Cart {items[]}
    loop 3. Với mỗi CartItem trong giỏ (prepOrderItems - main.go:343)
        Chk->>Cat: gRPC GetProduct(id=item.product_id)
        Cat-->>Chk: Product {price_usd}
        Chk->>Curr: gRPC Convert(from=price_usd, to=user_currency)
        Curr-->>Chk: Money (Đơn giá đã quy đổi)
    end
    Chk->>Ship: 4. gRPC GetQuote(address, cartItems)
    Ship-->>Chk: GetQuoteResponse {cost_usd}
    Chk->>Curr: 5. gRPC Convert(from=cost_usd, to=user_currency)
    Curr-->>Chk: shippingCostLocalized
    Note over Chk: 6. Cộng tổng tiền = Shipping + Sum(Item.Cost * Quantity) (main.go:246-250)
    Chk->>Pay: 7. gRPC Charge(amount=total, credit_card)
    Pay-->>Chk: ChargeResponse {transaction_id}
    Chk->>Ship: 8. gRPC ShipOrder(address, cartItems)
    Ship-->>Chk: ShipOrderResponse {tracking_id}
    Chk->>Cart: 9. gRPC EmptyCart(user_id) (main.go:263 - bỏ qua lỗi nếu có)
    Cart-->>Chk: Empty {}
    Chk->>Email: 10. gRPC SendOrderConfirmation(email, orderResult)
    Email-->>Chk: Empty {} (Nếu lỗi chỉ log.Warnf - main.go:273)
    Chk-->>FE: PlaceOrderResponse {Order: orderResult}
    FE-->>User: HTTP 200 OK (Render trang xác nhận đơn hàng "order")
```

---

### 1.4. Physical / Deployment View (Góc nhìn Vật lý & Triển khai Kubernetes)

**Mối quan tâm:** Mã nguồn sau khi đóng gói thành Container Image được triển khai lên cụm Kubernetes như thế nào? Có bao nhiêu `Deployment`, `Pod`, `Service`, `ServiceAccount`? Dịch vụ nào public ra ngoài, dịch vụ nào chỉ giao tiếp nội bộ (`ClusterIP`)? Giới hạn tài nguyên (`requests`/`limits`) và cơ chế kiểm tra sức khỏe (`readinessProbe`/`livenessProbe`) được cấu hình ra sao?

#### Sơ đồ Physical / Deployment View (Dựa trên `release/kubernetes-manifests.yaml`)
```mermaid
flowchart TB
    subgraph External["Bên ngoài Cụm Kubernetes"]
        UserBrowser["Trình duyệt Người dùng<br/>(http://localhost:8080 hoặc LoadBalancer IP:80)"]
    end

    subgraph K8sCluster["Kubernetes Cluster (Namespace mặc định / theanh-architecture)"]
        subgraph IngressSvc["Public Entrypoint Service"]
            FE_Ext["Service: frontend-external<br/>(type: LoadBalancer, port: 80 -> targetPort: 8080)"]
            FE_Int["Service: frontend<br/>(type: ClusterIP, port: 80 -> targetPort: 8080)"]
        end

        subgraph EdgeWorkloads["Edge & Traffic Workloads"]
            FE_Pod["Deployment: frontend<br/>Pod: frontend (Go :8080)<br/>CPU: 100m-200m | Mem: 64Mi-128Mi"]
            LG_Pod["Deployment: loadgenerator<br/>InitContainer: busybox wget frontend:80<br/>Pod: loadgenerator (Locust USERS=10)"]
        end

        subgraph InternalGrpcServices["Internal gRPC Services (type: ClusterIP)"]
            Cat_Pod["Deployment & Service: productcatalogservice<br/>Port: 3550 (Go)<br/>CPU: 100m-200m | Mem: 64Mi-128Mi"]
            Cart_Pod["Deployment & Service: cartservice<br/>Port: 7070 (C# .NET)<br/>CPU: 200m-300m | Mem: 64Mi-128Mi"]
            Curr_Pod["Deployment & Service: currencyservice<br/>Port: 7000 (Node.js)<br/>CPU: 100m-200m | Mem: 64Mi-128Mi"]
            Chk_Pod["Deployment & Service: checkoutservice<br/>Port: 5050 (Go)<br/>CPU: 100m-200m | Mem: 64Mi-128Mi"]
            Pay_Pod["Deployment & Service: paymentservice<br/>Port: 50051 (Node.js)<br/>CPU: 100m-200m | Mem: 64Mi-128Mi"]
            Ship_Pod["Deployment & Service: shippingservice<br/>Port: 50051 (Go)<br/>CPU: 100m-200m | Mem: 64Mi-128Mi"]
            Email_Pod["Deployment & Service: emailservice<br/>Svc Port: 5000 -> Pod Port: 8080 (Python)<br/>CPU: 100m-200m | Mem: 64Mi-128Mi"]
            Rec_Pod["Deployment & Service: recommendationservice<br/>Port: 8080 (Python)<br/>CPU: 100m-200m | Mem: 220Mi-450Mi"]
            Ad_Pod["Deployment & Service: adservice<br/>Port: 9555 (Java)<br/>CPU: 200m-300m | Mem: 180Mi-300Mi"]
        end

        subgraph StatefulWorkload["Stateful Backing Store"]
            Redis_Pod["Deployment & Service: redis-cart<br/>Port: 6379 (redis:alpine)<br/>Volume: redis-data (emptyDir: {})<br/>CPU: 70m-125m | Mem: 200Mi-256Mi"]
        end
    end

    UserBrowser -->|"HTTP :80 / port-forward :8080"| FE_Ext
    FE_Ext --> FE_Pod
    LG_Pod -->|"HTTP frontend:80"| FE_Int
    FE_Int --> FE_Pod

    FE_Pod -->|"gRPC DNS Nội bộ"| Cat_Pod
    FE_Pod -->|"gRPC DNS Nội bộ"| Cart_Pod
    FE_Pod -->|"gRPC DNS Nội bộ"| Curr_Pod
    FE_Pod -->|"gRPC DNS Nội bộ"| Chk_Pod
    FE_Pod -->|"gRPC DNS Nội bộ"| Ship_Pod
    FE_Pod -->|"gRPC DNS Nội bộ"| Rec_Pod
    FE_Pod -->|"gRPC DNS Nội bộ"| Ad_Pod

    Rec_Pod -->|"gRPC :3550"| Cat_Pod
    Chk_Pod -->|"gRPC"| Cart_Pod
    Chk_Pod -->|"gRPC"| Cat_Pod
    Chk_Pod -->|"gRPC"| Curr_Pod
    Chk_Pod -->|"gRPC"| Ship_Pod
    Chk_Pod -->|"gRPC"| Pay_Pod
    Chk_Pod -->|"gRPC"| Email_Pod

    Cart_Pod -->|"TCP :6379"| Redis_Pod
```

#### Bảng Tổng hợp Thông số Triển khai Kubernetes (`release/kubernetes-manifests.yaml`)

| Workload (`Deployment`) | Kubernetes `Service` | Loại Service | Service Port $\rightarrow$ Target Port | Health Probes (`readiness` / `liveness`) | CPU (`req` / `lim`) | Memory (`req` / `lim`) | Lưu trữ / Volume |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `frontend` | `frontend` & `frontend-external` | `ClusterIP` & `LoadBalancer` | `80 -> 8080` | `httpGet /_healthz:8080` (kèm Cookie probe) | `100m / 200m` | `64Mi / 128Mi` | Không (`readOnlyRootFilesystem: true`) |
| `checkoutservice` | `checkoutservice` | `ClusterIP` | `5050 -> 5050` | Native `grpc` probe port `5050` | `100m / 200m` | `64Mi / 128Mi` | Không (`readOnlyRootFilesystem: true`) |
| `productcatalogservice` | `productcatalogservice` | `ClusterIP` | `3550 -> 3550` | Native `grpc` probe port `3550` | `100m / 200m` | `64Mi / 128Mi` | Không (JSON đóng gói sẵn trong image) |
| `cartservice` | `cartservice` | `ClusterIP` | `7070 -> 7070` | Native `grpc` probe port `7070` (delay 15s) | `200m / 300m` | `64Mi / 128Mi` | Không (`readOnlyRootFilesystem: true`) |
| `redis-cart` | `redis-cart` | `ClusterIP` | `6379 -> 6379` | `tcpSocket` port `6379` (period 5s) | `70m / 125m` | `200Mi / 256Mi` | `mountPath: /data` $\rightarrow$ `emptyDir: {}` |
| `currencyservice` | `currencyservice` | `ClusterIP` | `7000 -> 7000` | Native `grpc` probe port `7000` | `100m / 200m` | `64Mi / 128Mi` | Không (JSON đóng gói sẵn trong image) |
| `paymentservice` | `paymentservice` | `ClusterIP` | `50051 -> 50051` | Native `grpc` probe port `50051` | `100m / 200m` | `64Mi / 128Mi` | Không (`readOnlyRootFilesystem: true`) |
| `shippingservice` | `shippingservice` | `ClusterIP` | `50051 -> 50051` | Native `grpc` probe port `50051` | `100m / 200m` | `64Mi / 128Mi` | Không (`readOnlyRootFilesystem: true`) |
| `emailservice` | `emailservice` | `ClusterIP` | **`5000 -> 8080`** | Native `grpc` probe port `8080` | `100m / 200m` | `64Mi / 128Mi` | Không (`readOnlyRootFilesystem: true`) |
| `recommendationservice` | `recommendationservice` | `ClusterIP` | `8080 -> 8080` | Native `grpc` probe port `8080` | `100m / 200m` | `220Mi / 450Mi` | Không (`readOnlyRootFilesystem: true`) |
| `adservice` | `adservice` | `ClusterIP` | `9555 -> 9555` | Native `grpc` probe port `9555` (delay 20s) | `200m / 300m` | `180Mi / 300Mi` | Không (`readOnlyRootFilesystem: true`) |
| `loadgenerator` | *(Không có Service)* | Headless Client | Gọi `frontend:80` | `initContainer: frontend-check` (retry 12 lần) | `300m / 500m` | `256Mi / 512Mi` | Không (`readOnlyRootFilesystem: true`) |

> **Điểm đáng chú ý trong Deployment View:**
> 1. **Ánh xạ cổng khác biệt ở `emailservice`:** Container `emailservice` lắng nghe ở cổng `8080` (`containerPort: 8080`), nhưng Kubernetes `Service` của nó mở cổng `5000` (`port: 5000 -> targetPort: 8080` tại `kubernetes-manifests.yaml:391-393`). Do đó, biến môi trường ở `checkoutservice` được cấu hình là `EMAIL_SERVICE_ADDR: "emailservice:5000"`.
> 2. **Volume của `redis-cart` là `emptyDir: {}` (`kubernetes-manifests.yaml:889-891`):** Dữ liệu giỏ hàng tồn tại trong suốt vòng đời của Pod `redis-cart`, nhưng nếu Pod `redis-cart` bị xóa và tạo lại trên Node khác, `emptyDir` sẽ được khởi tạo mới (trống).

---

### 1.5. Scenarios View (`+1` — Các Kịch bản Kết nối 4 Views)

| Mã Kịch bản | Tên Kịch bản | Logical View | Development View | Process View | Physical / Deployment View |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S1** | **Duyệt danh mục & Đổi tiền tệ** (`GET /`, `POST /setCurrency`) | `frontend` $\rightarrow$ `productcatalog`, `currency`, `cart`, `ad` | `handlers.go:homeHandler` gọi `rpc.go` qua stub `genproto` | Gọi đồng bộ `ListProducts`, `GetCart`, và lặp `Convert` cho 9 sản phẩm | `frontend` Pod gọi DNS `productcatalogservice:3550`, `currencyservice:7000` |
| **S2** | **Thêm sản phẩm vào giỏ hàng** (`POST /cart`) | `frontend` $\rightarrow$ `productcatalog` $\rightarrow$ `cartservice` $\rightarrow$ `redis-cart` | `handlers.go:addToCartHandler` $\rightarrow$ `CartService.cs` $\rightarrow$ `RedisCartStore.cs` | Kiểm tra SP tồn tại $\rightarrow$ `AddItem` $\rightarrow$ `GetAsync` + `SetAsync` trong Redis $\rightarrow$ Redirect `302 /cart` | `cartservice:7070` đọc/ghi TCP vào `redis-cart:6379` (Volume `emptyDir`) |
| **S3** | **Đặt hàng thành công** (`POST /cart/checkout`) | `frontend` $\rightarrow$ `checkoutservice` điều phối 6 dịch vụ con | `checkoutservice/main.go:PlaceOrder` + package `money` tính tổng tiền | 10 bước RPC tuần tự: `GetCart` $\rightarrow$ `GetProduct` $\rightarrow$ `Convert` $\rightarrow$ `GetQuote` $\rightarrow$ `Charge` $\rightarrow$ `ShipOrder` $\rightarrow$ `EmptyCart` $\rightarrow$ `SendOrderConfirmation` | `checkoutservice:5050` kết nối gRPC tới 6 ClusterIP Services trong cụm |
| **S4** | **Chịu lỗi: Dịch vụ phụ trợ chết vs. Dịch vụ cốt lõi chết** (`Failure & Recovery`) | Phân biệt Non-critical (`ad`, `recommendation`, `email`) vs. Critical (`redis-cart`, `productcatalog`, `payment`) | `handlers.go:178-181` & `chooseAd` bắt lỗi trả cảnh báo; `RedisCartStore.cs:62-65` ném `RpcException(FailedPrecondition)` | Nếu `adservice` hoặc `recommendationservice` tắt $\rightarrow$ trang sản phẩm vẫn trả `HTTP 200`. Nếu `redis-cart` hoặc `productcatalogservice` tắt $\rightarrow$ `frontend` trả `HTTP 500` | Scale `replicas: 0` cho `adservice` (hệ thống vẫn chạy) vs. scale `replicas: 0` cho `redis-cart` (giỏ hàng lỗi ngay, khôi phục khi scale lại `replicas: 1`) |

---

## Phần 2: Mô hình C4 (C4 Model — Levels 1, 2, 3, 4)

### 2.1. C4 Level 1 — System Context Diagram (Bối cảnh Hệ thống)
```mermaid
flowchart LR
    Customer(["👤 Khách mua hàng<br/>[Person]<br/>Duyệt hàng, quản lý giỏ, đặt hàng"])
    LoadUser(["🤖 Locust Load Generator<br/>[Automated Actor]<br/>Giả lập người dùng truy cập liên tục"])

    System["🛒 Hệ thống Online Boutique<br/>[Software System]<br/>Ứng dụng thương mại điện tử đa ngôn ngữ<br/>gồm 10 microservices nghiệp vụ + Redis"]

    Customer -->|"Duyệt web, thêm giỏ hàng, thanh toán<br/>[HTTP/1.1 trên cổng 80/8080]"| System
    LoadUser -->|"Gửi tải tự động (Browse, Cart, Checkout)<br/>[HTTP/1.1]"| System
```

---

### 2.2. C4 Level 2 — Container Diagram (Sơ đồ Container / Dịch vụ)
```mermaid
flowchart TB
    Customer(["👤 Khách mua hàng (Browser)"])

    subgraph Boundary["Hệ thống Online Boutique (Kubernetes Cluster)"]
        FE["frontend<br/>[Go HTTP Server :8080]<br/>Phục vụ giao diện HTML, quản lý session cookie và chuyển tiếp yêu cầu sang gRPC"]

        Cat["productcatalogservice<br/>[Go gRPC Server :3550]<br/>Cung cấp danh sách, chi tiết và tìm kiếm 9 sản phẩm từ products.json"]
        Cart["cartservice<br/>[C# .NET gRPC Server :7070]<br/>Quản lý giỏ hàng của từng session người dùng"]
        Redis[("redis-cart<br/>[Redis Alpine :6379]<br/>Lưu trữ key-value: user_id -> Protobuf Cart bytes")]

        Curr["currencyservice<br/>[Node.js gRPC Server :7000]<br/>Chuyển đổi đơn vị tiền tệ theo tỷ giá ECB"]
        Chk["checkoutservice<br/>[Go gRPC Server :5050]<br/>Điều phối quy trình đặt hàng (Orchestrator)"]

        Ship["shippingservice<br/>[Go gRPC Server :50051]<br/>Tính phí vận chuyển và tạo mã vận đơn tracking_id"]
        Pay["paymentservice<br/>[Node.js gRPC Server :50051]<br/>Kiểm tra thẻ VISA/MasterCard và sinh transaction_id"]
        Email["emailservice<br/>[Python gRPC Server :5000->8080]<br/>Render mẫu HTML và ghi log xác nhận đơn hàng"]

        Rec["recommendationservice<br/>[Python gRPC Server :8080]<br/>Đề xuất tối đa 5 sản phẩm liên quan"]
        Ad["adservice<br/>[Java gRPC Server :9555]<br/>Phục vụ quảng cáo theo ngữ cảnh danh mục"]
    end

    Customer -->|"HTTP GET/POST"| FE
    FE -->|"gRPC"| Cat
    FE -->|"gRPC"| Cart
    FE -->|"gRPC"| Curr
    FE -->|"gRPC"| Chk
    FE -->|"gRPC"| Ship
    FE -->|"gRPC"| Rec
    FE -->|"gRPC"| Ad

    Rec -->|"gRPC"| Cat
    Cart -->|"Redis TCP"| Redis

    Chk -->|"gRPC"| Cart
    Chk -->|"gRPC"| Cat
    Chk -->|"gRPC"| Curr
    Chk -->|"gRPC"| Ship
    Chk -->|"gRPC"| Pay
    Chk -->|"gRPC"| Email
```

---

### 2.3. C4 Level 3 — Component Diagram (Bên trong `frontend`, `checkoutservice` và `cartservice`)
```mermaid
flowchart TB
    subgraph FE_Container["Container: frontend (src/frontend/)"]
        FE_Main["main.go<br/>[Bootstrap & Router]<br/>Khởi tạo Gorilla Mux, kết nối 7 gRPC channels"]
        FE_Mid["middleware.go<br/>[HTTP Middleware]<br/>ensureSessionID (Cookie shop_session-id) & Logrus structured logging"]
        FE_Handlers["handlers.go<br/>[HTTP Handlers]<br/>homeHandler, productHandler, addToCartHandler, viewCartHandler, placeOrderHandler"]
        FE_Val["validator/validator.go<br/>[Input Validator]<br/>AddToCartPayload, PlaceOrderPayload, SetCurrencyPayload"]
        FE_RPC["rpc.go<br/>[gRPC Client Wrappers]<br/>getProducts, getCart, insertCart, convertCurrency, getRecommendations, chooseAd"]
        FE_Tpl["templates/*.html<br/>[HTML View Engine]<br/>home, product, cart, order, recommendations, ad"]
    end

    subgraph Chk_Container["Container: checkoutservice (src/checkoutservice/)"]
        Chk_Main["main.go:main()<br/>[gRPC Server & Client Init]<br/>Lắng nghe :5050, mustConnGRPC tới 6 dịch vụ"]
        Chk_Place["main.go:PlaceOrder()<br/>[Order Orchestrator]<br/>Điều phối luồng đặt hàng, tính tổng tiền, gom kết quả OrderResult"]
        Chk_Prep["main.go:prepareOrderItemsAndShippingQuoteFromCart()<br/>[Cart & Quote Resolver]<br/>Lấy giỏ hàng, tra giá từng SP, lấy phí ship và quy đổi tiền tệ"]
        Chk_Money["money/money.go<br/>[Exact Money Arithmetic]<br/>Sum(), MultiplySlow(), carry nanos/units"]
    end

    subgraph Cart_Container["Container: cartservice (src/cartservice/src/)"]
        Cart_Startup["Program.cs & Startup.cs<br/>[DI & Store Selection]<br/>Đọc REDIS_ADDR, đăng ký IDistributedCache & RedisCartStore"]
        Cart_Grpc["services/CartService.cs<br/>[gRPC Servicer]<br/>AddItem(), GetCart(), EmptyCart()"]
        Cart_Store["cartstore/RedisCartStore.cs<br/>[Persistence Adapter]<br/>AddItemAsync(), GetCartAsync(), EmptyCartAsync() dùng Google.Protobuf"]
    end

    FE_Main --> FE_Mid --> FE_Handlers
    FE_Handlers --> FE_Val
    FE_Handlers --> FE_RPC
    FE_Handlers --> FE_Tpl
    FE_Handlers -->|"gRPC PlaceOrder"| Chk_Place
    FE_RPC -->|"gRPC AddItem/GetCart"| Cart_Grpc

    Chk_Main --> Chk_Place
    Chk_Place --> Chk_Prep
    Chk_Place --> Chk_Money
    Chk_Prep -->|"gRPC GetCart"| Cart_Grpc
    Chk_Place -->|"gRPC EmptyCart"| Cart_Grpc

    Cart_Startup --> Cart_Grpc --> Cart_Store
```

---

### 2.4. C4 Level 4 — Code Diagram (Chi tiết cấu trúc lớp/hàm trong `checkoutservice`, `cartservice` và `protos/demo.proto`)
```mermaid
classDiagram
    class CheckoutServiceServer {
        <<Go struct: checkoutService>>
        -productCatalogSvcAddr string
        -cartSvcAddr string
        -currencySvcAddr string
        -shippingSvcAddr string
        -emailSvcAddr string
        -paymentSvcAddr string
        +PlaceOrder(ctx, *PlaceOrderRequest) (*PlaceOrderResponse, error)
        -prepareOrderItemsAndShippingQuoteFromCart(ctx, userID, userCurrency, address) (orderPrep, error)
        -prepOrderItems(ctx, []*CartItem, userCurrency) ([]*OrderItem, error)
        -quoteShipping(ctx, *Address, []*CartItem) (*Money, error)
        -chargeCard(ctx, *Money, *CreditCardInfo) (string, error)
        -shipOrder(ctx, *Address, []*CartItem) (string, error)
        -emptyUserCart(ctx, userID) error
        -sendOrderConfirmation(ctx, email, *OrderResult) error
    }

    class orderPrep {
        <<Go struct>>
        +orderItems []*OrderItem
        +cartItems []*CartItem
        +shippingCostLocalized *Money
    }

    class ICartStore {
        <<C# interface>>
        +AddItemAsync(string userId, string productId, int quantity) Task
        +EmptyCartAsync(string userId) Task
        +GetCartAsync(string userId) Task~Cart~
        +Ping() bool
    }

    class RedisCartStore {
        <<C# class>>
        -IDistributedCache _cache
        +AddItemAsync(string userId, string productId, int quantity) Task
        +EmptyCartAsync(string userId) Task
        +GetCartAsync(string userId) Task~Cart~
        +Ping() bool
    }

    class Money {
        <<Protobuf Message>>
        +string currency_code
        +int64 units
        +int32 nanos
    }

    class Cart {
        <<Protobuf Message>>
        +string user_id
        +repeated CartItem items
    }

    class OrderResult {
        <<Protobuf Message>>
        +string order_id
        +string shipping_tracking_id
        +Money shipping_cost
        +Address shipping_address
        +repeated OrderItem items
    }

    CheckoutServiceServer ..> orderPrep : creates
    CheckoutServiceServer ..> OrderResult : returns
    CheckoutServiceServer ..> Money : calculates via money.Sum/MultiplySlow
    ICartStore <|.. RedisCartStore : implements
    RedisCartStore ..> Cart : serializes/deserializes via Google.Protobuf
```

---

## Phần 3: Data Schema / Data Model (Redis, JSON Catalog & Protobuf Contracts)

> [!IMPORTANT]
> **Ghi chú trung thực theo đúng yêu cầu của `docs/TEAM-ASSIGNMENT.md` (Mục 5, dòng 68):**
> Bản chuẩn (baseline) của **Online Boutique KHÔNG sử dụng cơ sở dữ liệu quan hệ (RDBMS / SQL)** nên không có bảng SQL `CREATE TABLE`. Thay vào đó, trạng thái và mô hình dữ liệu của hệ thống được biểu diễn qua **3 lớp Schema thực tế trong code**:
> 1. **Redis Key-Value Schema (Binary Protobuf)** cho Giỏ hàng (`redis-cart`).
> 2. **JSON Document Schema** cho Danh mục sản phẩm (`products.json`) và Tỷ giá tiền tệ (`currency_conversion.json`).
> 3. **Protobuf Wire Contract Schema (`protos/demo.proto`)** định nghĩa toàn bộ cấu trúc bản tin truyền qua mạng và cấu trúc lưu trữ trong Redis.
> *(Trong tài liệu `cartservice` có hỗ trợ tùy chọn Spanner/AlloyDB/Memorystore nếu cấu hình biến môi trường GCP, nhưng ở cấu hình chuẩn `release/kubernetes-manifests.yaml` dòng 800, hệ thống chạy `REDIS_ADDR="redis-cart:6379"`).*

### 3.1. Sơ đồ Quan hệ Thực thể Logic & Lưu trữ Vật lý (Logical Data Model)
```mermaid
erDiagram
    REDIS_CART_ENTRY {
        string redis_key PK "user_id (UUID từ cookie shop_session-id)"
        bytes protobuf_value "Chuỗi byte nhị phân của message hipstershop.Cart"
    }

    PROTO_CART {
        string user_id "ID phiên người dùng"
        repeated_CartItem items "Danh sách các mặt hàng trong giỏ"
    }

    PROTO_CART_ITEM {
        string product_id FK "Mã sản phẩm (VD: OLJCESPC7Z) - Tham chiếu logic"
        int32 quantity "Số lượng cộng dồn (> 0)"
    }

    JSON_PRODUCT_CATALOG {
        string id PK "Mã sản phẩm 10 ký tự (VD: OLJCESPC7Z)"
        string name "Tên sản phẩm (VD: Sunglasses)"
        string description "Mô tả chi tiết"
        string picture "Đường dẫn ảnh tĩnh (/static/img/products/...)"
        Money priceUsd "Giá gốc bằng USD {currencyCode, units, nanos}"
        string_array categories "Danh sách nhãn (VD: ['accessories'])"
    }

    EPHEMERAL_ORDER_RESULT {
        string order_id PK "UUID sinh lúc PlaceOrder (không lưu DB)"
        string shipping_tracking_id "Mã vận đơn sinh từ ShippingService"
        Money shipping_cost "Phí vận chuyển đã quy đổi sang user_currency"
        Address shipping_address "Địa chỉ giao hàng"
        repeated_OrderItem items "Danh sách CartItem kèm đơn giá Cost đã quy đổi"
    }

    REDIS_CART_ENTRY ||--|| PROTO_CART : "deserializes via Cart.Parser.ParseFrom()"
    PROTO_CART ||--o{ PROTO_CART_ITEM : "contains"
    PROTO_CART_ITEM }o--|| JSON_PRODUCT_CATALOG : "resolves via GetProduct(product_id)"
    EPHEMERAL_ORDER_RESULT ||--o{ PROTO_CART_ITEM : "snapshots during PlaceOrder()"
```

---

### 3.2. Chi tiết 3 Lớp Data Schema thực tế trong Mã nguồn

#### A. Schema Lưu trữ Giỏ hàng trong Redis (`src/cartservice/src/cartstore/RedisCartStore.cs`)
- **Engine:** `redis:alpine` chạy trên cổng `6379`, truy cập thông qua thư viện `Microsoft.Extensions.Caching.Distributed.IDistributedCache` (`StackExchangeRedisCache` được cấu hình tại `Startup.cs`).
- **Cấu trúc Key:** Chuỗi `userId` (chính là giá trị UUID của cookie `shop_session-id` do `frontend` cấp tại `src/frontend/middleware.go:103-116`).
- **Cấu trúc Value:** Mảng byte nhị phân (`byte[]`) được tuần tự hóa trực tiếp từ đối tượng Protobuf `Hipstershop.Cart` bằng phương thức `cart.ToByteArray()` (`RedisCartStore.cs:60`) và giải tuần tự hóa bằng `Hipstershop.Cart.Parser.ParseFrom(value)` (`RedisCartStore.cs:49, 94`).
- **Định nghĩa Schema `Cart` (`protos/demo.proto:29-50` & `src/cartservice/src/protos/Cart.proto`):**
  ```protobuf
  message CartItem {
      string product_id = 1; // Mã sản phẩm, VD: "OLJCESPC7Z"
      int32  quantity = 2;   // Số lượng mặt hàng
  }

  message Cart {
      string user_id = 1;          // UUID phiên người dùng
      repeated CartItem items = 2; // Danh sách mặt hàng trong giỏ
  }
  ```
- **Hành vi khi làm rỗng giỏ hàng (`EmptyCartAsync` — `RedisCartStore.cs:68-81`):** Thay vì xóa key (`DEL`), code khởi tạo một `new Hipstershop.Cart()` rỗng và ghi đè `cart.ToByteArray()` vào lại key `userId`.

#### B. Schema Danh mục Sản phẩm (`src/productcatalogservice/products.json`) & Tiền tệ (`src/currencyservice/data/currency_conversion.json`)
1. **Product Catalog JSON (`products.json` — 9 sản phẩm):**
   - Được nạp vào biến toàn cục `catalog pb.ListProductsResponse` khi khởi động `productcatalogservice` (`server.go:65` & `catalog_loader.go`) bằng `jsonpb.Unmarshal`.
   - Mỗi phần tử tuân thủ chặt chẽ message `hipstershop.Product` (`protos/demo.proto:77-87`):
     - `id` (`string`): Khóa định danh 10 ký tự chữ hoa + số (VD: `"OLJCESPC7Z"`, `"66VCHSJNUP"`, `"1YMWWN1N4O"`).
     - `name` (`string`), `description` (`string`), `picture` (`string`).
     - `priceUsd` (`Money`): Lưu giá gốc luôn tính bằng `"USD"` với 2 trường số nguyên `units` (phần nguyên, `int64`) và `nanos` (phần thập phân $10^{-9}$, `int32`) để **tránh sai số dấu phẩy động (floating-point precision error)**. Ví dụ: `$19.99` được lưu là `units: 19, nanos: 990000000`.
     - `categories` (`repeated string`): Mảng danh mục phục vụ lọc quảng cáo (VD: `["clothing", "tops"]`).
2. **Currency Conversion JSON (`currency_conversion.json`):**
   - Lưu bảng tỷ giá hối đoái quy chuẩn theo đồng `EUR` (ví dụ: `"USD": "1.1305"`, `"JPY": "126.40"`, `"GBP": "0.85970"`).
   - Khi chuyển đổi từ tiền tệ A sang tiền tệ B (`server.js:138-163`), `currencyservice` đổi từ `A -> EUR` rồi từ `EUR -> B`, sau đó gọi hàm `_carry(amount)` (`server.js:117-123`) để chuẩn hóa phần dư giữa `units` và `nanos`.

#### C. Trạng thái Đơn hàng khi Checkout (`OrderResult` — Ephemeral Snapshot)
- Trong `checkoutservice`, khi hàm `PlaceOrder()` (`src/checkoutservice/main.go:230-280`) chạy xong:
  - Nó giải quyết (resolve) từng `CartItem` sang `OrderItem` chứa **giá đã quy đổi tại thời điểm đặt hàng (`Cost: price`)** (`main.go:352-354`).
  - Nó đóng gói `OrderResult` (gồm `order_id`, `shipping_tracking_id`, `shipping_cost`, `shipping_address`, `items`) và trả trực tiếp về cho `frontend` để hiển thị trang kết quả đặt hàng (`templates/order.html`) đồng thời gửi sang `emailservice`.
  - **Không có Order Database:** `checkoutservice` không lưu `OrderResult` vào bất kỳ cơ sở dữ liệu nào sau khi trả response (đây là thiết kế chủ đích của Google cho ứng dụng demo stateless).

> **Đối chiếu bổ sung với Mini Shop (nếu giảng viên hỏi về ERD quan hệ / SQL Schema):**
> Trong trường hợp câu hỏi vấn đáp yêu cầu trình bày thêm về **Relational Database Schema (SQL)** có khóa chính/khóa ngoại và lưu trữ đơn hàng bền vững, bạn có thể dẫn chiếu ngay sang dự án phụ **[Mini Shop](../mini-shop/project-knowledge-application-implementation/01-concepts.md#phần-3-database-schema--data-model)** trong cùng thư mục Chủ đề 2 này (sử dụng 2 MySQL instances tách biệt `products-db` và `orders-db`, lưu snapshot `product_name` + `unit_price_vnd` vào bảng `order_items` và chống trùng đơn bằng `idempotency_key` + `request_hash` trong ACID transaction).
