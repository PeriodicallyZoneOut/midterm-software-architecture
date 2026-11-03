# Kiến thức áp dụng — Istio Service Mesh & Observability

## Phạm vi kiến thức & Công nghệ

Service Mesh Architecture, Control Plane (`istiod`), Data Plane (Envoy Sidecar Proxy), Ingress Gateway, VirtualService, DestinationRule, Traffic Management (Canary, Fault Injection, Retries, Timeouts), Zero Trust Security (SPIFFE ID, Mutual TLS `PeerAuthentication`), Cloud-Native Observability (Prometheus Metrics Scrape, PromQL, Grafana Dashboards).

---

## 1. Khái niệm cốt lõi & Vấn đề giải quyết

### 1.1. Tại sao cần Service Mesh? (Tách biệt Application Logic và Network Infrastructure)
- **Vấn đề giải quyết**: Trong hệ thống gồm nhiều microservice đa ngôn ngữ (Go, C#, Node.js, Python, Java như Online Boutique), việc cài đặt thư viện mạng (mTLS, retry, circuit breaker, metrics tracing) vào từng source code gây trùng lặp logic, khó đồng bộ phiên bản và phụ thuộc chặt vào ngôn ngữ.
- **Giải pháp**: Service Mesh đưa toàn bộ logic mạng, bảo mật và đo lường xuống hạ tầng thông qua cơ chế **Sidecar Proxy (Envoy)** can thiệp vào tầng L4/L7 của network stack.

### 1.2. Kiến trúc Istio: Control Plane vs Data Plane
- **Control Plane (`istiod`)**:
  - Đóng vai trò trung tâm điều khiển (Brain).
  - Nhận các khai báo cấu hình trừu tượng (Custom Resources - CRDs) từ Kubernetes API Server.
  - Biên dịch thành định dạng cấu hình chuẩn xDS API đẩy xuống các Envoy proxy.
  - Tích hợp CA (Certificate Authority) nội bộ để cấp phát và xoay vòng chứng chỉ số X.509 tự động.
- **Data Plane (Envoy Proxies)**:
  - Chạy kẹp nách bên trong từng Pod dưới dạng container phụ (**Sidecar**).
  - Tự động chặn (intercept) toàn bộ lưu lượng mạng ra/vào Pod bằng `iptables`.
  - Thực thi: mTLS encryption, rate limiting, routing rule, circuit breaking, thu thập telemetry metrics.

### 1.3. Bảo mật Zero Trust & Transparent mTLS
- **Vấn đề giải quyết**: Nguy cơ nghe lén (packet sniffing), mạo danh dịch vụ (spoofing) bên trong mạng nội bộ cluster (vốn thường bị xem nhẹ do quan niệm "mạng LAN an toàn").
- **Cách áp dụng**:
  - **SPIFFE ID**: Định danh dịch vụ dựa trên ServiceAccount (Ví dụ: `spiffe://cluster.local/ns/default/sa/frontend`).
  - **Mutual TLS Handshake**: Envoy ở phía gửi và Envoy ở phía nhận bắt tay xác thực 2 chiều, mã hóa toàn bộ dữ liệu truyền trên dây cáp mạng.
  - **Policy `PeerAuthentication`**:
    - `PERMISSIVE`: Cho phép cả kết nối plaintext và mTLS song song (phù hợp giai đoạn migration).
    - `STRICT`: Bắt buộc 100% traffic nội bộ phải được mã hóa mTLS; từ chối bất kỳ kết nối nào không có sidecar proxy.

### 1.4. Quản lý luồng mạng (Traffic Management)
- **Ingress Gateway**: Cổng đón duy nhất traffic ngoài Internet vào cluster, hỗ trợ TLS termination.
- **VirtualService**: Định tuyến L7 theo URI, header, method hoặc chia trọng số phần trăm traffic (**Canary Deployment**).
- **DestinationRule**: Cấu hình pool kết nối (Connection Pooling), thuật toán cân bằng tải (Round Robin, Least Connection), và phát hiện dịch vụ lỗi (Outlier Detection / Circuit Breaking).

### 1.5. Pipeline Thu thập Số liệu (Prometheus & Grafana)
- **Pull-based Metric Scraping**: Prometheus định kỳ gửi HTTP GET đến endpoint `:15090/stats/prometheus` trên Envoy sidecar để lấy số liệu mạng (RPS, lỗi, độ trễ).
- **Trực quan hóa**: Grafana lấy dữ liệu từ Prometheus thông qua PromQL và hiển thị lên các dashboard chuẩn (Istio Mesh, Istio Service, Istio Workload).

---

## 2. Quality Attributes được cải thiện & Trade-offs (Đánh đổi)

### 2.1. Quality Attributes cải thiện
- **Security (Bảo mật)**: Đạt chuẩn Zero Trust nội bộ mà không cần can thiệp một dòng code ứng dụng.
- **Observability (Khả năng quan sát)**: Thu thập tức thì 4 Golden Signals (Latency, Traffic, Errors, Saturation) trên toàn bộ hệ thống ngay khi bật mesh.
- **Maintainability & Agility**: Nâng cấp thuật toán định tuyến (Canary, Blue/Green) hoặc chính sách bảo mật mà không cần rebuild container ứng dụng.

### 2.2. Trade-offs (Chi phí phải trả)
- **Resource Footprint**: Mỗi Pod phải chạy thêm 1 container `istio-proxy`, tốn thêm ~50MB RAM và 100m CPU. Với 10-20 microservices, tổng lượng tài nguyên đội lên đáng kể.
- **Network Hop Latency**: Mỗi request nội bộ phải đi qua 2 lớp proxy (App A -> Envoy A -> Dây mạng -> Envoy B -> App B), làm tăng độ trễ từ **1.5ms đến 3ms** trên mỗi bước nhảy.
- **Operational Complexity**: Đòi hỏi kỹ sư SRE phải hiểu sâu về iptables, envoy access log, xDS sync và quản lý vòng đời chứng chỉ số.

---

## 3. Câu hỏi vấn đáp mẫu & Bằng chứng kỹ thuật

> **Q1: Phân biệt sự khác nhau giữa Kubernetes Service và Istio VirtualService?**  
> *Trả lời*: Kubernetes Service chỉ là cơ chế trừu tượng ở tầng L4 (TCP/UDP) cung cấp một IP ảo cố định (ClusterIP) và cân bằng tải ngẫu nhiên qua kube-proxy/iptables. Trong khi đó, Istio VirtualService hoạt động ở tầng L7 (Application layer), cho phép định tuyến dựa trên URL path, HTTP headers, cookies, chia phần trăm traffic (Canary: 90% v1, 10% v2) và thiết lập timeout/retry.

> **Q2: Nếu `istiod` (Control Plane) bị crash thì traffic giữa các microservice có bị gián đoạn không?**  
> *Trả lời*: **Không bị gián đoạn.** Data Plane (Envoy sidecar proxies) hoạt động hoàn toàn độc lập và đã cache toàn bộ bảng định tuyến vào bộ nhớ cục bộ. Các service vẫn gọi nhau bình thường. `istiod` chỉ cần thiết khi có sự thay đổi cấu hình mới (apply YAML mới) hoặc cấp phát/xoay vòng chứng chỉ mTLS mới.
