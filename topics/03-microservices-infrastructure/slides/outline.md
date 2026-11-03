# Dàn ý Slide: Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana

> **Người phụ trách**: Tường  
> **Mục tiêu**: Chuẩn bị bài thuyết trình 12–15 phút + demo vấn đáp giữa kỳ Kiến trúc Phần mềm.  
> **Projects minh chứng**: [Bookinfo](../projects/bookinfo/README.md) & [Istio + Addons](../projects/istio/README.md).

---

## Cấu trúc bài thuyết trình (14 Slides)

```text
Phần 1: Microservices Architecture & Polyglot Design (Slides 1–3)
├── Slide 1: Giới thiệu & So sánh Monolith vs Modular Monolith vs Microservices
├── Slide 2: Service Boundaries & Domain Decomposition trong Bookinfo
└── Slide 3: Giao tiếp liên dịch vụ: HTTP REST/JSON & Lan truyền Distributed Tracing Headers

Phần 2: Containerization & Kubernetes Orchestration (Slides 4–6)
├── Slide 4: Dockerization: Container, Linux Primitives & Multi-stage Build trong Java Reviews
├── Slide 5: Kubernetes Workload Modeling: Pod (App + Sidecar), Deployment, ClusterIP & Labels
└── Slide 6: Kubernetes Self-healing, Pod Scaling & Zero-downtime Rolling Update

Phần 3: Service Mesh với Istio (Slides 7–9)
├── Slide 7: Tại sao cần Service Mesh? Kiến trúc Control Plane (istiod) vs Data Plane (Envoy)
├── Slide 8: Traffic Management: Gateway, VirtualService, DestinationRule, Canary & Fault Injection
└── Slide 9: Service Mesh Security: Transparent mTLS, SPIFFE ID & Zero Trust Architecture

Phần 4: Cloud-Native Observability (Slides 10–12)
├── Slide 10: 3 Trụ cột Observability: Metrics vs Logs vs Traces & 4 Golden Signals
├── Slide 11: Prometheus Architecture: Pull-based Scraping (:15090), TSDB & PromQL
└── Slide 12: Grafana Dashboards: Trực quan hóa Telemetry của Istio Service Mesh

Phần 5: Demo Kịch bản & Đánh giá Trade-offs (Slides 13–14)
├── Slide 13: Kịch bản Demo Live: Polyglot Web -> Canary Routing -> Fault Injection -> Self-heal -> Grafana
└── Slide 14: Tổng kết & Architectural Trade-offs (Hop Latency, Resource Overhead, Operational Cost)
```

---

## Chi tiết từng Slide

### Slide 1: Đặt vấn đề & So sánh Kiến trúc (Monolith vs Modular Monolith vs Microservices)
- **Mục tiêu**: Nêu bật động lực chuyển dịch từ Monolith sang Microservices và chỉ rõ vị trí của Modular Monolith.
- **Nội dung chính**:
  - **Monolith**: Tất cả module chung 1 process, 1 database. *Ưu*: dễ phát triển ban đầu, ACID transaction đơn giản. *Nhược*: single point of failure, blast radius lớn, nghẽn scaling cục bộ, phụ thuộc tech stack đồng nhất.
  - **Modular Monolith**: Codebase chia packages/domains chặt chẽ nhưng vẫn deploy chung 1 executable process.
  - **Microservices**: Dịch vụ độc lập theo Business Capability, chạy process riêng, database-per-service, deploy & scale độc lập.
- **Bảng so sánh**: Khả năng mở rộng (Scalability), Tốc độ triển khai (Deploy velocity), Độ phức tạp vận hành (Operational complexity), Tính nhất quán dữ liệu (Data consistency).
- **Minh chứng Polyglot Bookinfo**: 4 microservices bằng 4 ngôn ngữ khác nhau: Python (Flask), Ruby (WEBrick), Java (Open Liberty), Node.js (Express).

