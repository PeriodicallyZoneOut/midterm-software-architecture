# HƯỚNG DẪN TOÀN TẬP — VẤN ĐÁP & THỰC HÀNH GIỮA KỲ

> **Người thực hiện**: Tường  
> **Chủ đề 3**: Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana  
> **Hệ thống minh chứng**: Bookinfo (Canonical Istio Polyglot Microservices Sample) + Istio Service Mesh & Observability Addons  
> **Mục tiêu**: Cẩm nang chuẩn bị 100% từ kiến thức slide, kịch bản thuyết trình, mapping source code đến câu lệnh chạy demo thực tế trên máy tính.

---

## MỤC LỤC TÀI LIỆU

1. [Sơ đồ Cấu trúc Tài liệu & Thư mục Dự án](#1-sơ-đồ-cấu-trúc-tài-liệu--thư-mục-dự-án)
2. [Tóm tắt Toàn bộ Bộ Slide Thuyết trình (14 Slides)](#2-tóm-tắt-toàn-bộ-bộ-slide-thuyết-trình-14-slides)
3. [Kịch bản Trình bày & Lời thoại Thuyết trình (Speaker Notes)](#3-kịch-bản-trình-bày--lời-thoại-thuyết-trình-speaker-notes)
4. [Bảng Ánh xạ Toàn bộ Microservices trong Bookinfo](#4-bảng-ánh-xạ-toàn-bộ-microservices-trong-bookinfo)
5. [Hướng dẫn Chạy Thực tế trên Máy tính (Step-by-Step Runbook)](#5-hướng-dẫn-chạy-thực-tế-trên-máy-tính-step-by-step-runbook)
6. [Bộ Câu hỏi Vấn đáp Giữa kỳ & Câu trả lời Mẫu (Q&A)](#6-bộ-câu-hỏi-vấn-đáp-giữa-kỳ--câu-trả-lời-mẫu-qa)

---

## 1. Sơ đồ Cấu trúc Tài liệu & Thư mục Dự án

Toàn bộ tài liệu cho phần của Tường nằm tập trung tại:
```text
topics/03-microservices-infrastructure/
├── README.md                                  # Giới thiệu tổng quan chủ đề 3
├── CHEAT-SHEET-CMD.md                         # Tóm tắt lệnh demo terminal 1 trang
├── HUONG-DAN-TOAN-TAP.md                      # Cẩm nang toàn diện vấn đáp & thực hành
├── setup-and-run.ps1                          # Script tự động triển khai K8s, Bookinfo, Mesh, Monitoring
├── slides/
│   ├── 01-microservices.md                    # Slide độc lập 1: Microservices (10 slide / 10 phút)
│   ├── 02-docker.md                           # Slide độc lập 2: Docker & Multi-stage (10 slide / 10 phút)
│   ├── 03-kubernetes.md                       # Slide độc lập 3: Kubernetes Orchestration (10 slide / 10 phút)
│   ├── 04-istio.md                            # Slide độc lập 4: Istio Service Mesh (10 slide / 10 phút)
│   ├── 05-prometheus.md                       # Slide độc lập 5: Prometheus Monitoring (10 slide / 10 phút)
│   ├── 06-grafana.md                          # Slide độc lập 6: Grafana Dashboards (10 slide / 10 phút)
│   ├── 07-bookinfo.md                         # Slide độc lập 7: Bookinfo Application (10 slide / 10 phút)
│   ├── README.md                              # Hướng dẫn xuất và trình chiếu 7 bộ slide
│   ├── slides.md                              # Bộ slide tổng hợp (tiếng Việt)
│   ├── slides-en.md                           # Bộ slide tổng hợp dịch 100% tiếng Anh
│   ├── outline.md                             # Dàn ý chi tiết slide
│   └── speaker-notes.md                       # Lời thoại mẫu từng slide & mốc chuyển live demo
└── projects/
    ├── bookinfo/                              # Hệ thống microservices đa ngôn ngữ chuẩn Istio
    │   ├── README.md                          # Giới thiệu Bookinfo
    │   ├── SOURCE-NOTES.md                    # Nguồn upstream & điểm đọc code
    │   ├── demo/runbook.md                    # Hướng dẫn chạy demo 5 phút (lệnh terminal, kịch bản test)
    │   ├── evidence/                          # Thư mục lưu log, ảnh chụp minh chứng
    │   ├── source/                            # Source code: productpage, details, reviews, ratings, manifests
    │   └── project-knowledge-application-implementation/
    │       ├── 01-concepts.md                 # Lý thuyết microservices, polyglot, mesh, metrics
    │       ├── 02-component-mapping.md        # Bảng mapping 4 microservices -> Code -> Port -> K8s
    │       ├── 03-implementation.md           # Multi-stage Dockerfile, Distributed tracing, CRDs
    │       └── 04-verification-and-tradeoffs.md # Kịch bản kiểm chứng & đánh đổi kiến trúc
    └── istio/                                 # Hệ thống Service Mesh & Observability Addons
        ├── demo/runbook.md
        ├── evidence/
        └── source/samples/addons/             # Manifests Prometheus, Grafana
```

---

## 2. Tóm tắt Toàn bộ Bộ Slide Thuyết trình

> **Bộ 7 Slide Độc Lập Cho Từng Chủ Đề (10 trang / 10 phút mỗi chủ đề)**:
> 1. [01-microservices.md](slides/01-microservices.md) · 2. [02-docker.md](slides/02-docker.md) · 3. [03-kubernetes.md](slides/03-kubernetes.md)
> 4. [04-istio.md](slides/04-istio.md) · 5. [05-prometheus.md](slides/05-prometheus.md) · 6. [06-grafana.md](slides/06-grafana.md) · 7. [07-bookinfo.md](slides/07-bookinfo.md)  
> *Chi tiết bản tổng hợp xem tại: [`slides/slides.md`](slides/slides.md) · [Bản tiếng Anh (slides-en.md)](slides/slides-en.md)*

- **Slide 1: Đặt Vấn Đề & Chuyển Dịch Sang Cloud-Native**
  - 4 câu hỏi hạ tầng: Giao tiếp mạng đa ngôn ngữ, tự phục hồi cụm K8s, bảo mật Zero Trust liên Pod, và giám sát phân tán.
- **Slide 2: Kiến Trúc Microservices & Tính Chất Polyglot**
  - Bảng so sánh 6 tiêu chí: Monolith vs Modular Monolith vs Microservices.
  - Minh chứng Polyglot 4 ngôn ngữ trong Bookinfo: Python (`productpage`), Ruby (`details`), Java (`reviews`), Node.js (`ratings`).
- **Slide 3: Phân Rã Domain (DDD) & Code Mapping trong Bookinfo**
  - Single Responsibility & Bounded Contexts. Code mapping `LibertyRestEndpoint.java`: 12-Factor App điều khiển v1/v2/v3 qua biến môi trường.
- **Slide 4: Giao Tiếp Liên Dịch Vụ & Lan Truyền Tracing Headers**
  - Phân tích hàm `getForwardHeaders` trong `productpage.py`: forward `end-user` (cho Envoy L7 routing) và `x-request-id`, `x-b3-*` (cho distributed tracing).
- **Slide 5: Containerization & Docker Multi-Stage Build**
  - Namespaces/Cgroups; phân tích `src/reviews/Dockerfile`: Stage 1 Gradle builder ➔ Stage 2 Liberty slim runtime, giảm 800MB xuống 150MB, thu hẹp bề mặt tấn công.
- **Slide 6: Kubernetes Workload Modeling & Label Selectors**
  - Pod `2/2 Running` (App + Envoy sidecar); Service ClusterIP `reviews:9080`; Label Selectors `version: v1/v2/v3`; Cân bằng tải L4 mặc định Round-Robin.
- **Slide 7: Kubernetes Self-Healing & Zero-Downtime Deployment**
  - Vòng lặp đối soát (Reconciliation Loop); kill Pod `details` tự sinh lại trong 1.8s; Rolling update với `readinessProbe` và `SIGTERM`.
- **Slide 8: Istio Service Mesh & Quản Trị Luồng (Canary Routing)**
  - Control Plane `istiod` vs Data Plane Envoy sidecar; Bộ ba CRD `Gateway`, `VirtualService`, `DestinationRule`; Canary routing header `end-user: jason`.
- **Slide 9: Bảo Mật Zero Trust Với Transparent mTLS**
  - SPIFFE ID; SDS cấp và xoay vòng chứng chỉ X.509; Transparent mTLS liên Pod; `PeerAuthentication` STRICT loại bỏ plaintext.
- **Slide 10: Giám Sát Prometheus & Grafana + Đánh Đổi Kiến Trúc**
  - Prometheus pull `:15090`; PromQL đo RPS và độ trễ P95; Grafana Dashboards; Bảng đánh đổi Hop Latency (+1.5-3ms) và RAM overhead (30-50MB/pod).

---

## 3. Kịch bản Trình bày & Lời thoại Thuyết trình (Speaker Notes)

*Chi tiết toàn bộ xem tại file: [`slides/speaker-notes.md`](slides/speaker-notes.md)*

### Phân bổ thời gian (Tổng cộng ĐÚNG 10 PHÚT):
1. **Phần 1: Báo cáo Slide & Phân tích Code (6.0 phút — Từ 0:00 đến 6:00)**:
   - Đặt vấn đề & So sánh Monolith vs Microservices (0:00 - 1:00).
   - Domain Bounded Context & Cơ chế Header Forwarding trong code (1:00 - 2:00).
   - Docker Multi-stage build & Kubernetes Workloads (Pod 2/2, Reconciliation Loop) (2:00 - 3:30).
   - Istio Mesh (Control Plane `istiod` vs Data Plane Envoy), Canary Routing & Zero Trust mTLS (3:30 - 5:00).
   - Observability với Prometheus PromQL & Grafana, phân tích Trade-offs (5:00 - 6:00).
2. **Phần 2: Live Demo Thực tế trên Máy tính (3.5 phút — Từ 6:00 đến 9:30)**:
   - Demo 1 (0.5p): Web Bookinfo & Cân bằng tải Round-Robin L4 mặc định.
   - Demo 2 (1.5p): Canary Routing theo Header user `jason` (thấy sao đen v2).
   - Demo 3 (1.0p): Kubernetes Pod Self-Healing (kill Pod `details`, tái sinh trong 1.8s, zero downtime).
   - Demo 4 (0.5p): Bơm tải & quan sát đồ thị RPS, P95 Latency trên Grafana.
3. **Phần 3: Kết bài & Chuyển sang Vấn đáp (0.5 phút — Từ 9:30 đến 10:00)**:
   - Tóm lược giá trị kiến trúc và mời Thầy/Cô đặt câu hỏi.

---

## 4. Bảng Ánh xạ Toàn bộ Microservices trong Bookinfo

*Chi tiết toàn bộ xem tại: [`projects/bookinfo/project-knowledge-application-implementation/02-component-mapping.md`](projects/bookinfo/project-knowledge-application-implementation/02-component-mapping.md)*

| STT | Microservice | Ngôn ngữ / Framework | Vị trí Source Code | Cổng Port | Kubernetes Resource | Vai trò & Đặc điểm |
|---|---|---|---|---|---|---|
| 1 | **`productpage`** | Python / Flask | `src/productpage/productpage.py` | 9080 (ClusterIP) | Deployment `productpage-v1`, Service `productpage` | Frontend UI / API Gateway Aggregator. Forward HTTP headers (`end-user`, tracing) sang `details` và `reviews`. |
| 2 | **`details`** | Ruby / WEBrick & Sinatra | `src/details/details.rb` | 9080 (ClusterIP) | Deployment `details-v1`, Service `details` | Trả về thông tin sách (thể loại, trang, NXB, ISBN). Cung cấp endpoint `/health`. |
| 3 | **`reviews-v1`** | Java / Open Liberty | `src/reviews/.../LibertyRestEndpoint.java` | 9080 (ClusterIP) | Deployment `reviews-v1`, Service `reviews` | Phiên bản cơ sở: hiển thị bình luận sách thuần text, không gọi service `ratings` (`ENABLE_RATINGS=false`). |
| 4 | **`reviews-v2`** | Java / Open Liberty | `src/reviews/.../LibertyRestEndpoint.java` | 9080 (ClusterIP) | Deployment `reviews-v2`, Service `reviews` | Phiên bản sao đen: gọi downstream sang `ratings:9080`, hiển thị 1-5 sao màu đen (`STAR_COLOR=black`). |
| 5 | **`reviews-v3`** | Java / Open Liberty | `src/reviews/.../LibertyRestEndpoint.java` | 9080 (ClusterIP) | Deployment `reviews-v3`, Service `reviews` | Phiên bản canary sao đỏ: gọi downstream sang `ratings:9080`, hiển thị 1-5 sao màu đỏ (`STAR_COLOR=red`). |
| 6 | **`ratings`** | Node.js / Express | `src/ratings/ratings.js` | 9080 (ClusterIP) | Deployment `ratings-v1`, Service `ratings` | Cung cấp điểm số đánh giá sách. Hỗ trợ giả lập độ trễ và lỗi ngắt quãng (`v-unavailable`). |

---

## 5. Hướng dẫn Chạy Thực tế trên Máy tính (Step-by-Step Runbook)

*Chi tiết toàn bộ xem tại: [`projects/bookinfo/demo/runbook.md`](projects/bookinfo/demo/runbook.md)*

### Bước 1: Khởi động tự động
Mở PowerShell tại thư mục `topics/03-microservices-infrastructure`:
```powershell
istioctl install --set profile=demo -y
.\setup-and-run.ps1
```
Chờ tất cả các Pod đạt trạng thái `2/2 Running`.

### Bước 2: Chạy 5 Kịch bản Demo Live
- **Demo 1**: `kubectl port-forward svc/productpage 9080:9080` -> Mở `http://localhost:9080/productpage` -> F5 xem tính chất Round-Robin và Polyglot.
- **Demo 2**: Khóa traffic v1 (`virtual-service-all-v1.yaml`) -> Route user `jason` sang v2 (`virtual-service-reviews-test-v2.yaml`) -> Đăng nhập `jason` thấy sao đen -> Shifting 50/50 sang v3 (`virtual-service-reviews-50-v3.yaml`) thấy sao đỏ.
- **Demo 3**: Chèn độ trễ 7s vào `ratings` (`virtual-service-ratings-test-delay.yaml`) -> Đăng nhập `jason` quan sát timeout và cơ chế fallback an toàn.
- **Demo 4**: Xóa Pod `details` (`kubectl delete pod -l app=details`) -> Xem Pod tự sinh lại trong 2s, web không downtime.
- **Demo 5**: Port forward Grafana (`3000:3000`) và Prometheus (`9090:9090`) -> Bơm tải 100 request -> Xem đồ thị RPS và Latency P95 trên Istio Service Dashboard.

---

## 6. Bộ Câu hỏi Vấn đáp Giữa kỳ & Câu trả lời Mẫu (Q&A)

### Câu 1: Tại sao Bookinfo lại là minh chứng kinh điển cho kiến trúc Polyglot Microservices?
- **Trả lời**: Bookinfo bao gồm 4 microservices được phát triển bằng 4 ngôn ngữ và runtime hoàn toàn độc lập: **Python (Flask)**, **Ruby (WEBrick)**, **Java (Open Liberty)**, và **Node.js (Express)**. Các dịch vụ này không chia sẻ bộ nhớ hay runtime process mà giao tiếp thuần túy qua giao thức HTTP REST/JSON và hợp đồng API tiêu chuẩn. Điều này chứng minh mỗi nhóm phát triển có thể tự do lựa chọn ngôn ngữ tối ưu nhất cho bài toán của mình.

### Câu 2: Tại sao trong Kubernetes, mỗi Pod trong Bookinfo lại hiển thị trạng thái `2/2 Running`?
- **Trả lời**: Trạng thái `2/2` nghĩa là trong 1 Pod có đúng 2 containers đang chạy song song:
  1. Container thứ nhất: Mã nguồn ứng dụng nghiệp vụ (`productpage`, `details`, `reviews`, hoặc `ratings`).
  2. Container thứ hai: **`istio-proxy` (Envoy)** được Istio Control Plane tự động tiêm (sidecar injection) vào nhờ nhãn `istio-injection=enabled` trên namespace default. Container Envoy này chịu trách nhiệm chặn bắt toàn bộ traffic vào/ra, thực thi mã hóa mTLS, định tuyến thông minh và thu thập telemetry.

### Câu 3: Làm thế nào mà Istio có thể định tuyến người dùng `jason` sang `reviews:v2` mà không cần sửa code Java của reviews?
- **Trả lời**:
  1. Ứng dụng `productpage` khi nhận request có đăng nhập sẽ trích xuất thông tin session và gắn HTTP header `end-user: jason` vào request gọi sang `http://reviews:9080`.
  2. Request này bị chặn lại bởi container Envoy sidecar của `productpage`.
  3. Envoy đối chiếu với luật cấu hình trong Istio `VirtualService`: quy định nếu `headers.end-user.exact == "jason"` thì chuyển tiếp tới subset `v2`.
  4. Subset `v2` được `DestinationRule` định nghĩa tương ứng với nhãn Kubernetes `version: v2`.
  5. Envoy của `productpage` trực tiếp gửi gói tin sang địa chỉ IP của Pod `reviews-v2`. Toàn bộ logic định tuyến này nằm ở tầng Proxy (Layer 7), code Java của `reviews` hoàn toàn không cần biết về logic routing này.

### Câu 4: Phân biệt sự khác nhau giữa Istio `Gateway`, `VirtualService` và `DestinationRule`?
- **Trả lời**:
  - **`Gateway`**: Cấu hình mở cổng tại biên của cụm (Edge Ingress), chỉ định cổng nào (port 80, 443), giao thức nào (HTTP, HTTPS), và tiếp nhận tên miền (hosts) nào từ ngoài Internet.
  - **`VirtualService`**: Định nghĩa luật định tuyến (Routing Rules) tầng L7: so khớp URI, Headers, Method để quyết định request sẽ được gửi tới dịch vụ đích nào và chia tỉ lệ bao nhiêu phần trăm (Weight).
  - **`DestinationRule`**: Định nghĩa chính sách áp dụng cho lưu lượng *sau khi* đã định tuyến: phân nhóm các bản sao thành các tập con (**Subsets**) dựa trên label, cấu hình thuật toán cân bằng tải (Round-robin, Least request), chính sách Circuit Breaker và chế độ mã hóa TLS.

### Câu 5: Khi áp dụng Fault Injection chèn độ trễ 7 giây vào `ratings`, tại sao `productpage` không bị treo vĩnh viễn?
- **Trả lời**:
  - Dịch vụ `reviews` có thiết lập thời gian timeout kết nối nội bộ (mặc định khoảng 2.5–3 giây).
  - Khi `ratings` bị cố tình trì hoãn 7 giây, kết nối từ `reviews` sang `ratings` sẽ bị kích hoạt timeout.
  - Code trong `LibertyRestEndpoint.java` bắt ngoại lệ `ProcessingException` và thực hiện cơ chế **Graceful Degradation (Suy thoái duyên dáng)**: trả về bài đánh giá mà không kèm phần đánh giá sao, đồng thời trả cờ báo lỗi hiển thị thông báo thân thiện cho người dùng. Điều này ngăn chặn lỗi lan truyền làm nghẽn toàn bộ chuỗi microservices.

### Câu 6: Prometheus thu thập số liệu (metrics) từ hệ thống Bookinfo bằng cách nào?
- **Trả lời**: Prometheus áp dụng mô hình **Pull-based**:
  - Định kỳ (mặc định mỗi 15 giây), Prometheus Server gửi HTTP GET request tới cổng quản trị `:15090/stats/prometheus` của từng container Envoy sidecar trong cụm.
  - Envoy proxy liên tục ghi nhận các chỉ số Golden Signals của mạng: tổng số request (`istio_requests_total`), độ trễ phân tán (`istio_request_duration_milliseconds_bucket`), và số kết nối TCP.
  - Dữ liệu thu thập được lưu trữ vào cơ sở dữ liệu chuỗi thời gian (TSDB) của Prometheus để Grafana truy vấn qua ngôn ngữ PromQL.

### Câu 7: Transparent mTLS của Istio hoạt động như thế nào và đem lại lợi ích gì?
- **Trả lời**:
  - Khi `productpage` gửi request sang `details`, traffic nội bộ bị Envoy sidecar của `productpage` chặn lại.
  - Hai Envoy sidecar (client và server) tự động thực hiện bắt tay mã hóa TLS hai chiều (**mutual TLS**), sử dụng chứng chỉ số x.509 được cấp phát tự động bởi `istiod` với định danh **SPIFFE ID**.
  - Toàn bộ dữ liệu truyền qua mạng nội bộ Kubernetes đều được mã hóa tuyệt đối mà hai ứng dụng Python và Ruby hoàn toàn không cần cấu hình chứng chỉ hay biết về TLS. Điều này hiện thực hóa mô hình bảo mật **Zero Trust** (không tin tưởng mạng nội bộ).

### Câu 8: Đánh đổi lớn nhất khi đưa Bookinfo lên nền tảng Kubernetes + Istio là gì?
- **Trả lời**: Có 3 đánh đổi cốt lõi:
  1. **Hop Latency**: Mỗi kết nối mạng phải đi qua 2 tiến trình proxy trung gian (Outbound Envoy -> Inbound Envoy), làm tăng thêm khoảng $1.5 - 3\text{ ms}$ cho mỗi chặng gọi service.
  2. **Chi phí tài nguyên**: Mỗi Pod tiêu tốn thêm khoảng $30 - 50\text{ MB}$ RAM và CPU cho container `istio-proxy`.
  3. **Độ phức tạp vận hành**: Đội ngũ kỹ sư cần kỹ năng quản trị sâu về Kubernetes CRDs, cơ chế iptables, và hạ tầng Prometheus/Grafana để khắc phục sự cố.
