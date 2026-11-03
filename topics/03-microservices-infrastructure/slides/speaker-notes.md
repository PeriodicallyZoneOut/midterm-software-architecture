# Speaker Notes: Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana

> **Người thuyết trình**: Tường  
> **Tổng thời lượng dự kiến**: 12 – 15 phút (8–10 phút trình bày slide + 4–5 phút live demo & vấn đáp)  
> **Hệ thống minh chứng**: [Bookinfo](../../projects/bookinfo/README.md) & [Istio Service Mesh](../../projects/istio/README.md)  
> **Nguyên tắc**: Nói ngắn gọn, dứt khoát, gắn liền từng luận điểm lý thuyết với code, manifest và kịch bản thực tế của Bookinfo.

---

## Bảng phân bổ thời gian & File tham chiếu

| Slide | Chủ đề | Ý chính cần nói | File / Component cần mở | Demo / Evidence tương ứng | Thời lượng |
|---|---|---|---|---|---|
| **1** | Tiêu đề & Đặt vấn đề | Đặt ra 4 thách thức khi chuyển đổi sang Microservices: Network, Orchestration, Security, Observability. | Slide 1 | Cấu trúc Bookinfo (Python, Ruby, Java, Node.js) | 0.5 phút |
| **2** | Monolith vs Microservices | So sánh blast radius, scaling bottleneck và tính chất **Polyglot** của Bookinfo. | `src/productpage/`, `src/details/`, `src/reviews/`, `src/ratings/` | 4 thư mục source code đa ngôn ngữ | 1.0 phút |
| **3** | Service Boundaries & DDD | Bounded context, Single Responsibility Principle; độc lập lifecycle phát triển và release. | `src/reviews/.../LibertyRestEndpoint.java` | Sơ đồ Mermaid luồng gọi dữ liệu giữa 4 services | 1.0 phút |
| **4** | Giao tiếp & Tracing Propagation | HTTP REST/JSON; cơ chế forward headers (`x-request-id`, `x-b3-*`, `end-user`) qua hàm `getForwardHeaders`. | `src/productpage/productpage.py` (dòng 125) | Đoạn code trích xuất và tiêm header qua OpenTelemetry | 1.0 phút |
| **5** | Docker & Multi-stage Build | Cách ly kernel (namespace/cgroup); tối ưu kích thước image và attack surface bằng multi-stage build. | `src/reviews/Dockerfile` | So sánh Stage 1 (Gradle builder) vs Stage 2 (Liberty slim) | 1.0 phút |
| **6** | Kubernetes Workload & Labels | Pod chứa 2 container (App + Envoy); Deployment; ClusterIP Service; nhãn `app: reviews` và `version: v1/v2/v3`. | `platform/kube/bookinfo.yaml` | `kubectl get pods,svc` (hiển thị trạng thái 2/2) | 1.0 phút |
| **7** | K8s Self-healing & Rolling Update | Vòng lặp đối soát (Reconciliation loop); tự tạo lại Pod trong 2s; quy trình Zero-downtime rolling update. | `platform/kube/bookinfo.yaml` (Deployment details) | Minh họa Pod bị xóa và được tái sinh ngay lập tức | 1.0 phút |
| **8** | Service Mesh Architecture & Istio | Tách biệt Network Concern khỏi App Code; Control Plane `istiod` vs Data Plane Envoy Sidecar. | `istio-system` namespace & label `istio-injection=enabled` | `kubectl get pods -n istio-system` (istiod, ingressgateway) | 1.0 phút |
| **9** | Traffic Management & Canary | Bộ 3 CRD: Gateway, VirtualService, DestinationRule; Canary routing theo header `jason` và fault injection. | `networking/virtual-service-reviews-test-v2.yaml`, `destination-rule-all.yaml` | Cấu hình YAML VirtualService và DestinationRule | 1.0 phút |
| **10** | Mesh Security: Zero Trust & mTLS | Triết lý Zero Trust; tự động sinh SPIFFE ID; PeerAuthentication STRICT mã hóa 100% dữ liệu liên Pod. | `PeerAuthentication` manifest | SPIFFE ID trong chứng chỉ x.509 do Citadel cấp | 1.0 phút |
| **11** | Trụ cột Observability & Prometheus | Metrics vs Logs vs Traces; 4 Golden Signals (SRE); Prometheus pull model từ `:15090/stats/prometheus`; PromQL. | `samples/addons/prometheus.yaml`, Prometheus Web UI (`:9090`) | Câu lệnh PromQL đo RPS và độ trễ P95 | 1.0 phút |
| **12** | Grafana Dashboards | Trực quan hóa Telemetry của Istio Service Mesh; xem đồ thị RPS và Latency percentiles p50/p90/p99. | `samples/addons/grafana.yaml`, Grafana UI (`:3000`) | Giao diện Istio Service Dashboard | 0.5 phút |
| **13** | Kịch bản Live Demo (5 Phút) | Thực hiện 5 kịch bản: Web -> Canary Header -> Fault Injection -> Self-healing -> Grafana. | Trình duyệt + Terminal PowerShell | **Thực hiện trực tiếp 5 kịch bản theo CHEAT-SHEET-CMD.md** | 4.0 phút |
| **14** | Tổng kết & Trade-offs | Chi phí tài nguyên (sidecar 30-50MB RAM), hop latency (+1.5-3ms), gánh nặng vận hành SRE. | Bảng tổng kết trade-offs | Q&A với Thầy/Cô và các bạn trong nhóm | 1.0 phút |