### Slide 2: Service Boundaries & Domain Decomposition trong Bookinfo
- **Mục tiêu**: Giải thích cách chia microservice đúng chuẩn Domain-Driven Design (DDD) trong Bookinfo.
- **Nội dung chính**:
  - Khái niệm **Bounded Context** và nguyên tắc **Single Responsibility Principle** ở mức service:
    - `productpage` (Python): Web UI & API Aggregator, nhận HTTP traffic từ user, gọi `details` và `reviews`.
    - `details` (Ruby): Quản lý metadata xuất bản của sách (thể loại, số trang, nhà xuất bản, ISBN).
    - `reviews` (Java): Quản lý đánh giá của độc giả với 3 phiên bản đồng thời (v1 không sao, v2 sao đen, v3 sao đỏ).
    - `ratings` (Node.js): Quản lý điểm số xếp hạng sách (1-5 sao) do reviewer chấm điểm.
  - Ranh giới rõ ràng: Mỗi service có lifecycle phát triển và triển khai hoàn toàn độc lập.

### Slide 3: Giao tiếp Liên Dịch vụ & Lan truyền Tracing Headers
- **Mục tiêu**: Trình bày giao thức HTTP REST/JSON và cơ chế chuyển tiếp Distributed Tracing Context.
- **Nội dung chính**:
  - Giao thức HTTP REST/JSON: Đơn giản, phi trạng thái (stateless), tương thích đa ngôn ngữ tự nhiên.
  - Thách thức phân tán: Làm thế nào theo vết một request đi qua chuỗi `productpage` -> `reviews` -> `ratings`?
  - **Cơ chế Header Propagation** (`productpage.py` & `LibertyRestEndpoint.java`):
    - Chuyển tiếp các header chuẩn: `x-request-id`, `x-b3-traceid`, `x-b3-spanid`.
    - Chuyển tiếp `end-user`: Truyền thông tin danh tính đăng nhập người dùng (phục vụ Canary Routing).
  - Phân tích rủi ro: Nếu một service trong chuỗi không forward header, chuỗi trace bị đứt gãy và Istio mất khả năng định tuyến L7 theo ngữ cảnh user.

### Slide 4: Containerization & Docker Best Practices trong Bookinfo
- **Mục tiêu**: Giải thích nguyên lý đóng gói container và kỹ thuật build image chuẩn production.
- **Nội dung chính**:
  - Container vs Virtual Machine: Namespace (PID, Network, Mount) & Cgroups (giới hạn CPU/RAM) của Linux Kernel.
  - **Multi-stage Build** (Minh chứng từ `src/reviews/Dockerfile`):
    - Stage 1: Build bằng Gradle trên Alpine JDK 8 (`gradle:4.8.1-jdk8-alpine as builder`).
    - Stage 2: Chuyển file `.war` sang runtime gọn nhẹ `open-liberty:kernel-slim`.
    - Giảm kích thước image từ >800MB xuống còn ~150MB, loại bỏ hoàn toàn JDK/Gradle compiler khỏi production.
  - Tối ưu hóa các container Python, Ruby, Node.js nhỏ gọn chạy non-root.

### Slide 5: Kubernetes Core Concepts & Workload Modeling trong Bookinfo
- **Mục tiêu**: Ánh xạ kiến trúc container sang các thành phần trừu tượng của Kubernetes.
- **Nội dung chính**:
  - **Pod**: Đơn vị tính toán nhỏ nhất. Trong môi trường mesh, mỗi Pod chứa 2 container (`app` + `istio-proxy`).
  - **Deployment**: Quản lý số lượng replica mong muốn: `productpage-v1`, `details-v1`, `reviews-v1`, `reviews-v2`, `reviews-v3`, `ratings-v1`.
  - **ClusterIP Service**: Cung cấp DNS nội bộ ổn định (`http://reviews:9080`).
  - **Label Selectors & Subsets**: 3 Deployment `reviews-v1`, `reviews-v2`, `reviews-v3` đều mang nhãn chung `app: reviews`, nhưng phân biệt bởi `version: v1`, `v2`, `v3`.

### Slide 6: Kubernetes Self-healing, Pod Scaling & Rolling Updates
- **Mục tiêu**: Chứng minh khả năng tự phục hồi và cập nhật không downtime của K8s.
- **Nội dung chính**:
  - **Self-healing**: Khi Pod bị crash hoặc bị xóa (`kubectl delete pod`), ReplicaSet controller phát hiện sai lệch trạng thái (State Drift) và tự động tạo Pod mới thay thế trong 2 giây.
  - **Zero-downtime Rolling Update**:
    - Khởi tạo Pod phiên bản mới song song.
    - Kiểm tra `readinessProbe` pass mới gán IP vào Service Endpoints.
    - Gửi tín hiệu `SIGTERM` dừng Pod cũ an toàn.
  - **Pod Scaling**: Co giãn linh hoạt số bản sao của từng microservice theo tải thực tế.

