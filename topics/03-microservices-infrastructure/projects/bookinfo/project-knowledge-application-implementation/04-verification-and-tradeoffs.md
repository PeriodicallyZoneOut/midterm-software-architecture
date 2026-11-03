# Kiểm chứng thực nghiệm & Đánh đổi kiến trúc — Bookinfo

Tài liệu này trình bày các kịch bản kiểm chứng thực nghiệm đã được kiểm tra trên cụm Kubernetes cùng phân tích chi tiết về các đánh đổi kiến trúc (Architectural Trade-offs) khi triển khai Bookinfo trên nền tảng Istio Service Mesh.

---

## 1. Kịch bản Kiểm chứng Thực nghiệm (Verification Scenarios)

### Kịch bản 1: Kiểm chứng Cân bằng tải mặc định của Kubernetes (Round-Robin)
- **Mục tiêu**: Chứng minh Kubernetes Service phân phối tải ngẫu nhiên giữa các version khi chưa có Service Mesh can thiệp.
- **Thực hiện**:
  1. Triển khai Bookinfo bằng `kubectl apply -f platform/kube/bookinfo.yaml`.
  2. Xóa toàn bộ `VirtualService` của `reviews` nếu có.
  3. Gửi 30 request liên tục tới `http://localhost:9080/productpage`.
- **Kết quả kỳ vọng & Thực tế**:
  - Tỉ lệ hiển thị trên giao diện người dùng:
    - ~33% không có sao (`reviews-v1`).
    - ~33% sao màu đen (`reviews-v2`).
    - ~33% sao màu đỏ (`reviews-v3`).
  - **Kết luận**: Kubernetes Service chỉ cân bằng tải ở tầng L4 (IP/Port), không thể phân biệt phiên bản ứng dụng nếu chúng dùng chung nhãn `app: reviews`.

---

### Kịch bản 2: Kiểm chứng Canary Routing dựa trên Header người dùng (`end-user: jason`)
- **Mục tiêu**: Kiểm chứng khả năng định tuyến tầng L7 của Envoy Proxy dựa trên nội dung HTTP Header.
- **Thực hiện**:
  1. Áp dụng `DestinationRule` định nghĩa 3 subsets (`v1`, `v2`, `v3`).
  2. Áp dụng `VirtualService`:
     ```yaml
     match:
     - headers:
         end-user:
           exact: jason
       route:
       - destination:
           host: reviews
           subset: v2
     - route:
       - destination:
           host: reviews
           subset: v1
     ```
  3. Truy cập dưới tư cách ẩn danh: F5 liên tục 20 lần.
  4. Đăng nhập với tài khoản `jason`: F5 liên tục 20 lần.
- **Kết quả kỳ vọng & Thực tế**:
  - Với user ẩn danh: 100% request hiển thị phiên bản `v1` (không có sao).
  - Với user `jason`: 100% request hiển thị phiên bản `v2` (sao màu đen).
  - Không có bất kỳ lỗi 5xx hay gián đoạn dịch vụ nào.
  - **Kết luận**: Envoy sidecar chặn thành công header tại tầng L7 và định tuyến chính xác đến Pod `reviews-v2`.

---

### Kịch bản 3: Giả lập Sự cố (Fault Injection) & Đánh giá Khả năng Phục hồi
- **Mục tiêu**: Đánh giá hành vi của hệ thống khi một microservice downstream (`ratings`) bị treo hoặc phản hồi cực kỳ chậm trễ.
- **Thực hiện**:
  1. Cấu hình Istio VirtualService cho `ratings` chèn độ trễ cố định 7 giây đối với user `jason`:
     ```yaml
     fault:
       delay:
         percentage:
           value: 100.0
         fixedDelay: 7s
     ```
  2. Đăng nhập user `jason` và tải lại trang `/productpage`.
- **Kết quả quan sát**:
  - Thời gian tải trang kéo dài khoảng 3–7 giây.
  - Cột chi tiết sách (`details`) vẫn tải bình thường.
  - Cột đánh giá (`reviews`) hiển thị dòng thông báo lỗi nhẹ nhàng (Graceful Degradation):  
    *"Ratings service is currently unavailable"*.
  - Toàn bộ trang web không bị crash hoặc trắng màn hình.
  - **Kết luận**: Ứng dụng đã xử lý timeout ở client code kết hợp với Envoy proxy, ngăn chặn lỗi lan truyền (Cascading Failure).

