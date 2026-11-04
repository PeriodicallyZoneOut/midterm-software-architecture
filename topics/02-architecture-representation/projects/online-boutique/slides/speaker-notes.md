# Lời dẫn Thuyết trình (Speaker Notes — 8–10 Phút) — Online Boutique

Tài liệu này là kịch bản nói chi tiết cho 12 slide của **Online Boutique (`microservices-demo`)**, bám sát tiêu chí nghiệm thu của **Thế Anh (Mục 5 — `docs/TEAM-ASSIGNMENT.md`)**.

---

## Slide 1: Biểu diễn Kiến trúc Online Boutique (~40 giây)
- **Lời dẫn:** Xin chào thầy và các bạn. Hôm nay mình đại diện nhóm trình bày Chủ đề 2: **Architecture Representation (Biểu diễn Kiến trúc Phần mềm)** áp dụng trên hệ thống mã nguồn mở **Google Online Boutique (`microservices-demo`, phiên bản `v0.10.7`)**.
- Thay vì chỉ dùng lại bức ảnh sơ đồ tổng quan có sẵn trên GitHub của Google, mục tiêu của phần trình bày này là tái dựng toàn bộ kiến trúc từ mã nguồn đa ngôn ngữ và cấu hình Kubernetes thực tế theo mô hình **4+1 Views**, **C4 Model (Level 1–4)**, **Data Model (Protobuf/Redis/JSON)** và ánh xạ từng hộp trên sơ đồ xuống đúng hàm xử lý trong code (`file:line`) cũng như Pod/Service đang chạy.

## Slide 2: Stakeholders, 4+1 Views & C4 Model (~45 giây)
- **Lời dẫn:** Trước hết, tại sao một hình vẽ duy nhất không bao giờ đủ? Vì mỗi nhóm Stakeholder có mối quan tâm hoàn toàn khác nhau: khách hàng quan tâm trải nghiệm giỏ hàng và thanh toán; lập trình viên quan tâm hợp đồng gRPC giữa 5 ngôn ngữ; còn kỹ sư vận hành (SRE) lại quan tâm Pod, cổng mạng và giới hạn CPU/RAM.
- Một nguyên tắc quan trọng là **4 sơ đồ UML không đồng nghĩa với 4 Views**, và **4 cấp độ C4 cũng không thay thế được 4+1 Views**. C4 cung cấp 4 mức phóng đại cấu trúc tĩnh (từ Context $\rightarrow$ Container $\rightarrow$ Component $\rightarrow$ Code), còn 4+1 Views bổ sung chiều động ở Process View, Deployment View và các kịch bản kiểm chứng (`+1` Scenarios).

## Slide 3: C4 Context & Container — 11 Microservices (~50 giây)
- **Lời dẫn:** Ở cấp độ C4 Level 1 và Level 2, Online Boutique bao gồm **10 microservices nghiệp vụ**, **1 công cụ tạo tải (`loadgenerator`)** và **1 kho dữ liệu `redis-cart`**, được viết bằng 5 ngôn ngữ: Go, C#/.NET, Node.js, Python và Java.
- Khi đọc sâu vào code, chúng ta phải phân biệt rất rõ hai nhóm dịch vụ mà sơ đồ gốc không nói tới:
  1. **Nhóm xử lý dữ liệu thật:** `frontend`, `cartservice` (ghi vào Redis thật), `productcatalogservice` (đọc 9 sản phẩm từ JSON), `currencyservice` (tính tỷ giá ECB thật), `checkoutservice`, `recommendationservice` và `adservice`.
  2. **Nhóm dịch vụ mô phỏng (Mock/Stateless):** `paymentservice` chỉ kiểm tra thuật toán Luhn và thẻ VISA/MasterCard rồi trả về UUID ngẫu nhiên; `shippingservice` tính cước theo số lượng item; và `emailservice` chạy lớp `DummyEmailService` chỉ in log chứ không gửi SMTP thật.