### Slide 7: Giới thiệu Service Mesh & Kiến trúc Istio
- **Mục tiêu**: Phân tích vì sao cần Service Mesh ở quy mô Microservices lớn và bóc tách kiến trúc Istio.
- **Nội dung chính**:
  - Vấn đề khi Microservices tăng lên: Khó quản lý mTLS toàn diện, thiếu observability tập trung, code logic mạng (retry/circuit break) bị nhân bản ở từng service.
  - Service Mesh tách **Application Logic** khỏi **Network & Infrastructure Concerns**.
  - **Kiến trúc Istio**:
    - **Control Plane (`istiod`)**: Chuyển đổi khai báo YAML cấp cao thành cấu hình Envoy, quản lý Certificate Authority (Citadel) cấp chứng chỉ mTLS.
    - **Data Plane (Envoy Proxies)**: Chạy dưới dạng **Sidecar container** trong từng Pod, can thiệp toàn bộ traffic vào/ra.
  - So sánh: Sidecar model vs Istio Ambient Mesh (ztunnel chia sẻ ở tầng node).

### Slide 8: Traffic Management với Istio (Ingress, Routing & Resilience)
- **Mục tiêu**: Trình bày cơ chế điều khiển luồng traffic thông minh bằng Custom Resource Definitions (CRDs).
- **Nội dung chính**:
  - **Istio Ingress Gateway**: Entry point duy nhất đón public traffic từ bên ngoài cluster vào mesh qua `bookinfo-gateway.yaml`.
  - **VirtualService & DestinationRule**:
    - `VirtualService`: Định nghĩa quy tắc định tuyến L7 (URI matching, header matching, weighted distribution).
    - `DestinationRule`: Định nghĩa các Subsets (`v1`, `v2`, `v3`) dựa trên label pods.
  - **Canary Routing**: Định tuyến user `jason` vào `reviews:v2` (sao đen), các user khác vào `reviews:v1` (không sao).
  - **Traffic Shifting**: Phân bổ lưu lượng 50% vào `reviews:v1` và 50% vào `reviews:v3` (sao đỏ).
  - **Fault Injection**: Tiêm độ trễ 7 giây vào `ratings` để kiểm thử độ bền hệ thống và cơ chế fallback.

### Slide 9: Service Mesh Security: Zero Trust & Transparent mTLS
- **Mục tiêu**: Giải thích cách Istio hiện thực hóa mô hình bảo mật Zero Trust.
- **Nội dung chính**:
  - Rủi ro mạng nội bộ: Một pod bị thỏa hiệp có thể nghe lén hoặc mạo danh gửi request đến các service khác.
  - **Mutual TLS (mTLS)** tự động:
    - Istio tự sinh SPIFFE ID (dựa trên ServiceAccount) gắn vào X.509 certificate.
    - Hai Envoy sidecar tự động bắt tay và mã hóa toàn bộ dữ liệu trên đường truyền.
    - Chế độ `PeerAuthentication` STRICT: Bắt buộc 100% traffic phải có sidecar mã hóa.
  - Ứng dụng Python, Ruby, Java, Node.js không cần viết 1 dòng code mã hóa TLS.

### Slide 10: Cloud-Native Observability: Metrics, Logs & Traces
- **Mục tiêu**: Phân biệt 3 trụ cột giám sát và mối quan hệ giữa chúng trong việc định vị lỗi.
- **Nội dung chính**:
  - **Metrics**: Số liệu thống kê dạng chuỗi thời gian (Time-series) giúp phát hiện sự cố nhanh chóng ("Hệ thống có vấn đề không?").
  - **Logs**: Bản ghi sự kiện chi tiết theo ngữ cảnh ("Chuyện gì đã xảy ra tại service X lúc Y?").
  - **Traces**: Dấu vết phân tán xuyên suốt các service thông qua trace ID/span ID ("Nút thắt cổ chai nằm ở bước nào trong chuỗi gọi?").
  - Golden Signals của SRE: Latency (độ trễ), Traffic (lưu lượng RPS), Errors (tỉ lệ lỗi), Saturation (độ bão hòa tài nguyên).

