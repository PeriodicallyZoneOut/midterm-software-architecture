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
│   ├── slides.md                              # BỘ SLIDE THUYẾT TRÌNH ĐẦY ĐỦ 14 SLIDE (kèm bảng, code, mermaid)
│   ├── outline.md                             # Dàn ý chi tiết 14 slide
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

## 2. Tóm tắt Toàn bộ Bộ Slide Thuyết trình (14 Slides)

*Chi tiết toàn bộ xem tại file: [`slides/slides.md`](slides/slides.md)*

- **Slide 1: Tiêu đề & Đặt vấn đề**
  - Đặt ra 4 câu hỏi: Giao tiếp liên dịch vụ thế nào để không nghẽn? Điều phối và tự phục hồi ra sao? Bảo mật mạng nội bộ chuẩn Zero Trust bằng cách nào? Giám sát phân tán thế nào?
- **Slide 2: Monolith vs Modular Monolith vs Microservices**
  - So sánh chi tiết về Runtime process, Database ownership, Blast radius, Khả năng mở rộng (Scale) và Độ phức tạp.
  - Minh chứng tính chất **Polyglot** của Bookinfo (Python, Ruby, Java, Node.js).
- **Slide 3: Service Boundaries & Domain Decomposition**
  - Áp dụng Domain-Driven Design (DDD): Single Responsibility cho từng service (`productpage`, `details`, `reviews`, `ratings`).
  - Trách nhiệm độc lập, ranh giới rõ ràng, không xâm lấn dữ liệu của nhau.
- **Slide 4: Giao tiếp Liên Dịch vụ & Distributed Tracing Propagation**
  - Giao tiếp qua HTTP REST/JSON.
  - Lan truyền header tracing (`x-request-id`, `x-b3-traceid`, `end-user`) qua hàm `getForwardHeaders` trong `productpage.py` và JAX-RS trong `LibertyRestEndpoint.java`.
- **Slide 5: Dockerization & Multi-stage Build**
  - Linux kernel primitives: Cgroups (giới hạn CPU/RAM) và Namespaces (cách ly PID, Network, Mount).
  - Phân tích `src/reviews/Dockerfile`: Dùng Multi-stage build rút gọn image từ >800MB (Gradle + JDK) xuống còn ~150MB (Liberty kernel slim runtime).
- **Slide 6: Kubernetes Workload Modeling**
  - Các khái niệm trừu tượng: Pod (chứa App + Envoy sidecar), Deployment, ReplicaSet, ClusterIP Service.
  - Phân tách phiên bản qua nhãn: `app: reviews` dùng chung, phân biệt bằng `version: v1`, `version: v2`, `version: v3`.
- **Slide 7: Kubernetes Self-healing & Rolling Update**
  - Cơ chế Reconciliation Loop của ReplicaSet tự động phát hiện và bù đắp Pod bị xóa trong 2 giây.
  - Quy trình Zero-downtime Rolling Update: Khởi tạo Pod v mới song song, pass readiness probe mới route traffic, gửi `SIGTERM` dừng Pod cũ.
- **Slide 8: Service Mesh Architecture & Istio**
  - Lý do ra đời: Tách biệt logic mạng (mTLS, retry, timeout, telemetry, canary routing) ra khỏi mã nguồn ứng dụng.
  - Kiến trúc: **Control Plane (`istiod`)** quản lý cấu hình và cấp chứng chỉ; **Data Plane (Envoy Sidecar)** can thiệp L4/L7 traffic trong từng Pod.
- **Slide 9: Traffic Management & Canary Routing**
  - Các CRD cốt lõi: `Gateway`, `VirtualService`, `DestinationRule`.
  - Kịch bản Canary Deployment: Định tuyến theo HTTP header `end-user: jason` vào `reviews:v2` (sao đen) và phân chia tải 50/50 vào `reviews:v3` (sao đỏ).
- **Slide 10: Service Mesh Security: Zero Trust & Transparent mTLS**
  - Triết lý Zero Trust: Không tin tưởng mạng nội bộ cluster.
  - Cơ chế Transparent mTLS: Tự động bắt tay TLS giữa 2 Envoy sidecar, xác thực danh tính qua SPIFFE ID. Chế độ `PeerAuthentication` STRICT ngăn chặn kết nối không có proxy.
- **Slide 11: Cloud-Native Observability & 4 Golden Signals**
  - 3 trụ cột: **Metrics** (Phát hiện lỗi nhanh), **Logs** (Bản ghi chi tiết ngữ cảnh), **Traces** (Dấu vết hành trình phân tán).
  - 4 Golden Signals của Google SRE: Latency, Traffic, Errors, Saturation.
- **Slide 12: Prometheus Architecture & PromQL**
  - Mô hình Pull-based định kỳ cào số liệu từ cổng `:15090/stats/prometheus` của Envoy.
  - Câu lệnh PromQL đo lường thực tế: Đo RPS hệ thống, tỉ lệ phản hồi 200/500, và độ trễ P95 của dịch vụ `productpage`.
- **Slide 13: Grafana Dashboard & Kịch bản Demo**
  - Trực quan hóa dữ liệu telemetry qua Istio Mesh & Service Dashboards.
  - Sơ đồ 5 bước Demo thực tế trên máy tính (Web -> Canary -> Fault Injection -> Self-healing -> Grafana).
- **Slide 14: Tổng kết & Architectural Trade-offs**
  - Bảng đánh đổi đa chiều: Scalability & Tech Agility đối trọng với chi phí Hop Latency (+1.5–3ms), Overhead RAM/CPU của sidecar, và độ phức tạp vận hành SRE.

---

## 3. Kịch bản Trình bày & Lời thoại Thuyết trình (Speaker Notes)

*Chi tiết toàn bộ xem tại file: [`slides/speaker-notes.md`](slides/speaker-notes.md)*

### Phân bổ thời gian (Tổng cộng 12–15 phút):
1. **Phần 1: Lý thuyết Kiến trúc (5 phút — Slides 1 đến 7)**:
   - Đặt vấn đề, so sánh Monolith vs Microservices.
   - Giới thiệu Bookinfo: Hệ thống Polyglot gồm Python, Ruby, Java, Node.js.
   - Phân tích cơ chế Header propagation phục vụ tracing và routing.
   - Phân tích Docker Multi-stage build và Kubernetes Workloads (Pod, Deployment, Service).
2. **Phần 2: Hạ tầng Service Mesh & Observability (4 phút — Slides 8 đến 14)**:
   - Kiến trúc Istio: Control plane `istiod` vs Data plane Envoy.
   - Quản trị luồng thông minh với Gateway, VirtualService, DestinationRule.
   - Bảo mật Zero Trust với mTLS tự động và SPIFFE ID.
   - Giám sát 4 Golden Signals với Prometheus và Grafana.
   - Phân tích các đánh đổi kiến trúc (Trade-offs).
3. **Phần 3: Live Demo Thực tế trên Máy tính (5 phút)**:
   - Thực hiện trực tiếp 5 kịch bản theo [CHEAT-SHEET-CMD.md](CHEAT-SHEET-CMD.md).

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
