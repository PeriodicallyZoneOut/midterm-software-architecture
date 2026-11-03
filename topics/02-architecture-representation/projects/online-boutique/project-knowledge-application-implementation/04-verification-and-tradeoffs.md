# 04. Kiểm chứng Kiến trúc, Đánh đổi (Trade-offs) & 10 Câu hỏi Vấn đáp — Online Boutique

Tài liệu này tổng hợp bảng đối chiếu sơ đồ upstream với mã nguồn thực tế, phân tích **5 Quyết định Kiến trúc & Đánh đổi (ADRs / Trade-offs)** và chuẩn bị sẵn **10 Câu hỏi — Đáp án Vấn đáp chuyên sâu** kèm trích dẫn `file:line` theo đúng yêu cầu tại **Mục 5 & Mục 10 (`docs/TEAM-ASSIGNMENT.md`)**.

---

## Phần 1: Bảng Đối chiếu Sơ đồ Upstream vs. Mã nguồn & Manifest Thực tế

Theo yêu cầu tại `docs/TEAM-ASSIGNMENT.md` (dòng 70): *"Sơ đồ upstream đơn lẻ chưa đủ"*. Dưới đây là những điểm mà sơ đồ tổng quan trong `README.md` gốc của Google không thể hiện hết, nhưng đã được chúng ta xác minh trực tiếp từ code và `release/kubernetes-manifests.yaml`:

| Điểm kiểm chứng | Sơ đồ Upstream (`README.md` gốc) | Thực tế trong Mã nguồn & Manifest (`source/`) | Vị trí Bằng chứng (`file:line`) |
| :--- | :--- | :--- | :--- |
| **1. Cổng của `emailservice`** | Chỉ vẽ mũi tên gRPC từ `checkoutservice` tới `emailservice`. | Container `emailservice` lắng nghe cổng `8080`, nhưng Kubernetes `Service/emailservice` mở cổng **`5000`** ánh xạ vào `targetPort: 8080`. | `release/kubernetes-manifests.yaml:217-218` (`EMAIL_SERVICE_ADDR: "emailservice:5000"`) & `:391-393` (`port: 5000, targetPort: 8080`). |
| **2. Dịch vụ Thật vs. Dịch vụ Mock** | Vẽ tất cả 11 hộp microservice giống hệt nhau. | `paymentservice` (chỉ kiểm tra Luhn + VISA/MasterCard rồi trả UUID), `shippingservice` (tính phí theo công thức đếm item), và `emailservice` (chạy `DummyEmailService` chỉ in log) là **Mock / Stateless**. | `src/paymentservice/charge.js:61-86`, `src/shippingservice/main.go:119-155`, `src/emailservice/email_server.py:108-125`. |
| **3. Cơ sở dữ liệu Đơn hàng (Orders DB)** | Người xem dễ lầm tưởng `checkoutservice` lưu đơn hàng vào DB. | `checkoutservice` **hoàn toàn không có Database**. `OrderResult` chỉ tồn tại trong bộ nhớ lúc chạy `PlaceOrder()` rồi trả về cho `frontend` hiển thị. | `src/checkoutservice/main.go:230-280`. |
| **4. Độ bền dữ liệu của `redis-cart`** | Vẽ `redis-cart` như một database lưu trữ bền vững. | Trong `release/kubernetes-manifests.yaml`, volume `redis-data` dùng **`emptyDir: {}`** (không phải `PersistentVolumeClaim`), nghĩa là dữ liệu mất khi Pod bị xóa. | `release/kubernetes-manifests.yaml:880-891`. |
| **5. Phân cấp Chịu lỗi (Critical vs. Non-Critical)** | Các mũi tên gRPC từ `frontend` đều có nét vẽ giống nhau. | Lỗi từ `adservice` (timeout 100ms) và `recommendationservice` bị `frontend` bắt và bỏ qua (`log.Warn`), trang vẫn trả `HTTP 200`. Lỗi từ `cart`, `catalog`, `currency`, `checkout` trả ngay `HTTP 500`. | `src/frontend/rpc.go:169-180` (`chooseAd`), `src/frontend/handlers.go:178-181, 266-269`. |
| **6. Dịch vụ Tùy chọn (`shoppingassistantservice`, `packagingInfo`)** | Không xuất hiện trong manifest mặc định hoặc bị comment. | `frontend` có biến môi trường `SHOPPING_ASSISTANT_SERVICE_ADDR` và code kiểm tra `ENABLE_ASSISTANT`, `PACKAGING_SERVICE_URL`, nhưng mặc định tắt (`false`) và không triển khai Pod trong `kubernetes-manifests.yaml`. | `src/frontend/handlers.go:48, 190-196` & `release/kubernetes-manifests.yaml:541-557`. |