## Slide 4: Logical View & Development View (~45 giây)
- **Lời dẫn:** Sang mô hình 4+1:
  - Ở **Logical View**, `frontend` đóng vai trò cổng vào HTTP duy nhất kiêm Backend-for-Frontend, còn `checkoutservice` là bộ điều phối trung tâm (Orchestrator) cho quy trình đặt hàng.
  - Ở **Development View**, toàn bộ 10 dịch vụ backend chia sẻ một nguồn sự thật duy nhất là tệp hợp đồng **`protos/demo.proto`** (`package hipstershop` gồm 9 gRPC Services và 29 Messages). Mã nguồn trong `src/` tuân thủ triệt để nguyên tắc **Share-Nothing** (ngay cả các dịch vụ cùng viết bằng Go cũng không dùng chung thư viện nội bộ) và được đóng gói bằng các Multi-stage Dockerfiles riêng biệt.

## Slide 5: C4 Level 3 & 4 — Bên trong Frontend, Checkout & Cart (~50 giây)
- **Lời dẫn:** Phóng đại vào C4 Level 3 và Level 4 của 3 dịch vụ quan trọng nhất:
  - Trong **`frontend`**: `middleware.go` cấp cookie `shop_session-id`; `handlers.go` nhận HTTP request, gọi `validator.go` kiểm tra dữ liệu và dùng `rpc.go` để gọi 7 gRPC channels.
  - Trong **`checkoutservice`**: Hàm `PlaceOrder()` gọi `prepareOrderItemsAndShippingQuoteFromCart()` và dùng package `money` (`Sum`, `MultiplySlow`) để tính toán tiền tệ không sai số.
  - Trong **`cartservice`**: Lớp `CartService.cs` gọi qua interface `ICartStore` xuống `RedisCartStore.cs`, sử dụng thư viện `Google.Protobuf` để chuyển đổi đối tượng `Cart` thành mảng byte nhị phân lưu vào Redis.

## Slide 6: Process View — Luồng Đặt hàng Đồng bộ `PlaceOrder` (~55 giây)
- **Lời dẫn:** Ở Process View, hãy nhìn vào luồng phức tạp nhất hệ thống: khi người dùng bấm nút **Place Order**, `checkoutservice` thực hiện **10 bước đồng bộ tuần tự**:
  1. Tạo `orderID` UUID và gọi `GetCart` sang `cartservice:7070`.
  2. Lặp qua từng món hàng: gọi `GetProduct` (`:3550`) lấy giá gốc USD và gọi `Convert` (`:7000`) đổi sang tiền tệ người dùng.
  3. Gọi `GetQuote` (`:50051`) lấy phí vận chuyển rồi lại gọi `Convert` sang tiền tệ người dùng.
  4. Cộng tổng tiền, gọi `Charge` (`:50051`) thu tiền thẻ, gọi `ShipOrder` (`:50051`) lấy mã vận đơn `tracking_id`.
  5. Cuối cùng gọi `EmptyCart` xóa giỏ hàng và gọi `SendOrderConfirmation` (`:5000`) gửi email xác nhận trước khi trả `OrderResult` về trình duyệt.

## Slide 7: Physical / Deployment View (Kubernetes) & Chịu lỗi (+1 Scenarios) (~50 giây)
- **Lời dẫn:** Ở góc nhìn Deployment (`release/kubernetes-manifests.yaml`), hệ thống triển khai **12 Deployments và 12 Services** trên Kubernetes:
  - Chỉ `frontend-external` là `LoadBalancer` mở cổng `80 -> 8080`; toàn bộ các dịch vụ còn lại đều là `ClusterIP` nội bộ. Lưu ý một chi tiết thực tế từ manifest: Pod `emailservice` lắng nghe cổng `8080`, nhưng Kubernetes `Service` của nó mở cổng **`5000`** trỏ vào `targetPort: 8080`.
  - Về kịch bản chịu lỗi (`+1` Scenarios): Hệ thống tách bạch rõ **Non-Critical Path** và **Critical Path**. Nếu ta tắt `adservice` hoặc `recommendationservice`, `frontend` chỉ ghi cảnh báo `log.Warn` (với timeout 100ms cho quảng cáo) và vẫn trả trang web `HTTP 200 OK`. Ngược lại, nếu tắt `redis-cart`, `cartservice` ném `RpcException(FailedPrecondition)` và hệ thống báo lỗi `HTTP 500` ngay lập tức.