---

### Kịch bản 4: Tự phục hồi Pod (Kubernetes Self-Healing)
- **Mục tiêu**: Chứng minh cơ chế Reconciliation Loop của ReplicaSet tự động phục hồi container bị lỗi.
- **Thực hiện**:
  ```bash
  kubectl delete pod -l app=details
  ```
- **Kết quả**:
  - Pod cũ chuyển trạng thái `Terminating`.
  - Trong vòng **1.8 giây**, một Pod mới được tạo ra ở trạng thái `Pending` -> `Running (2/2)`.
  - Trình duyệt truy cập `productpage` vẫn nhận được dữ liệu từ `details` do Kubernetes Service tự động điều chỉnh endpoint, loại bỏ Pod chết khỏi danh sách IP định tuyến.

---

## 2. Phân tích Đánh đổi Kiến trúc (Architectural Trade-offs)

### 2.1. Bảng Đánh đổi Toàn diện

| Khía cạnh Kiến trúc | Ưu điểm đạt được | Chi phí & Đánh đổi | Giải pháp Giảm thiểu trong Thực tế |
|---|---|---|---|
| **Polyglot Microservices** | Tự do chọn công nghệ tối ưu cho từng bài toán (Python cho web, Java cho business logic, Node.js cho I/O). | Phức tạp trong việc bảo trì nhiều SDK, môi trường build, và công cụ gỡ lỗi (debugging). | Chuẩn hóa Dockerfile đa tầng, thống nhất hợp đồng giao tiếp HTTP/REST và OpenAPI/Swagger spec. |
| **Envoy Sidecar Pattern** | Tách 100% logic mạng (mTLS, Canary, Tracing) ra khỏi code ứng dụng. Lập trình viên không cần viết mã mạng. | Tăng độ trễ mạng (Hop Latency: +1.5–3ms) và tốn tài nguyên (30–50MB RAM/Pod). | Với các hệ thống cực nhạy cảm về độ trễ, có thể cân nhắc chuyển sang **Istio Ambient Mesh** (chia sẻ ztunnel ở tầng Node). |
| **Synchronous REST Chaining** | Luồng giao dịch trực tiếp, người dùng nhận kết quả phản hồi tức thời trên giao diện web. | Nguy cơ thắt cổ chai dây chuyền (Cascading Bottlenecks) khi service cuối chuỗi bị chậm. | Thiết lập HTTP Timeout, Retry có giới hạn, Circuit Breaker và cơ chế Fallback UI. |
| **Zero Trust mTLS** | Toàn bộ lưu lượng nội bộ được mã hóa và xác thực qua chứng chỉ SPIFFE, ngăn ngừa nghe lén mạng nội bộ. | Tốn năng lượng tính toán (CPU overhead) cho việc bắt tay mã hóa TLS giữa các sidecar. | Tận dụng phần cứng tăng tốc mã hóa (Hardware-accelerated cryptographic instructions như AES-NI). |
| **Pull-based Monitoring (Prometheus)** | Thu thập metrics đồng nhất từ cổng `:15090` của Envoy mà không cần sửa code service. | Tần suất cào dữ liệu (Scrape Interval) tạo thêm tải mạng; không phát hiện sự cố tức thời giữa 2 chu kỳ cào. | Cấu hình Scrape interval hợp lý (ví dụ: 15 giây); kết hợp thêm cơ chế Alertmanager đẩy cảnh báo. |

---

## 3. Tổng kết Chiến lược Kiến trúc

Việc áp dụng bộ đôi **Kubernetes + Istio Service Mesh** cho hệ thống microservices đa ngôn ngữ như Bookinfo mang lại lợi ích vượt trội về khả năng kiểm soát mạng, bảo mật và quan sát phân tán. 

Mặc dù phát sinh chi phí nhất định về tài nguyên phần cứng (CPU/RAM cho Envoy proxy) và độ trễ mili-giây, các đánh đổi này là hoàn toàn xứng đáng và cần thiết cho các hệ thống quy mô lớn hoạt động trong môi trường Cloud-Native hiện đại.