---

## Chi tiết Speaker Notes theo từng Slide

### Slide 1: Giới thiệu & Đặt vấn đề
- **Lời thoại**: "Kính thưa Thầy/Cô và các bạn, hôm nay em xin đại diện nhóm trình bày Chủ đề 3: Kiến trúc Microservices, Containerization với Docker, Điều phối với Kubernetes, Quản trị luồng với Istio Service Mesh, và Giám sát với Prometheus & Grafana. Hệ thống thực nghiệm chính được em triển khai và kiểm chứng là Bookinfo — ứng dụng microservices đa ngôn ngữ chuẩn mực của Istio."

### Slide 2: Monolith vs Modular Monolith vs Microservices
- **Lời thoại**:
  - "Trong Monolith, mọi tính năng chạy chung 1 tiến trình và 1 database. Ưu điểm là triển khai ban đầu rất đơn giản, transaction tuân thủ ACID. Nhưng nhược điểm chí mạng là Blast Radius quá lớn: một lỗi rò rỉ bộ nhớ ở module phụ có thể làm sập toàn bộ hệ thống."
  - "Bookinfo giải quyết vấn đề này qua kiến trúc **Polyglot Microservices**: 4 microservices được viết bằng 4 ngôn ngữ và runtime hoàn toàn khác biệt: Python (Flask) cho `productpage`, Ruby (WEBrick) cho `details`, Java (Open Liberty) cho `reviews`, và Node.js (Express) cho `ratings`. Mỗi dịch vụ chạy trong container độc lập, tối ưu tuyệt đối theo đặc thù ngôn ngữ."

### Slide 3: Service Boundaries & Domain Decomposition
- **Lời thoại**:
  - "Mời Thầy/Cô quan sát ranh giới nghiệp vụ của Bookinfo được thiết kế theo nguyên tắc Single Responsibility của DDD. `productpage` đóng vai trò API Aggregator, `details` quản lý thông tin xuất bản, `reviews` quản lý bình luận độc giả, và `ratings` quản lý điểm số sao."
  - "Điểm mạnh kiến trúc ở đây là nhóm phát triển `reviews` có thể tự do phát triển và phát hành phiên bản mới (v2 có sao đen, v3 có sao đỏ) mà nhóm phụ trách `details` hoàn toàn không bị ảnh hưởng hay cần build lại mã nguồn."

### Slide 4: Giao tiếp Liên Dịch vụ & Lan truyền Tracing Headers
- **Hành động**: Chỉ vào hàm `getForwardHeaders` trong `productpage.py`.
- **Lời thoại**:
  - "Các service trong Bookinfo giao tiếp qua HTTP REST/JSON. Nhưng thách thức lớn của kiến trúc phân tán là: Làm sao theo dõi một request xuyên suốt 3 chặng mạng và làm sao phân loại người dùng để định tuyến?"
  - "Bookinfo giải quyết bằng cơ chế **Header Propagation**: Khi nhận request, `productpage` trích xuất các header tracing (`x-request-id`, `x-b3-*`) và đặc biệt là header danh tính người dùng `end-user` (ví dụ `jason`). Sau đó, hàm chuyển tiếp các header này sang `reviews`. Nhờ vậy, Envoy proxy mới có thể bắt được header tại tầng L7 để thực hiện Canary Routing."

### Slide 5: Dockerization & Multi-stage Build trong Java Reviews
- **Hành động**: Mở `src/reviews/Dockerfile`.
- **Lời thoại**:
  - "Để đóng gói microservice chuẩn production, chúng ta áp dụng kỹ thuật **Multi-stage Build**. Ở Stage 1, image sử dụng Gradle trên JDK 8 để biên dịch mã nguồn Java. Sang Stage 2, chỉ có file `.war` thành phẩm được copy sang runtime image siêu nhẹ Open Liberty kernel-slim."
  - "Kết quả: Kích thước image giảm từ hơn 800MB xuống còn khoảng 150MB, loại bỏ hoàn toàn compiler và source code khỏi container chạy thật, giúp thu hẹp triệt để bề mặt tấn công bảo mật."

### Slide 6: Kubernetes Workload Modeling
- **Lời thoại**:
  - "Khi triển khai lên Kubernetes, mỗi microservice được mô hình hóa thành một Deployment và một ClusterIP Service. Mời Thầy/Cô để ý: Cả 3 Deployments `reviews-v1`, `reviews-v2`, `reviews-v3` đều chia sẻ chung một Service mang nhãn `app: reviews`."
  - "Mặc định, Kubernetes Service sẽ phân phối tải Round-Robin ngẫu nhiên sang cả 3 phiên bản. Đây chính là lý do chúng ta cần đến Istio Service Mesh để kiểm soát luồng tải có chủ đích."

