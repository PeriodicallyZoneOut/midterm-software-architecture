# Kiến thức áp dụng — Bookinfo

## Phạm vi kiến thức & Công nghệ

Microservices Architecture, Polyglot Development (Python, Ruby, Java, Node.js), Kubernetes Workload Modeling (Pods, Deployments, ClusterIP Services), Istio Service Mesh (Control Plane `istiod`, Data Plane Envoy sidecar proxy, Ingress Gateway, VirtualService, DestinationRule, Canary Deployment, Fault Injection, mTLS), Cloud-Native Observability (Prometheus metric scraping, PromQL, Grafana Dashboards).

---

## 1. Các khái niệm cốt lõi & Vấn đề giải quyết

### 1.1. Phân rã Microservices & Bounded Contexts
- **Vấn đề giải quyết**: Trong kiến trúc Monolith, toàn bộ nghiệp vụ hiển thị, thông tin sách, đánh giá và chấm điểm sao nằm chung trong một codebase và runtime process duy nhất. Khi cần nâng cấp tính năng đánh giá (ví dụ thêm màu sắc sao, tích hợp AI rating), toàn bộ ứng dụng phải build lại, test lại và deploy lại, tiềm ẩn rủi ro sập toàn hệ thống (High blast radius).
- **Cách áp dụng trong Bookinfo**:
  - Hệ thống được chia thành 4 microservices độc lập theo nguyên tắc Bounded Context của Domain-Driven Design (DDD):
    1. **`productpage`**: Đóng vai trò Presentation Layer & API Aggregator, hiển thị giao diện người dùng và gọi các dịch vụ downstream.
    2. **`details`**: Quản lý thông tin xuất bản và metadata của sách.
    3. **`reviews`**: Quản lý bình luận của độc giả; hỗ trợ đa phiên bản (`v1` không sao, `v2` sao đen, `v3` sao đỏ).
    4. **`ratings`**: Quản lý điểm số xếp hạng và tương tác trực tiếp với cơ sở dữ liệu nếu cần.
  - Mỗi service có lifecycle độc lập: team phát triển `reviews` có thể deploy phiên bản v3 mà team `details` không hề bị ảnh hưởng.

### 1.2. Kiến trúc Đa ngôn ngữ (Polyglot Microservices)
- **Vấn đề giải quyết**: "One size does not fit all" — mỗi ngôn ngữ lập trình có thế mạnh riêng biệt cho từng loại tác vụ (ví dụ: Python mạnh về web rendering/AI, Java mạnh về xử lý enterprise logic tin cậy, Node.js mạnh về I/O bất đồng bộ nhẹ nhàng).
- **Cách áp dụng trong Bookinfo**:
  - `productpage`: Viết bằng **Python (Flask)** — cú pháp ngắn gọn, template engine Jinja2 tiện lợi để sinh HTML.
  - `details`: Viết bằng **Ruby (WEBrick/Sinatra)** — linh hoạt, xử lý dữ liệu cấu trúc JSON nhanh chóng.
  - `reviews`: Viết bằng **Java (Open Liberty / JAX-RS)** — kiến trúc module vững chắc, quản lý luồng tốt.
  - `ratings`: Viết bằng **Node.js (Express)** — non-blocking event-driven I/O lý tưởng cho dịch vụ tra cứu điểm số nhỏ gọn.

### 1.3. Giao tiếp liên dịch vụ & Truyền dẫn Header phân tán (Distributed Tracing Propagation)
- **Vấn đề giải quyết**: Khi một request từ người dùng đi qua chuỗi microservices phân tán (`productpage` -> `reviews` -> `ratings`), nếu có lỗi hoặc độ trễ cao, việc xác định nguyên nhân gốc rễ (Root Cause Analysis) trong hàng chục container là vô cùng khó khăn nếu không có mã định danh xuyên suốt.
- **Cách áp dụng trong Bookinfo**:
  - Các service giao tiếp với nhau qua giao thức HTTP REST/JSON.
  - Khi `productpage` nhận request từ browser, nó trích xuất và chủ động chuyển tiếp (forward) các HTTP tracing headers sang `details` và `reviews`:
    - `x-request-id`: Định danh duy nhất cho từng request.
    - `x-b3-traceid`, `x-b3-spanid`, `x-b3-sampled`: Chuẩn Zipkin/B3 tracing.
    - `end-user`: Chứa thông tin tài khoản đăng nhập (ví dụ: `jason`) phục vụ định tuyến phân tầng.
  - `reviews` tiếp tục forward các header này sang `ratings`, tạo thành một vết chuỗi (trace) liền mạch cho Envoy proxy thu thập telemetry.