## Slide 8: Data Schema / Data Model — Redis, JSON & Protobuf (~50 giây)
- **Lời dẫn:** Về Data Schema, cần khẳng định rõ: **bản chuẩn của Online Boutique không sử dụng cơ sở dữ liệu SQL quan hệ**. Thay vào đó, mô hình dữ liệu gồm 3 lớp:
  1. **Redis Key-Value Schema (`redis-cart:6379`):** Key là chuỗi `user_id` (lấy từ cookie `shop_session-id`), còn Value là chuỗi byte nhị phân `Hipstershop.Cart.ToByteArray()` chứa danh sách `product_id` và `quantity`.
  2. **JSON Static Schema:** Tệp `products.json` lưu 9 sản phẩm nạp thẳng vào RAM của `productcatalogservice`, và `currency_conversion.json` lưu tỷ giá của Ngân hàng Trung ương Châu Âu (ECB).
  3. **Exact Money Model:** Mọi số tiền đều lưu bằng cấu trúc `Money {currency_code, int64 units, int32 nanos}` ($10^{-9}$) để loại bỏ hoàn toàn sai số dấu phẩy động.

## Slide 9: Security View & Concurrency View (~45 giây)
- **Lời dẫn:**
  - Về **Security View**: Hệ thống có 3 ranh giới tin cậy. Điểm sáng trong manifest là toàn bộ 12 Deployments đều bật `securityContext` rất nghiêm ngặt: `runAsNonRoot: true` (UID 1000), `readOnlyRootFilesystem: true`, và `drop: ["ALL"]` capabilities. Tuy nhiên, giao tiếp gRPC nội bộ mặc định vẫn là plaintext (`insecure.NewCredentials()`), có thể nâng cấp bằng Istio mTLS.
  - Về **Concurrency View**: Trong `RedisCartStore.AddItemAsync`, thao tác thêm giỏ hàng dùng mẫu **Read-Modify-Write** (`GetAsync` $\rightarrow$ sửa số lượng trong RAM $\rightarrow$ `SetAsync`) mà không có khóa hay Lua script, nên nếu cùng 1 user gửi 2 request song song có thể xảy ra **Lost Update**.

## Slide 10 & Slide 11: Component Mapping (Từ Sơ đồ $\rightarrow$ Code $\rightarrow$ K8s Runtime) (~60 giây)
- **Lời dẫn:** Hai slide 10 và 11 tóm tắt bảng ánh xạ đầy đủ cho từng dịch vụ từ hộp sơ đồ $\rightarrow$ hàm xử lý trong code (`file:line`) $\rightarrow$ Deployment/Service/Port trên Kubernetes:
  - Ví dụ: Hộp `frontend` ánh xạ tới `src/frontend/handlers.go` (`homeHandler` dòng 59, `placeOrderHandler` dòng 320), chạy trong `Deployment/frontend` cổng `8080`.
  - Hộp `cartservice` ánh xạ tới `RedisCartStore.cs` dòng 33 (`AddItemAsync`), kết nối biến môi trường `REDIS_ADDR=redis-cart:6379` với volume `emptyDir: {}`.
  - Hộp `checkoutservice` ánh xạ tới `src/checkoutservice/main.go` dòng 230 (`PlaceOrder`), lắng nghe gRPC cổng `5050`.

## Slide 12: Đánh đổi Kiến trúc (Trade-offs) & Kết luận (~45 giây)
- **Lời dẫn:** Cuối cùng, không có kiến trúc nào là hoàn hảo không đánh đổi:
  1. **Polyglot gRPC** mang lại hợp đồng chặt chẽ và hiệu năng HTTP/2 cao, nhưng buộc phải có tầng `frontend` chuyển đổi HTTP/1.1 sang gRPC và gây hiện tượng gọi lặp N+1 RPC khi quy đổi tiền tệ.
  2. **Synchronous Orchestrator (`checkoutservice`)** giúp code dễ đọc và trả kết quả đặt hàng tức thì, nhưng tạo ra phụ thuộc thời gian chạy vào 5 dịch vụ con và chưa có cơ chế hoàn tiền bù trừ (Saga Compensation) nếu bước giao hàng lỗi sau khi đã trừ tiền.
  3. **Stateless Checkout & In-Memory JSON** giúp triển khai Kubernetes cực gọn nhẹ, đổi lại đơn hàng chỉ là bản chụp tạm thời (`OrderResult`) không lưu lịch sử lâu dài.
- Em xin kết thúc phần trình bày lý thuyết và chuyển sang phần Live Demo trực tiếp trên cụm Kubernetes. Cảm ơn thầy và các bạn đã lắng nghe!