### Slide 7: Kubernetes Self-healing & Rolling Update
- **Lời thoại**:
  - "Kubernetes vận hành dựa trên cơ chế **Reconciliation Loop**: liên tục so sánh trạng thái thực tế (Current State) với trạng thái mong muốn (Desired State)."
  - "Trong phần live demo lát nữa, em sẽ cố tình xóa Pod `details`. Controller sẽ phát hiện ngay lập tức và tái sinh một Pod mới thay thế trong vòng 2 giây, giúp người dùng không cảm nhận bất kỳ sự gián đoạn nào (Zero Downtime)."

### Slide 8: Kiến trúc Service Mesh & Istio
- **Lời thoại**:
  - "Nếu không có Service Mesh, chúng ta sẽ phải viết mã mTLS, retry, timeout, và circuit breaker bằng cả 4 ngôn ngữ (Python, Ruby, Java, Node.js). Điều này cực kỳ tốn công và khó đồng bộ."
  - "Istio giải quyết triệt để bằng cách tách đôi kiến trúc: **Control Plane (`istiod`)** quản lý cấu hình và chứng chỉ; **Data Plane (Envoy Sidecars)** được tự động tiêm vào từng Pod, chặn bắt toàn bộ traffic qua iptables và thực thi mọi tác vụ mạng hoàn toàn độc lập với mã nguồn ứng dụng."

### Slide 9: Traffic Management & Canary Routing
- **Lời thoại**:
  - "Istio cung cấp bộ 3 Custom Resources mạnh mẽ: `Gateway` mở cổng tiếp nhận ở rìa cluster; `VirtualService` định nghĩa luật routing L7; và `DestinationRule` định nghĩa các tập con Subsets v1, v2, v3."
  - "Nhờ VirtualService, em có thể cấu hình: Mọi người dùng thông thường sẽ thấy `reviews:v1` (không sao), nhưng riêng người dùng đăng nhập `jason` sẽ được định tuyến sang `reviews:v2` (sao đen). Hoặc phân chia tỉ lệ 50% traffic sang `reviews:v3` (sao đỏ) để thử nghiệm tải diện rộng."

### Slide 10: Service Mesh Security: Zero Trust & Transparent mTLS
- **Lời thoại**:
  - "Với triết lý **Zero Trust**, chúng ta không tin tưởng mạng nội bộ cluster. Istio tự động gán cho mỗi service một danh tính duy nhất dạng SPIFFE ID và cấp phát chứng chỉ số X.509."
  - "Hai Envoy sidecar tự động thực hiện bắt tay mã hóa hai chiều (Mutual TLS) mà các lập trình viên Python, Ruby hay Java hoàn toàn không cần cấu hình chứng chỉ hay viết bất kỳ dòng code TLS nào."

### Slide 11: Cloud-Native Observability & Prometheus
- **Lời thoại**:
  - "Hệ thống giám sát áp dụng mô hình Pull-based của Prometheus. Cứ mỗi 15 giây, Prometheus sẽ chủ động cào số liệu từ cổng `:15090/stats/prometheus` của từng Envoy sidecar."
  - "Bằng ngôn ngữ truy vấn PromQL, chúng ta có thể đo đạc chính xác 4 tín hiệu vàng SRE: Lưu lượng RPS, Tỉ lệ lỗi, và Độ trễ phân tán P95/P99 qua các hàm như `rate()` và `histogram_quantile()`."

### Slide 12: Grafana Dashboards
- **Lời thoại**:
  - "Grafana đóng vai trò trực quan hóa dữ liệu telemetry thu được từ Prometheus. Bộ Dashboard của Istio cung cấp góc nhìn toàn diện từ tổng thể cluster (Istio Mesh Dashboard) đến chi tiết từng service cụ thể (Istio Service Dashboard)."

### Slide 13: Chuyển sang Live Demo Thực tế (5 Phút)
- **Lời thoại**: "Sau đây em xin phép chuyển sang màn hình Terminal và Trình duyệt để trình diễn trực tiếp 5 kịch bản thực tế trên máy tính cá nhân của em..." *(Thực hiện các thao tác theo CHEAT-SHEET-CMD.md)*.

### Slide 14: Tổng kết & Architectural Trade-offs
- **Lời thoại**:
  - "Kính thưa Thầy/Cô, không có giải pháp nào là toàn diện mà không phải đánh đổi. Khi áp dụng Kubernetes và Istio Service Mesh, chúng ta đạt được tính độc lập công nghệ, kiểm soát luồng tinh tế, bảo mật Zero Trust và khả năng quan sát vượt bậc."
  - "Tuy nhiên, cái giá phải trả là: Mỗi chặng mạng tăng thêm 1.5–3ms độ trễ qua Envoy proxy, mỗi Pod tốn thêm 30–50MB RAM, và đòi hỏi năng lực vận hành SRE cao hơn. Em xin kết thúc phần trình bày và sẵn sàng nhận câu hỏi từ Thầy/Cô!"