### 1.4. Hạ tầng Điều phối Kubernetes (Workload Modeling)
- **Vấn đề giải quyết**: Quản lý vòng đời của hàng loạt container trên các máy chủ vật lý: tự động lập lịch (scheduling), tự phục hồi (self-healing) khi tiến trình chết, và cân bằng tải nội bộ (service discovery & internal load balancing).
- **Cách áp dụng**:
  - **Pod**: Đơn vị thực thi nhỏ nhất, trong môi trường Istio mỗi Pod chứa 2 container (`app` + `istio-proxy`).
  - **Deployment**: Quản lý số lượng bản sao (replicas) mong muốn, cung cấp khả năng Rolling Update không gián đoạn.
  - **ClusterIP Service**: Cung cấp địa chỉ IP ảo và tên miền DNS nội bộ ổn định (ví dụ: `http://reviews:9080`), tự động cân bằng tải Round-Robin tới các Pod tương ứng.

### 1.5. Istio Service Mesh — Tách biệt Logic Mạng khỏi Ứng dụng
- **Vấn đề giải quyết**: Trong microservices truyền thống, các tác vụ mạng như mTLS, retry, timeout, circuit breaking, và canary routing thường bị code cứng vào từng thư viện ứng dụng (ví dụ Netflix Ribbon/Hystrix), dẫn đến việc phải viết lại thư viện cho từng ngôn ngữ (Python, Ruby, Java, Node.js).
- **Cách áp dụng**:
  - **Control Plane (`istiod`)**: Chuyển đổi các cấu hình khai báo (CRD: VirtualService, DestinationRule) thành cấu hình Envoy và phân phối xuống các sidecar.
  - **Data Plane (Envoy Sidecar)**: Được tự động tiêm (auto-injected) vào từng Pod, can thiệp toàn bộ traffic vào/ra (Inbound/Outbound) qua `iptables`. Mọi tính năng định tuyến, bảo mật và đo lường đều thực thi tại tầng sidecar mà không cần sửa mã nguồn ứng dụng.

---

## 2. Quality Attributes được cải thiện & Trade-offs (Đánh đổi)

### 2.1. Các thuộc tính chất lượng (Quality Attributes)
- **Modifiability & Independent Deployability**: Việc nâng cấp `reviews` từ v1 lên v2 và v3 hoàn toàn tách biệt, không cần deploy lại `productpage` hay `details`.
- **Fault Tolerance & Resilience (Độ bền bỉ)**: Nhờ có timeout và fallback trong code và cấu hình Istio, sự cố chậm trễ tại `ratings` không làm sập `productpage` mà chỉ hiển thị fallback text.
- **Zero Trust Security**: Istio tự động mã hóa lưu lượng giữa các Pod bằng mutual TLS (mTLS) với chứng chỉ x.509 được cấp phát và xoay vòng định kỳ bởi `istiod`, bảo vệ dữ liệu chống nghe lén ngay cả khi mạng nội bộ cluster bị thâm nhập.
- **Observability**: Prometheus tự động thu thập Golden Signals (RPS, Error rate, Latency p50/p90/p99) trực tiếp từ Envoy proxy mà lập trình viên không phải viết code giám sát trong từng microservice.

### 2.2. Chi phí & Đánh đổi (Trade-offs)
- **Network Hop Latency**: Mỗi request đi qua thêm 2 proxy Envoy (Outbound sidecar của client + Inbound sidecar của server), làm tăng thêm khoảng $1.5 - 3\text{ ms}$ độ trễ trên mỗi chặng mạng.
- **Resource Overhead (CPU/RAM)**: Mỗi Pod phải chạy kèm một container Envoy proxy tiêu tốn thêm khoảng $30 - 50\text{ MB}$ RAM và một phần năng lực CPU cho việc mã hóa/giải mã TLS và thu thập telemetry.
- **Operational Complexity**: Đòi hỏi đội ngũ SRE phải nắm vững Kubernetes CRDs, kiến trúc Istio, cơ chế iptables và hệ thống Prometheus/Grafana.

---

## 3. Câu hỏi vấn đáp mẫu & Bằng chứng thực tế

> **Q1: Tại sao Bookinfo lại là minh chứng chuẩn mực nhất cho kiến trúc Polyglot Microservices?**  
> *Trả lời*: Bookinfo gồm 4 microservices được viết bằng 4 ngôn ngữ và runtime hoàn toàn khác nhau: Python (Flask), Ruby (WEBrick), Java (Open Liberty), và Node.js (Express). Chúng giao tiếp hoàn toàn qua giao thức mạng HTTP REST/JSON và hợp đồng dữ liệu chuẩn hóa, chứng minh tính độc lập công nghệ tuyệt đối giữa các dịch vụ.

> **Q2: Istio thực hiện Canary Routing (ví dụ user `jason` thấy reviews v2) bằng cơ chế nào?**  
> *Trả lời*: Khi user đăng nhập với tên `jason`, `productpage` gắn HTTP header `end-user: jason` vào request gửi tới `reviews`. Envoy sidecar chặn request này tại tầng L7, đối chiếu với luật cấu hình trong Istio `VirtualService` (`headers: end-user: exact: jason`). Nếu khớp, Envoy định tuyến sang subset `v2` (nhãn `version: v2` của Deployment Java có sao đen) được định nghĩa trong `DestinationRule`. Các request không có header này được định tuyến sang subset `v1`. Toàn bộ quá trình diễn ra tại tầng proxy, không cần bất kỳ dòng code logic routing nào trong ứng dụng.

