# Kiến thức áp dụng — Online Boutique

## Phạm vi kiến thức & Công nghệ

Microservices Architecture, Inter-service gRPC/Protobuf Communication, Database-per-service Pattern (Redis Cache), Synchronous Service Orchestration, Kubernetes Workload Modeling (Pods, Deployments, Services, ConfigMaps, Probes).

---

## 1. Các khái niệm cốt lõi & Vấn đề giải quyết

### 1.1. Microservices Decomposition & Bounded Contexts
- **Vấn đề giải quyết**: Tránh kiến trúc Monolith cồng kềnh, nơi các domain nghiệp vụ (Catalog, Cart, Checkout, Shipping, Payment) phụ thuộc lẫn nhau trong cùng một runtime process và cơ sở dữ liệu dùng chung.
- **Cách áp dụng trong Online Boutique**:
  - Tách hệ thống thành 11 dịch vụ độc lập phân theo Business Capabilities (`cartservice`, `productcatalogservice`, `checkoutservice`, `paymentservice`, `shippingservice`, `emailservice`,...).
  - Mỗi dịch vụ sở hữu codebase, runtime độc lập (đa ngôn ngữ: Go, C#, Node.js, Python, Java) và tự chịu trách nhiệm về dữ liệu/logic của mình.

### 1.2. gRPC & Protocol Buffers (Protobuf) Contracts
- **Vấn đề giải quyết**: Giảm overhead chuyển đổi dữ liệu và kích thước payload của REST/JSON, đồng thời bắt buộc tính tương thích ngược và tính nhất quán của Interface giữa các đội phát triển.
- **Cách áp dụng**:
  - File định nghĩa hợp đồng chung: [`protos/demo.proto`](../source/src/checkoutservice/genproto/demo.pb.go).
  - Tận dụng HTTP/2 multiplexing, nhị phân hóa (Binary encoding) giúp thông lượng cao và độ trễ thấp khi các microservice gọi chéo lẫn nhau.

### 1.3. State Management & Database-per-service (Redis)
- **Vấn đề giải quyết**: Loại bỏ shared database bottleneck; đảm bảo tính độc lập và khả năng mở rộng riêng biệt của dữ liệu giỏ hàng.
- **Cách áp dụng**:
  - `cartservice` (viết bằng C#/.NET) sử dụng **Redis** làm in-memory key-value data store để lưu trữ giỏ hàng theo session người dùng.
  - Các service khác (như `frontend` hay `checkoutservice`) muốn đọc hoặc xóa giỏ hàng bắt buộc phải gọi RPC `GetCart` hoặc `EmptyCart` tới `cartservice`, hoàn toàn không có quyền kết nối trực tiếp vào Redis.

### 1.4. Synchronous Orchestration (Checkout Workflow)
- **Vấn đề giải quyết**: Điều phối quy trình nghiệp vụ phức tạp gồm nhiều bước (kiểm tra tồn kho, tính thuế/phí giao hàng, thanh toán tiền thẻ, vận chuyển và gửi email xác nhận).
- **Cách áp dụng**:
  - `checkoutservice` đóng vai trò là **Saga / Transaction Orchestrator**: trực tiếp gọi tuần tự tới các service downstream qua gRPC trong hàm `PlaceOrder`.

---

## 2. Quality Attributes được cải thiện & Trade-offs (Đánh đổi)

### 2.1. Thuộc tính chất lượng (Quality Attributes)
- **Scalability (Khả năng mở rộng)**: Cho phép co giãn độc lập (ví dụ: `frontend` nhận traffic lớn từ web có thể scale lên 5-10 pods, trong khi `shippingservice` chỉ cần 1-2 pods).
- **Fault Isolation (Cách ly lỗi)**: Nếu `recommendationservice` hoặc `emailservice` bị lỗi, chức năng mua hàng cốt lõi (Checkout) vẫn có thể xử lý fallback mà không làm sập toàn bộ ứng dụng.
- **Maintainability & Tech Diversity**: Các nhóm có quyền tự do lựa chọn ngôn ngữ và thư viện tối ưu nhất cho từng tác vụ chuyên biệt.

### 2.2. Chi phí & Đánh đổi (Trade-offs)
- **Cascading Latency**: Vì `checkoutservice` áp dụng cơ chế điều phối đồng bộ (Synchronous RPC chain), độ trễ của cả giao dịch là tổng độ trễ của tất cả các service thành phần:
  $$\text{Latency}_{\text{checkout}} = T_{\text{cart}} + T_{\text{catalog}} + T_{\text{shipping}} + T_{\text{payment}} + T_{\text{email}}$$
- **Data Consistency (Tính nhất quán dữ liệu)**: Không có ACID transaction xuyên suốt nhiều database/service; nếu thanh toán thành công nhưng gửi hàng hoặc gửi email lỗi, hệ thống phải xử lý bù trừ (Compensating actions) thủ công hoặc chấp nhận trạng thái bất toàn diện.
- **Operational Complexity**: Việc quản lý 11 deployments, cấu hình mạng, DNS, giám sát log phân tán đòi hỏi hạ tầng Kubernetes và công cụ observability mạnh mẽ.

---

## 3. Câu hỏi vấn đáp mẫu & Bằng chứng thực tế

> **Q1: Tại sao `checkoutservice` không dùng Event-Driven (Kafka/RabbitMQ) mà lại dùng gRPC đồng bộ?**  
> *Trả lời*: Với quy trình checkout người dùng cần biết kết quả thanh toán ngay lập tức trên giao diện web (Immediate Feedback: Order ID, Confirmation). gRPC đồng bộ giúp code đơn giản, phản hồi tức thời. Tuy nhiên nhược điểm là nếu downstream service bị nghẽn thì request checkout sẽ bị timeout hoặc chậm trễ.

> **Q2: Pod của `cartservice` gặp sự cố thì dữ liệu giỏ hàng có bị mất không?**  
> *Trả lời*: Không bị mất, vì `cartservice` là stateless worker; toàn bộ state giỏ hàng được lưu trữ tại Redis service (`redis-cart`). Khi pod `cartservice` restart, nó kết nối lại vào Redis thông qua biến môi trường `REDIS_ADDR` và tiếp tục phục vụ bình thường.