---

## Phần 2: 5 Quyết định Kiến trúc & Đánh đổi (Architectural Decisions & Trade-offs)

### ADR-01: Giao tiếp Nội bộ bằng gRPC + Protocol Buffers trên nền Đa ngôn ngữ (Polyglot Microservices)
- **Quyết định:** Sử dụng **gRPC (HTTP/2)** và một tệp hợp đồng duy nhất **`protos/demo.proto`** (`package hipstershop`) để kết nối 10 microservices viết bằng 5 ngôn ngữ khác nhau (Go, C#/.NET, Node.js, Python, Java).
- **Lợi ích (Pros):**
  - **Strict Contract & Type Safety:** Sinh mã client/server tự động (`protoc`), loại bỏ lỗi sai lệch tên trường JSON giữa các ngôn ngữ.
  - **Hiệu năng cao:** Tuần tự hóa nhị phân Protobuf nhỏ gọn và ghép kênh nhiều request trên một kết nối TCP duy nhất nhờ HTTP/2 (`*grpc.ClientConn`).
- **Đánh đổi (Cons / Cost):**
  - Trình duyệt web không gọi trực tiếp được gRPC thuần, buộc phải có tầng `frontend` chuyển đổi HTTP/1.1 $\leftrightarrow$ gRPC.
  - Khó debug thủ công bằng `curl` hơn REST/JSON (cần `grpcurl` hoặc gRPC reflection).

### ADR-02: Điều phối Đặt hàng Tập trung Đồng bộ (`checkoutservice` Orchestrator) vs. Choreography (EDA)
- **Quyết định:** Dùng `checkoutservice` làm **Synchronous Orchestrator** gọi tuần tự 6 dịch vụ (`Cart` $\rightarrow$ `ProductCatalog` $\rightarrow$ `Currency` $\rightarrow$ `Shipping` $\rightarrow$ `Payment` $\rightarrow$ `Email`) trong một lời gọi RPC `PlaceOrder`.
- **Lợi ích (Pros):**
  - Luồng nghiệp vụ tập trung tại một hàm duy nhất (`src/checkoutservice/main.go:230-280`), rất dễ đọc, dễ hiểu và trả ngay mã vận đơn `shipping_tracking_id` cho người dùng trong cùng HTTP response.
  - Không cần vận hành Message Broker (như RabbitMQ/Kafka).
- **Đánh đổi (Cons / Cost):**
  - **Temporal Coupling (Phụ thuộc thời gian thực):** Nếu 1 trong 5 dịch vụ trọng yếu (`Cart`, `Catalog`, `Currency`, `Payment`, `Shipping`) bị treo hoặc chết tại thời điểm bấm nút, toàn bộ lệnh `PlaceOrder` thất bại ngay lập tức.
  - **Không có Saga Compensation:** Nếu `chargeCard` (Bước 7) thành công nhưng `shipOrder` (Bước 8) thất bại (`main.go:258-261`), code hiện tại trả lỗi `codes.Unavailable` mà chưa có bước gọi ngược lại `PaymentService` để hoàn tiền (Refund).

### ADR-03: Biểu diễn Tiền tệ bằng Cấu trúc Số nguyên `Money {units, nanos}` thay vì `float / double`
- **Quyết định:** Mọi giá trị tiền tệ trong `protos/demo.proto` (`Money` message tại dòng 146–161) đều tách thành `int64 units` (phần nguyên) và `int32 nanos` ($10^{-9}$ đơn vị), kèm thư viện tính toán riêng (`src/checkoutservice/money/money.go`, `src/frontend/money/money.go`, `_carry()` trong `src/currencyservice/server.js:117`).
- **Lợi ích (Pros):**
  - Triệt tiêu hoàn toàn sai số biểu diễn nhị phân dấu phẩy động IEEE 754 (ví dụ `0.1 + 0.2 != 0.3`) khi nhân số lượng và quy đổi qua lại giữa `USD`, `EUR`, `JPY`.
- **Đánh đổi (Cons / Cost):**
  - Không dùng được toán tử `+`, `*` mặc định của ngôn ngữ; mỗi ngôn ngữ (Go, JS) phải tự cài đặt và duy trì logic cộng/nhân có nhớ (`carry`).

### ADR-04: Lưu trữ Giỏ hàng bằng Redis Binary Protobuf (`redis-cart`) thay vì Relational DB
- **Quyết định:** Dùng Redis lưu trực tiếp mảng byte `Hipstershop.Cart.ToByteArray()` theo key `userId` (`RedisCartStore.cs:60`).
- **Lợi ích (Pros):**
  - Đọc/ghi toàn bộ giỏ hàng chỉ tốn **1 lệnh Redis (`GET` hoặc `SET`)** với độ trễ cực thấp, không tốn chi phí `JOIN` bảng `carts` và `cart_items`.
- **Đánh đổi (Cons / Cost):**
  - Không thể truy vấn phân tích (analytics query) bên trong giỏ hàng từ phía DB, và thao tác `AddItemAsync` theo kiểu Read-Modify-Write (`GetAsync` $\rightarrow$ sửa RAM $\rightarrow$ `SetAsync`) có thể gặp **Lost Update** nếu cùng 1 user gửi 2 request song song.

### ADR-05: Cô lập Lỗi Dịch vụ Phụ trợ (Graceful Degradation cho `adservice`, `recommendationservice`, `emailservice`)
- **Quyết định:** Các dịch vụ tăng cường trải nghiệm (`adservice`, `recommendationservice`) và thông báo (`emailservice`) được xử lý theo cơ chế **Best-Effort**: đặt timeout ngắn (100ms cho `chooseAd`) và nuốt lỗi (`log.Warn`) tại caller.
- **Lợi ích (Pros):**
  - Bảo vệ luồng doanh thu chính (Browse $\rightarrow$ Add to Cart $\rightarrow$ Checkout) luôn hoạt động ngay cả khi dịch vụ Java (`adservice`) hoặc Python (`recommendationservice`, `emailservice`) bị OOMKilled hoặc quá tải.
- **Đánh đổi (Cons / Cost):**
  - Người dùng có thể thấy trang web thiếu phần quảng cáo/gợi ý hoặc không nhận được email mà không có thông báo lỗi trên màn hình (cần hệ thống giám sát Log/Metrics bên dưới để phát hiện).

---

## Phần 3: Bộ 10 Câu hỏi & Trả lời Vấn đáp Chuyên sâu (Có Trích dẫn `file:line`)

### Câu 1: Vì sao nói "4 sơ đồ UML không đồng nghĩa với 4+1 Views" và "4 cấp độ C4 không thay thế được 4+1 Views"?
- **Trả lời:**
  - **4+1 Views (Kruchten)** phân chia kiến trúc theo **mối quan tâm của từng nhóm Stakeholder**: Logical (chức năng & domain ownership), Development (tổ chức code & build), Process (luồng thực thi, đồng bộ/bất đồng bộ, chịu lỗi), Physical/Deployment (hạ tầng Pod/Service/Network), và Scenarios (`+1`).
  - Trong khi đó, **C4 Model** phân chia theo **4 mức độ phóng đại không gian (Zoom Levels)** của cấu trúc tĩnh: System Context (L1) $\rightarrow$ Container (L2) $\rightarrow$ Component (L3) $\rightarrow$ Code (L4). C4 làm rất tốt việc giải thích Logical View và Development View, nhưng chỉ riêng C4 thì không thể hiện rõ thứ tự gọi 10 bước trong `PlaceOrder()`, hành vi lỗi khi `redis-cart` chết (Process View) hay cấu hình `readinessProbe`, `securityContext`, `emptyDir` (Deployment View). Vì vậy cần kết hợp cả hai.

### Câu 2: Trong Online Boutique, những dịch vụ nào xử lý dữ liệu thật và những dịch vụ nào chỉ là Mock? Chứng minh bằng code.
- **Trả lời:**
  - **Dịch vụ xử lý thật:**
    1. `frontend` (`src/frontend/handlers.go`): Xử lý HTTP, session cookie, gọi gRPC và render HTML thật.
    2. `cartservice` (`src/cartservice/src/cartstore/RedisCartStore.cs:33-104`): Đọc/ghi byte Protobuf thật vào `redis-cart:6379`.
    3. `productcatalogservice` (`src/productcatalogservice/product_catalog.go:41-83`): Nạp và tìm kiếm thật trên 9 sản phẩm từ `products.json`.
    4. `currencyservice` (`src/currencyservice/server.js:138-167`): Tính toán quy đổi tỷ giá thật từ `currency_conversion.json`.
    5. `checkoutservice` (`src/checkoutservice/main.go:230-280`): Điều phối thật 6 dịch vụ và tính tổng tiền bằng package `money`.
    6. `recommendationservice` (`recommendation_server.py:70-86`) & `adservice` (`AdService.java:94-118`): Lọc danh sách sản phẩm và tra cứu multimap quảng cáo thật trong RAM.
  - **Dịch vụ Mock (Mô phỏng):**
    1. `paymentservice` (`src/paymentservice/charge.js:61-86`): Chỉ kiểm tra định dạng thẻ VISA/MasterCard bằng `simple-card-validator` rồi trả về `uuidv4()`, không gọi cổng thanh toán ngân hàng.
    2. `shippingservice` (`src/shippingservice/main.go:119-155`): Tính phí vận chuyển giả lập từ số lượng item (`CreateQuoteFromCount`) và ghép chuỗi tạo mã vận đơn ngẫu nhiên (`CreateTrackingId`).
    3. `emailservice` (`src/emailservice/email_server.py:108-125`): Mặc định khởi chạy `DummyEmailService` (`start(dummy_mode=True)` tại dòng 199), chỉ ghi log chứ không gửi SMTP thật (`EmailService.__init__` tại dòng 63 thậm chí `raise Exception('cloud mail client not implemented')`).

### Câu 3: Hãy truy vết chính xác những gì xảy ra trong code khi người dùng bấm nút "Place Order" (`POST /cart/checkout`).
- **Trả lời:**
  1. `frontend` nhận `POST /cart/checkout` tại `placeOrderHandler` (`src/frontend/handlers.go:320`), kiểm tra hợp lệ bằng `payload.Validate()` (dòng 349), rồi gọi gRPC `PlaceOrder` sang `checkoutservice:5050` (dòng 354).
  2. Tại `src/checkoutservice/main.go:230` (`PlaceOrder`), hệ thống sinh `orderID` (dòng 233) và gọi `prepareOrderItemsAndShippingQuoteFromCart` (dòng 238):
     - Gọi `cartservice.GetCart` lấy danh sách `cartItems` (dòng 290).
     - Trong `prepOrderItems` (dòng 339–357), lặp qua từng item: gọi `productcatalogservice.GetProduct` lấy giá USD, rồi gọi `currencyservice.Convert` đổi sang tiền tệ của khách.
     - Gọi `shippingservice.GetQuote` lấy cước vận chuyển USD (dòng 298) rồi gọi `currencyservice.Convert` đổi sang tiền tệ của khách (dòng 302).
  3. Cộng tổng tiền `total = shippingCostLocalized + sum(item.Cost * qty)` bằng `money.Sum` và `money.MultiplySlow` (dòng 246–250).
  4. Gọi `paymentservice.Charge` (dòng 252) để lấy `txID`.
  5. Gọi `shippingservice.ShipOrder` (dòng 258) để lấy `shippingTrackingID`.
  6. Gọi `cartservice.EmptyCart` để xóa giỏ hàng (dòng 263).
  7. Gọi `emailservice.SendOrderConfirmation` (dòng 273) và trả `OrderResult` về cho `frontend` render `templates/order.html` (dòng 392).

### Câu 4: Baseline của Online Boutique có Relational Database Schema (SQL) không? Dữ liệu giỏ hàng và sản phẩm được lưu trữ theo schema nào?
- **Trả lời:**
  - **Không.** Bản chuẩn của Online Boutique không sử dụng RDBMS/SQL (không có MySQL/PostgreSQL trong `release/kubernetes-manifests.yaml`).
  - Hệ thống dùng **3 lớp Non-Relational Schema**:
    1. **Redis Key-Value Schema (`redis-cart:6379`):** Trong `src/cartservice/src/cartstore/RedisCartStore.cs:33-104`, key là chuỗi `userId` (session UUID), value là mảng byte nhị phân của Protobuf message `Hipstershop.Cart` (`user_id` + `repeated CartItem {product_id, quantity}`).
    2. **JSON Catalog Schema (`src/productcatalogservice/products.json`):** Lưu 9 sản phẩm theo cấu trúc `Product` (`id`, `name`, `description`, `picture`, `priceUsd: {currencyCode, units, nanos}`, `categories[]`), nạp vào bộ nhớ qua `loadCatalog()` (`catalog_loader.go:34`).
    3. **JSON Currency Schema (`src/currencyservice/data/currency_conversion.json`):** Bảng tỷ giá tĩnh quy chiếu theo đồng `EUR`.

### Câu 5: Nếu Pod `adservice` hoặc `recommendationservice` bị sập (`replicas=0`), người dùng có mua hàng được không? Ngược lại, nếu `redis-cart` bị sập thì sao?
- **Trả lời:**
  - **Nếu `adservice` hoặc `recommendationservice` sập:** Người dùng **vẫn duyệt web, thêm giỏ hàng và đặt hàng thành công bình thường (`HTTP 200 OK`)**. Lý do:
    - Ở `src/frontend/rpc.go:169-180` (`chooseAd`), `frontend` đặt timeout 100ms cho `getAd`; nếu lỗi chỉ ghi `log.WithField("error", err).Warn("failed to retrieve ads")` và trả về mảng quảng cáo rỗng.
    - Ở `src/frontend/handlers.go:178-181` (`productHandler`) và `:266-269` (`viewCartHandler`), lỗi từ `getRecommendations` chỉ ghi `log.Warn` chứ không gọi `renderHTTPError`.
  - **Nếu `redis-cart` sập:** Mọi trang có đọc/ghi giỏ hàng (`/`, `/product/{id}`, `/cart`, `/cart/checkout`) đều **thất bại với `HTTP 500 Internal Server Error`**. Lý do: `RedisCartStore.cs:64, 102` bắt ngoại lệ kết nối Redis và ném `RpcException(StatusCode.FailedPrecondition, "Can't access cart storage...")`, khiến `frontend` (`handlers.go:73-75, 166-168, 231-234`) dừng xử lý và trả trang lỗi 500.

### Câu 6: Có sự khác biệt nào giữa cổng Container và cổng Kubernetes Service trong `release/kubernetes-manifests.yaml` không?
- **Trả lời:**
  - Hầu hết các dịch vụ có `port` trùng với `targetPort` (ví dụ `productcatalogservice: 3550->3550`, `cartservice: 7070->7070`, `checkoutservice: 5050->5050`), ngoại trừ **2 trường hợp**:
    1. **`frontend` và `frontend-external` (`kubernetes-manifests.yaml:576-595`):** Kubernetes Service mở cổng HTTP chuẩn **`80`**, chuyển tiếp vào `targetPort: 8080` của container `frontend`.
    2. **`emailservice` (`kubernetes-manifests.yaml:358, 391-393`):** Container Python lắng nghe trên `containerPort: 8080`, nhưng Kubernetes `Service/emailservice` mở cổng **`5000`** (`port: 5000 -> targetPort: 8080`). Do đó `checkoutservice` kết nối tới `emailservice:5000` (`kubernetes-manifests.yaml:218`).

### Câu 7: Điều gì xảy ra nếu hai request `AddItem` của cùng một người dùng gửi đến `cartservice` vào cùng một thời điểm?
- **Trả lời:**
  - Trong `src/cartservice/src/cartstore/RedisCartStore.cs:40-60`, hàm `AddItemAsync` thực hiện:
    1. `var value = await _cache.GetAsync(userId);`
    2. Giải tuần tự hóa Protobuf `Cart.Parser.ParseFrom(value)` và cộng dồn `Quantity` trong bộ nhớ C#.
    3. `await _cache.SetAsync(userId, cart.ToByteArray());`
  - Vì không có khóa phân tán (Distributed Lock), giao dịch Redis (`WATCH`/`MULTI`/`EXEC`) hay Lua script, đây là mẫu **Read-Modify-Write không nguyên tử**. Nếu 2 request của cùng 1 `userId` đọc cùng `value` ban đầu, request ghi `SetAsync` sau sẽ ghi đè làm mất lượt thêm hàng của request trước (**Lost Update**). Khác người dùng (`userId` khác nhau) thì hoàn toàn độc lập, không bị ảnh hưởng.

### Câu 8: Nếu trong lúc `PlaceOrder()`, bước `chargeCard` (thu tiền) đã thành công nhưng bước `shipOrder` ngay sau đó bị lỗi mạng thì chuyện gì xảy ra?
- **Trả lời:**
  - Tại `src/checkoutservice/main.go:252-264`:
    - Dòng 252: `txID, err := cs.chargeCard(...)` đã thực hiện xong.
    - Dòng 258–261: `shippingTrackingID, err := cs.shipOrder(...)` nếu trả về `err != nil`, hàm lập tức `return nil, status.Errorf(codes.Unavailable, "shipping error: %+v", err)`.
  - Hệ quả:
    1. Không có lệnh gọi hoàn tiền (Compensating Transaction / Refund) sang `paymentservice`.
    2. Dòng 263 (`_ = cs.emptyUserCart(...)`) chưa được chạy tới, nên các mặt hàng vẫn nằm nguyên trong giỏ hàng của khách.
    3. Đây là giới hạn điển hình của điều phối đồng bộ không có Saga / Persistent State Machine.

### Câu 9: Các container trong `release/kubernetes-manifests.yaml` được bảo vệ ở tầng hệ điều hành/Kubernetes như thế nào?
- **Trả lời:**
  - Tất cả 12 Deployments trong `release/kubernetes-manifests.yaml` đều tuân thủ nguyên tắc **Least Privilege** rất nghiêm ngặt:
    - **Pod-level `securityContext`:** Chạy với user thường `runAsNonRoot: true`, `runAsUser: 1000`, `runAsGroup: 1000`, `fsGroup: 1000`.
    - **Container-level `securityContext`:** Hệ thống tệp gốc chỉ đọc (`readOnlyRootFilesystem: true`), cấm leo thang đặc quyền (`allowPrivilegeEscalation: false`, `privileged: false`), và gỡ bỏ toàn bộ Linux capabilities (`capabilities: { drop: ["ALL"] }`).
    - Mỗi dịch vụ chạy dưới một `ServiceAccount` riêng biệt.

### Câu 10: Tại sao trong `frontend/handlers.go` và `checkoutservice/main.go`, việc hiển thị trang chủ hoặc đặt hàng nhiều sản phẩm lại có thể gây ra hiện tượng "N+1 gRPC Calls" (Chatty I/O)?
- **Trả lời:**
  - Trong `src/frontend/handlers.go:83-90` (`homeHandler`), sau khi lấy 9 sản phẩm từ `ListProducts`, `frontend` chạy vòng lặp `for i, p := range products` và gọi `fe.convertCurrency(...)` **9 lần liên tiếp qua mạng gRPC** sang `currencyservice:7000` (1 lần cho mỗi sản phẩm).
  - Tương tự, trong `src/checkoutservice/main.go:343-355` (`prepOrderItems`), với giỏ hàng có $K$ mặt hàng, `checkoutservice` lặp $K$ lần: mỗi lần gọi 1 RPC `GetProduct` sang `productcatalogservice:3550` và 1 RPC `Convert` sang `currencyservice:7000` (tổng cộng $2K$ RPC tuần tự).
  - **Cách tối ưu (nếu được hỏi mở rộng):** Thêm RPC batch như `ConvertBatch` hoặc thực hiện quy đổi tỷ giá theo bảng cache ngắn hạn ngay tại client, và thêm `GetProductsByIds(repeated string ids)` (giống như endpoint `/internal/products/resolve` đã được thiết kế trong dự án phụ **Mini Shop**!).