### Slide 11: Prometheus: Kiến trúc, Scraping & PromQL trong Bookinfo
- **Mục tiêu**: Trình bày nguyên lý hoạt động của Prometheus trong hệ sinh thái Kubernetes.
- **Nội dung chính**:
  - **Pull Model**: Prometheus chủ động định kỳ gửi HTTP GET đến endpoint `:15090/stats/prometheus` của từng Envoy sidecar.
  - **Prometheus TSDB**: Lưu trữ chuỗi thời gian nén cao, gắn kèm các nhãn (Labels: `destination_workload`, `response_code`).
  - **PromQL cơ bản cho Bookinfo**:
    - Tính RPS: `sum(rate(istio_requests_total[1m])) by (destination_workload)`
    - Tỉ lệ lỗi: `sum(rate(istio_requests_total{response_code=~"5.*"}[1m]))`
    - Độ trễ P95: `histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le))`

### Slide 12: Grafana: Trực quan hóa & Istio Mesh Telemetry
- **Mục tiêu**: Hướng dẫn cách Grafana kết nối Prometheus DataSource và hiển thị trạng thái vận hành.
- **Nội dung chính**:
  - Grafana kết nối tới Prometheus DataSource qua HTTP API nội bộ.
  - Khảo sát các Dashboard mẫu trong Istio Addon:
    - **Istio Mesh Dashboard**: Cái nhìn tổng quan toàn cluster (Global Request Volume, Success Rate, 4xx/5xx errors).
    - **Istio Service Dashboard**: Đào sâu từng service (`productpage`, `reviews`), hiển thị inbound/outbound traffic và duration percentiles (p50, p90, p99).
    - **Istio Workload Dashboard**: Thống kê mức tiêu thụ CPU/RAM của container và proxy song song với network telemetry.

### Slide 13: Kịch bản Demo Live (Step-by-step Runbook)
- **Mục tiêu**: Trình bày kịch bản thực nghiệm trực quan trên máy để chứng minh năng lực kỹ thuật.
- **Nội dung chính**:
  - **Demo 1**: Mở Web Bookinfo (`:9080/productpage`), minh chứng kiến trúc Polyglot và cân bằng tải Round-Robin.
  - **Demo 2**: Canary Routing (khóa v1 -> route user `jason` sang v2 sao đen -> chia tải 50/50 sang v3 sao đỏ).
  - **Demo 3**: Giả lập sự cố Fault Injection (chèn delay 7s vào `ratings`, quan sát timeout và graceful degradation).
  - **Demo 4**: Kubernetes Self-healing (kill pod `details`, quan sát K8s sinh pod mới trong 2s, web không downtime).
  - **Demo 5**: Grafana & Prometheus (bơm tải 100 request, quan sát đồ thị RPS và Latency P95).

### Slide 14: Tổng kết & Architectural Trade-offs
- **Mục tiêu**: Đưa ra nhận định kỹ thuật sâu sắc, không ca ngợi một chiều mà chỉ rõ cái giá phải trả khi áp dụng Microservices & Service Mesh.
- **Nội dung chính**:
  - **Lợi ích đạt được**: Decoupling công nghệ (Polyglot), team velocity cao, tự do scale từng phần, độ bền hệ thống cao, bảo mật Zero-trust mặc định.
  - **Cái giá phải trả (Trade-offs)**:
    - *Overhead tài nguyên*: Envoy sidecar tiêu tốn thêm RAM/CPU trên từng Pod (30–50MB RAM/Pod).
    - *Network Latency*: Mỗi bước nhảy (hop) thêm ~1.5–3ms do đi qua 2 sidecars.
    - *Độ phức tạp vận hành*: Đòi hỏi kỹ năng SRE cao để quản trị K8s CRDs, cert rotation, và debug phân tán.
  - **Kết luận**: Microservices và Service Mesh mang lại giá trị vượt trội khi kiểm soát các hệ thống lớn, phức tạp.
