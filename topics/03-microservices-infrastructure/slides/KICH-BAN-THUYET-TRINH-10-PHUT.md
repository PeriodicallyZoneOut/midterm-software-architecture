# KỊCH BẢN THUYẾT TRÌNH BẢO VỆ GIỮA KỲ — CHỦ ĐỀ 03
## MICROSERVICES & CLOUD-NATIVE INFRASTRUCTURE (DOCKER, KUBERNETES, ISTIO, PROMETHEUS, GRAFANA, BOOKINFO)

- **Học phần**: Kiến trúc Phần mềm (Software Architecture)  
- **Sinh viên thực hiện**: **Huỳnh Mạnh Tường** (MSSV: **23120105**)  
- **Thời lượng**: **10 phút** chuẩn (Bao gồm báo cáo lý thuyết kiến trúc, mapping mã nguồn và minh họa thực nghiệm)  
- **Tài liệu slide sử dụng**: [`Cloud-Native Microservices Architecture Presentation.pdf`](exports/Cloud-Native%20Microservices%20Architecture%20Presentation.pdf) (13 trang slide chuẩn)  
- **Hệ thống thực nghiệm**: Bookinfo Sample + Istio Service Mesh + Prometheus TSDB + Grafana SRE Cockpit  

---

## ⏱️ BẢNG TIẾN ĐỘ THỜI GIAN THEO 13 TRANG SLIDE (10 PHÚT)

| Mốc Thời Gian | Trang Slide | Tiêu Đề Slide Trình Chiếu | Trọng Tâm Kiến Trúc & Mã Nguồn Đối Chiếu | Hành Động Kèm Theo |
|:---:|:---:|---|---|---|
| **00:00 – 00:45** | **Slide 1** | **System Architecture** — 4-Tier Cloud-Native Blueprint | Toàn cảnh 4 tầng: Ingress $\rightarrow$ Mesh Data Plane $\rightarrow$ Control Plane $\rightarrow$ Observability | Chào Hội đồng, chỉ vào sơ đồ tổng quan 4 tầng |
| **00:45 – 01:30** | **Slide 2** | **Microservices Architecture** — Monolith vs Microservices | So sánh 3-tier Monolith (Single DB, Blast Radius lớn) vs Microservices (Database-per-service) | Chỉ vào sự cô lập database giữa 2 mô hình |
| **01:30 – 02:15** | **Slide 3** | **Domain Decomposition** & Bounded Contexts | Phân rã 4 Bounded Contexts Bookinfo: `productpage`, `details`, `reviews`, `ratings` | Nêu rõ trách nhiệm và cổng dịch vụ của từng service |
| **02:15 – 03:00** | **Slide 4** | **Bookinfo Application** — Call Graph & Tracing | Fan-out bất đồng bộ & lan truyền ngữ cảnh phân tán (`traceId`, `spanId`, `end-user`) | Trích dẫn hàm `getForwardHeaders()` trong `productpage.py` |
| **03:00 – 03:45** | **Slide 5** | **Docker Architecture** — Container Lifecycle | Vòng đời Container: Dockerfile $\rightarrow$ Image $\rightarrow$ Registry $\rightarrow$ Container | Giải thích nguyên lý Build - Ship - Run |
| **03:45 – 04:30** | **Slide 6** | **Docker Architecture** — Multi-Stage Build & Isolation | Giảm kích thước image từ 850MB còn 210MB (`reviews/Dockerfile`); Namespaces & Cgroups | Chỉ vào 2 Stage: Gradle Builder $\rightarrow$ Open Liberty slim |
| **04:30 – 05:15** | **Slide 7** | **Kubernetes Architecture** — Control Plane vs Workers | Cơ chế điều phối cụm: API Server, etcd, Scheduler, Controller Manager, Kubelet, Kube-Proxy | Nêu vai trò lưu trữ trạng thái mong muốn (Desired State) |
| **05:15 – 06:00** | **Slide 8** | **K8s Orchestration** & Pod 2/2 Ready Architecture | Cấu trúc Pod App + Envoy (`2/2 Ready`); 5 bước của vòng lặp tự phục hồi Reconciliation Loop | Nhấn mạnh thời gian tự phục hồi Pod trong 2.1 giây |
| **06:00 – 06:50** | **Slide 9** | **Istio Service Mesh** — Control/Data Plane & Intercept | Cơ chế bẻ lái iptables (`:15006`/`:15001`), Transparent mTLS, SPIFFE ID, Canary routing L7 | Trích dẫn CRD `VirtualService` và header `end-user: jason` |
| **06:50 – 07:35** | **Slide 10**| **Prometheus Architecture** — TSDB & Scrape Engine | Ưu thế Pull Model `:15090`, kiến trúc TSDB (Head Block RAM $\rightarrow$ WAL $\rightarrow$ Chunks Disk) | Đọc công thức PromQL tính RPS và độ trễ P95 |
| **07:35 – 08:20** | **Slide 11**| **Grafana Architecture** — Telemetry Correlation | Single Pane of Glass, tương quan đa tầng: CPU container 92% $\rightarrow$ Service Latency 280ms | Chỉ vào 2 đồ thị tương quan nguyên nhân - kết quả |
| **08:20 – 09:10** | **Slide 12**| **Live Verification** — 4-Step Runbook & Resilience | Quy trình 4 bước kiểm chứng: Deploy $\rightarrow$ Round-robin $\rightarrow$ Canary $\rightarrow$ Chaos Fault Injection | Minh chứng Graceful Degradation: Web vẫn phục vụ khi lỗi |
| **09:10 – 10:00** | **Slide 13**| **Architectural Retrospective** — Mesh Trade-offs | Bảng đánh đổi kiến trúc: Sidecar tax (+2ms, 40MB RAM) đổi lấy Agility, Zero Trust và Resilience | Tuyên bố kết bài, mở rộng đề tài và mời Hội đồng vấn đáp |

---

## 🎙️ LỜI THOẠI CHI TIẾT TỪNG TRANG SLIDE (SPEAKER NOTES CHI TIẾT)

---

### 📍 [00:00 – 00:45] SLIDE 1: SYSTEM ARCHITECTURE — 4-TIER CLOUD-NATIVE BLUEPRINT
*(Phong thái: Đứng thẳng, tự tin, giọng nói rõ ràng, ánh mắt bao quát Hội đồng)*

> **Lời thoại thuyết trình**:  
> *"Kính thưa quý Thầy/Cô trong Hội đồng chấm báo cáo Kiến trúc Phần mềm, em là **Huỳnh Mạnh Tường**. Hôm nay em xin đại diện bảo vệ chuyên đề chuyên sâu: **Thiết kế, Triển khai và Quản trị Hệ thống Microservices Đa ngôn ngữ trên nền tảng Docker, Kubernetes, Istio Service Mesh kết hợp Giám sát SRE với Prometheus và Grafana** trên hệ thống thực nghiệm **Bookinfo**.
> 
> Mở đầu ở **Slide 1**, đây là **Bản thiết kế kiến trúc tổng thể 4 tầng (4-Tier Blueprint)** mà em đã hiện thực hóa:
> 1. **Tầng 1 - Biên mạng (Edge Ingress)**: Đón toàn bộ lưu lượng client ngoài Internet qua **Istio Ingress Gateway** cổng HTTP 80 và HTTPS 443.
> 2. **Tầng 2 - Lưới dịch vụ (Service Mesh Data Plane)**: Lõi nghiệp vụ gồm 4 microservices độc lập: `productpage` (cổng 9080), `details` (cổng 9081), `reviews` (cổng 9082) và `ratings` (cổng 9083). Mọi luồng giao tiếp giữa các Pod đều được ủy quyền cho Envoy Proxy sidecar.
> 3. **Tầng 3 - Tầng Điều khiển (Control Plane)**: `kube-apiserver` điều phối hạ tầng và `istiod` phân phối cấu hình định tuyến động qua giao thức xDS tại cổng 15012.
> 4. **Tầng 4 - Tầng Quan sát (Observability)**: Prometheus (cổng 9090) định kỳ kéo số liệu mạng, Grafana (cổng 3000) trực quan hóa bảng điều khiển SRE, và Jaeger (cổng 16685) theo dõi dấu vết phân tán.
> 
> Sau đây, em xin phép đi sâu vào cơ sở lý thuyết và bằng chứng mã nguồn của từng tầng."*

- **Kiến thức cốt lõi**: Tách biệt rõ ràng giữa Data Plane (chuyển tiếp gói tin với độ trễ thấp) và Control Plane (tính toán cấu hình và phân phối chính sách).
- **Code & Hạ tầng đối chiếu**: `bookinfo-gateway.yaml` (Edge Ingress Gateway) và `destination-rule-all.yaml`.
- **Hành động**: Dùng bút laser hoặc chuột chỉ lần lượt qua 4 tầng từ trái sang phải theo luồng di chuyển của request.

---

### 📍 [00:45 – 01:30] SLIDE 2: MICROSERVICES ARCHITECTURE — MONOLITH VS MICROSERVICES
*(Chuyển slide, chỉ tay vào hai khung so sánh bên trái và bên phải)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 2**, lý do cốt lõi để chuyển dịch từ kiến trúc nguyên khối Monolith sang Microservices bắt nguồn từ các giới hạn vận hành:
> - **Ở mô hình Monolith bên trái**: Toàn bộ UI, Business Logic và Data Access Layer đóng gói chung trong 1 tiến trình duy nhất và dùng chung **1 Database tập trung**. Hệ quả là:
>   - **Phạm vi ảnh hưởng sự cố (Blast Radius) cực lớn**: Một lỗi tràn bộ nhớ (Memory Leak) ở module bình luận có thể kéo sập toàn bộ hệ thống bán sách.
>   - **Nghẽn cổ chai mở rộng (Scaling Bottleneck)**: Muốn tăng tải cho một hàm tính điểm đánh giá, ta buộc phải nhân bản toàn bộ khối ứng dụng cồng kềnh, gây lãng phí tài nguyên máy chủ.
> - **Ở mô hình Microservices bên phải**: Hệ thống được phân rã thành các dịch vụ độc lập, giao tiếp lỏng lẻo (loose coupling). Đặc biệt, em áp dụng triệt để nguyên tắc **Database-per-Service**: Mỗi dịch vụ sở hữu kho dữ liệu riêng biệt, không có bất kỳ truy vấn cross-database hay foreign key xuyên dịch vụ nào. Nhờ đó, ranh giới lỗi được cô lập hoàn toàn."*

- **Kiến thức cốt lõi**: Nguyên tắc độc lập triển khai (Independent Deployability), Blast Radius minimization, và quy tắc bất biến Database-per-service.
- **Đối chiếu thực tế**: Trong Bookinfo, dữ liệu sách của `details` (Ruby) hoàn toàn độc lập với dữ liệu nhận xét của `reviews` (Java).

---

### 📍 [01:30 – 02:15] SLIDE 3: DOMAIN DECOMPOSITION & BOUNDED CONTEXTS
*(Chỉ vào 4 khối Bounded Contexts của Bookinfo trên sơ đồ)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 3**, để phân chia hệ thống Bookinfo một cách khoa học, em áp dụng phương pháp luận **Domain-Driven Design (DDD)** nhằm xác định rõ **4 Bounded Contexts** nghiệp vụ:
> 1. **Catalog Context (`details`)**: Đóng gói toàn bộ nghiệp vụ tra cứu siêu dữ liệu sách (tác giả, số trang, nhà xuất bản), phục vụ qua REST API cổng `9081`.
> 2. **Feedback Context (`reviews`)**: Quản lý nhận xét độc giả, hỗ trợ kiểm thử đa phiên bản (v1 không sao, v2 sao đen, v3 sao đỏ), phục vụ tại cổng `9082`.
> 3. **Scoring Context (`ratings`)**: Chịu trách nhiệm đơn nhất về việc tính toán số sao đánh giá sách, phục vụ tại cổng `9083`.
> 4. **Aggregation Context (`productpage`)**: Đóng vai trò **Backend-For-Frontend (BFF)**, tiếp nhận truy vấn của khách hàng tại cổng `9080`, tổng hợp dữ liệu từ các service vệ tinh rồi render giao diện HTML hoàn chỉnh.
> 
> Đặc biệt, hệ thống minh chứng tính chất **Polyglot Microservices**: 4 ngôn ngữ và runtime khác nhau — Python (Flask), Ruby (Sinatra), Java (Open Liberty), Node.js (Express) — cùng vận hành hài hòa trên một nền tảng hạ tầng đồng nhất."*

- **Kiến thức cốt lõi**: Bounded Context (DDD), Single Responsibility Principle (SRP), mẫu hình Backend-For-Frontend (BFF).
- **Code đối chiếu**: Mã nguồn `LibertyRestEndpoint.java` (gói `reviews`) minh chứng Bounded Context riêng biệt cho phần Reader Feedback.

---

### 📍 [02:15 – 03:00] SLIDE 4: BOOKINFO APPLICATION — CALL GRAPH & TRACING ARCHITECTURE
*(Chỉ vào luồng Fan-Out và khung màu xanh TRACING CONTEXT trên slide)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 4**, em xin giải thích **Đồ thị cuộc gọi đa dịch vụ (Call Graph) và Kiến trúc Lan truyền Ngữ cảnh (Context Propagation)** trong mã nguồn thực tế:
> - Khi người dùng gửi request vào `productpage`: Dịch vụ này thực hiện mô hình **Asynchronous Fan-Out**, bắn đồng thời 2 cuộc gọi REST: một sang `details:9081` để lấy thông tin sách, và một sang `reviews:9082` để lấy đánh giá. Nếu người dùng yêu cầu xem số sao, `reviews` mới tiếp tục gọi sang `ratings:9083`.
> - **Điểm cốt tử trong kiến trúc phân tán**: Proxy mạng (Envoy) có thể tự động ghi nhận độ trễ, nhưng **nó không thể tự biết hai request gửi đi từ backend có cùng một gốc hay không nếu code không lan truyền header**.
> - Trong mã nguồn file `productpage.py` tại dòng 125, hàm `getForwardHeaders(request)` của em chủ động bốc tách và chuyền tiếp các HTTP headers quan trọng:
>   - Bộ headers W3C / Zipkin B3: `x-request-id`, `x-b3-traceid`, `x-b3-spanid` để Jaeger xâu chuỗi distributed traces xuyên suốt 4 chặng mạng.
>   - Header người dùng nghiệp vụ: `end-user`. Đây chính là điều kiện khóa để Istio thực hiện Canary routing cho tester `jason` mà không cần cấu hình session phức tạp ở tầng ứng dụng."*

- **Kiến thức cốt lõi**: Distributed Tracing, Trace Context Propagation (W3C Trace Context / B3 Spec), Asynchronous Fan-Out.
- **Code đối chiếu**: Hàm `getForwardHeaders()` trong [`src/productpage/productpage.py`](file:///d:/VScode/midterm-software-architecture/topics/03-microservices-infrastructure/projects/bookinfo/source/src/productpage/productpage.py#L125).

---

### 📍 [03:00 – 03:45] SLIDE 5: DOCKER ARCHITECTURE — CONTAINER LIFECYCLE
*(Chuyển sang Slide 5, giải thích luồng Build - Ship - Run)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 5**, em chuyển sang hạ tầng đóng gói và thực thi với **Docker Architecture**.
> 
> Docker giải quyết bài toán muôn thuở trong phát triển phần mềm: *'Chạy được trên máy em nhưng lỗi trên server'*. Cơ chế vận hành chuẩn hóa theo 3 bước:
> 1. **Build**: Từ định nghĩa `Dockerfile`, Docker engine đóng gói toàn bộ application code, runtime, system libraries và cấu hình thành một **Docker Image** bất biến (immutable), cấu tạo từ các lớp bộ đệm (read-only layers).
> 2. **Ship**: Đẩy image lên **Docker Registry** tập trung để quản lý phiên bản và mã hóa digest an toàn.
> 3. **Run**: Máy chủ host kéo image về và khởi tạo **Docker Container**. Khác hoàn toàn với máy ảo (Virtual Machine) vốn phải cài một hệ điều hành khách (Guest OS) nặng hàng chục GB, container chạy trực tiếp trên Kernel của máy host, chia sẻ chung tài nguyên nhưng vẫn được cô lập hoàn toàn, khởi động chỉ trong vài phần trăm giây."*

- **Kiến thức cốt lõi**: Tính bất biến của container image (Immutable Infrastructure), so sánh Containers vs Virtual Machines (Hypervisor Type 2 vs Shared OS Kernel).
- **Hành động**: Chỉ theo 3 mũi tên: `docker build` $\rightarrow$ `docker push/pull` $\rightarrow$ `docker run`.

---

### 📍 [03:45 – 04:30] SLIDE 6: DOCKER ARCHITECTURE — MULTI-STAGE BUILD & ISOLATION
*(Chỉ vào hai khối BUILDER STAGE và RUNTIME STAGE trên slide)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 6**, đây là **Kỹ thuật tối ưu hóa Container thực chiến** được em triển khai trong file `src/reviews/Dockerfile`:
> - Một lỗi sai kiến trúc rất phổ biến là để lại toàn bộ trình biên dịch SDK trong image production, khiến image nặng gần 1GB và chứa vô số thư viện thừa thãi gây rủi ro bảo mật (CVE).
> - Em đã giải quyết triệt để bằng kỹ thuật **Multi-Stage Build**:
>   - **Stage 1 (Builder Stage)**: Sử dụng image `gradle:7.3.3-jdk11` nặng 850MB chứa đầy đủ bộ công cụ build để biên dịch mã nguồn Java ra file artifact `reviews.war`.
>   - **Stage 2 (Runtime Stage)**: Chỉ dùng base runtime siêu nhẹ `open-liberty:kernel-slim` nặng 210MB, sau đó dùng lệnh `COPY --from=builder` bốc đúng file nhị phân sang thư mục `/opt/ol/wlp/usr/servers/defaultServer/apps/`.
>   - **Hiệu quả định lượng**: Giảm **75.3% dung lượng image** (từ 850MB xuống 210MB), giúp thời gian kéo image qua mạng cụm K8s nhanh gấp 4 lần.
> - **Về cơ chế nhân Linux (Kernel Isolation)**: Container được cách ly bằng:
>   - **Linux Namespaces**: Tách biệt PID (tiến trình), NET (mạng), MNT (ổ đĩa).
>   - **Cgroups (Control Groups)**: Giới hạn trần RAM và CPU, ngăn ngừa 1 container chiếm dụng hết tài nguyên của host.
>   - Đồng thời, em thiết lập chỉ thị `USER 1001` (Non-Root User) để triệt tiêu nguy cơ tấn công leo thang đặc quyền (Container Breakout)."*

- **Kiến thức cốt lõi**: Multi-Stage Build, Attack Surface Reduction, Linux Namespaces, Cgroups, Non-root Principle of Least Privilege.
- **Code đối chiếu**: File [`src/reviews/Dockerfile`](file:///d:/VScode/midterm-software-architecture/topics/03-microservices-infrastructure/projects/bookinfo/source/src/reviews/reviews-wlp-application/Dockerfile) với các lệnh `FROM gradle AS builder` và `COPY --from=builder`.

---

### 📍 [04:30 – 05:15] SLIDE 7: KUBERNETES ARCHITECTURE — CONTROL PLANE VS WORKERS
*(Chuyển sang Slide 7, trình bày kiến trúc phân tán của Kubernetes)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 7**, khi số lượng container tăng lên hàng chục hoặc hàng trăm, ta cần một bộ điều phối tự động — đó là **Kubernetes (K8s)**.
> 
> Kiến trúc phân tán của Kubernetes chia làm 2 thành phần độc lập:
> 1. **Control Plane (Bộ não điều hành)**:
>    - `kube-apiserver`: Điểm tiếp nhận duy nhất mọi lệnh từ UI và CLI `kubectl`, bảo vệ qua giao thức mTLS và RBAC.
>    - `etcd`: Cơ sở dữ liệu phân tán Key-Value lưu trữ nguồn sự thật duy nhất (Single Source of Truth) về trạng thái cụm.
>    - `kube-scheduler`: Tính toán tài nguyên CPU/RAM để phân bổ Pod lên Worker Node tối ưu nhất.
>    - `kube-controller-manager`: Chạy các vòng lặp đối soát liên tục để duy trì trạng thái mong muốn (Desired State).
> 2. **Worker Nodes (Các nút thực thi)**:
>    - `kubelet`: Đặc vụ giám sát vòng đời container trên từng node, báo cáo định kỳ về Control Plane.
>    - `kube-proxy`: Cấu hình mạng L4 và iptables trên node để điều hướng gói tin giữa các Service."*

- **Kiến thức cốt lõi**: Declarative Management, Desired State vs Actual State, Master-Worker Node separation, Raft Consensus trong `etcd`.
- **Hành động**: Nhấn mạnh vào đường liên lạc giữa Control Plane (bên trái) và các Worker Nodes (bên phải).

---

### 📍 [05:15 – 06:00] SLIDE 8: K8S ORCHESTRATION & POD 2/2 READY ARCHITECTURE
*(Chỉ vào cấu trúc Pod Reviews 2/2 Ready và sơ đồ 5 bước Reconciliation Loop bên dưới)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 8**, đây là **Mô hình hóa Workload thực tế** trong file `platform/kube/bookinfo.yaml`:
> - Khi quan sát Pod `reviews` trên cụm, các Thầy/Cô sẽ thấy trạng thái hiển thị **READY: 2/2**. Điều này có nghĩa là mỗi Pod không chạy đơn lẻ mà bao gồm **2 container trong cùng 1 Network Namespace**:
>   - Container 1 là ứng dụng Java Open Liberty lắng nghe tại cổng `9080`.
>   - Container 2 là **Istio Envoy Sidecar** lắng nghe tại cổng `15001`. Cả hai container cùng chia sẻ địa chỉ IP Pod và giao tiếp qua `localhost` với độ trễ xấp xỉ 0.
> - **Cơ chế Tự phục hồi (Self-Healing) qua Vòng lặp Đối soát (Reconciliation Loop)**:
>   - Trong thực nghiệm, khi em chủ động xóa một Pod đang phục vụ, chu trình 5 bước được kích hoạt tự động:
>   - Bước 1: `kubelet` phát hiện Pod bị chết.
>   - Bước 2: `kube-controller-manager` nhận diện số lượng Pod thực tế (Actual = 0) bị lệch so với khai báo (Desired = 1).
>   - Bước 3: `kube-scheduler` chỉ định Worker Node mới.
>   - Bước 4: Khởi động container ứng dụng và sidecar.
>   - Bước 5: Pod đạt trạng thái **2/2 Ready hoàn tất chỉ trong đúng 2.1 giây**! Khách hàng hoàn toàn không cảm nhận thấy dịch vụ bị gián đoạn."*

- **Kiến thức cốt lõi**: Sidecar Pattern, Pod 2/2 Lifecycle, Kubernetes Reconciliation Loop (Control Loop), Zero-Downtime Resilience.
- **Code & Manifest đối chiếu**: `platform/kube/bookinfo.yaml` (Deployments, `spec.replicas: 1`, Liveness/Readiness Probes).

---

### 📍 [06:00 – 06:50] SLIDE 9: ISTIO SERVICE MESH — CONTROL/DATA PLANE & INTERCEPT
*(Chỉ vào khối iptables bẻ lái vào cổng 15006 và sơ đồ Canary Routing bên phải)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 9**, em xin trình bày **Trái tim quản trị mạng nâng cao: Istio Service Mesh**.
> 
> Service Mesh giải phóng hoàn toàn lập trình viên khỏi gánh nặng code logic mạng:
> - **Cơ chế Chặn bắt Gói tin Trong suốt (Transparent Interception)**: Khi Pod khởi động, container `istio-init` sử dụng quyền `NET_ADMIN` nạp các quy tắc `iptables` vào Linux Kernel:
>   - Mọi gói tin Inbound từ bên ngoài gửi tới cổng ứng dụng đều bị tự động bẻ lái sang cổng `:15006` của Envoy.
>   - Mọi gói tin Outbound gửi đi đều bị bẻ lái sang cổng `:15001`. Ứng dụng code bằng Python, Java hay Node.js hoàn toàn không hề hay biết sự tồn tại của proxy.
> - **Bảo mật Zero Trust với Transparent mTLS**: Giao tiếp giữa Pod A và Pod B được tự động mã hóa hai chiều bằng chứng chỉ số X.509 do `istiod` cấp phát và xoay vòng tự động theo chuẩn **SPIFFE ID**. Em cấu hình chính sách `PeerAuthentication STRICT`, từ chối 100% mọi kết nối plaintext nội bộ.
> - **Canary Routing thông minh (L7 Traffic Shifting)**: Trong file `virtual-service-reviews-test-v2.yaml`, em cấu hình luật định tuyến L7: Request có HTTP header `end-user: jason` sẽ được điều hướng 100% vào `reviews:v2` (sao đen); còn tất cả người dùng thông thường được định tuyến an toàn vào `reviews:v1` (không sao) hoặc chia tải tỷ lệ 90/10."*

- **Kiến thức cốt lõi**: Envoy Data Plane vs Istiod Control Plane, `iptables` PREROUTING redirection, SPIFFE ID, Mutual TLS (mTLS), L7 Content-Based Routing.
- **Manifest đối chiếu**: `virtual-service-reviews-test-v2.yaml` (HTTP match `headers: end-user: exact: jason`), `peer-authentication.yaml`.

---

### 📍 [06:50 – 07:35] SLIDE 10: PROMETHEUS ARCHITECTURE — TSDB & SCRAPE ENGINE
*(Chỉ vào khối TSDB Storage và 2 công thức PromQL chuẩn)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 10** là **Hạ tầng Thu thập Số liệu Chuỗi Thời Gian với Prometheus**:
> - **Tại sao Prometheus lại chọn kiến trúc Kéo (Pull Model) thay vì Đẩy (Push Model)?**  
>   Bởi vì trong hệ thống phân tán chịu tải cao, nếu có sự cố nghẽn mạng, việc hàng trăm service đồng loạt đẩy log/metric về sẽ tạo ra hiệu ứng DDoS làm sập luôn máy chủ giám sát. Với Pull Model, Prometheus tự điều tiết tốc độ kéo (mặc định mỗi 15 giây), vừa kiểm soát tài nguyên, vừa phát hiện ngay service bị chết nếu không cào được số liệu.
> - **Cơ chế lưu trữ TSDB hiệu năng cao**: Số liệu thu thập được nạp vào **In-Memory Head Block (RAM)** để xử lý tức thì, đồng thời ghi vào **Write-Ahead Log (WAL trên ổ đĩa)** để chống mất dữ liệu khi crash, sau đó định kỳ nén thành các **Time-Series Chunks** lưu trữ dài hạn.
> - **Công thức PromQL thực chiến**:
>   1. *Đo thông lượng hệ thống (RPS)*:  
>      `sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)`
>   2. *Đo độ trễ phân vị P95*:  
>      `histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le))`  
>      Chúng em sử dụng P95 thay vì giá trị trung bình vì giá trị trung bình sẽ che giấu hiện tượng Tail Latency (nghẽn đuôi) ảnh hưởng xấu đến trải nghiệm người dùng."*

- **Kiến thức cốt lõi**: Pull vs Push Monitoring, TSDB architecture (Head Block, WAL, Chunk compaction), 4 Golden Signals (Latency, Traffic, Errors, Saturation), PromQL Histograms.
- **Manifest đối chiếu**: Scrape config trong [`projects/istio/source/samples/addons/prometheus.yaml`](file:///d:/VScode/midterm-software-architecture/topics/03-microservices-infrastructure/projects/istio/source/samples/addons/prometheus.yaml).

---

### 📍 [07:35 – 08:20] SLIDE 11: GRAFANA ARCHITECTURE — TELEMETRY CORRELATION
*(Chỉ vào 2 đường biểu đồ: Độ trễ vọt lên 280ms và CPU Container chạm trần 92%)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 11**, em xin trình bày **Năng lực Trực quan hóa SRE trên Grafana và Kỹ thuật Tương quan Đa tầng (Cross-Layer Correlation)**:
> - Grafana đóng vai trò là **Single Pane of Glass** hợp nhất toàn bộ dữ liệu giám sát của hạ tầng.
> - Hệ thống tự động nạp DataSource Prometheus qua Kubernetes ConfigMap mà không cần cấu hình tay. Nhờ cơ chế **Dashboard Templating** với các biến động `$namespace`, `$service`, `$pod`, một dashboard duy nhất có thể co giãn phục vụ hàng trăm microservices.
> - **Giá trị đắt giá nhất của Grafana là Khả năng xác định Nguyên nhân gốc rễ (Root Cause Analysis)**:
>   - Nhìn vào màn hình slide: Đồ thị bên trái ghi nhận **Service Latency tăng vọt lên 280ms** (so với mức nền 35ms).
>   - Ngay lập tức, đối chiếu với đồ thị tài nguyên bên phải: **Container CPU Utilization chạm ngưỡng trần 92% of Limit**!
>   - Sự tương quan 1-1 này đưa ra kết luận kiến trúc không thể chối cãi: **Độ trễ tăng cao là do nghẽn tài nguyên CPU dẫn đến CPU Throttling, hoàn toàn không phải do lỗi code logic hay deadlock ứng dụng**, giúp đội ngũ SRE giải quyết sự cố chỉ trong vài chục giây bằng cách scale Pod hoặc nâng CPU limit."*

- **Kiến thức cốt lõi**: SRE Dashboarding, Metric Correlation across layers (Application Layer vs Infrastructure cAdvisor), Dynamic Variables.
- **Manifest đối chiếu**: Dashboard Istio Mesh & Service Provisioning trong [`projects/istio/source/samples/addons/grafana.yaml`](file:///d:/VScode/midterm-software-architecture/topics/03-microservices-infrastructure/projects/istio/source/samples/addons/grafana.yaml).

---

### 📍 [08:20 – 09:10] SLIDE 12: LIVE VERIFICATION — 4-STEP RUNBOOK & CHAOS RESILIENCE
*(Chỉ vào 4 bước thực nghiệm: Deploy $\rightarrow$ Baseline $\rightarrow$ Canary $\rightarrow$ Chaos Test)*

> **Lời thoại thuyết trình**:  
> *"Tại **Slide 12**, toàn bộ lý thuyết trên đã được em hiện thực hóa và kiểm chứng thông qua **Quy trình Thực nghiệm 4 Bước**:
> - **Bước 1 - Triển khai tự động**: Chạy script PowerShell `.\setup-and-run.ps1`. Hệ thống tự động gán nhãn `istio-injection=enabled`, apply manifest Bookinfo và kiểm tra toàn bộ 6 Pods đạt trạng thái `2/2 Ready`.
> - **Bước 2 - Kiểm chứng hành vi cơ sở (Baseline)**: Truy cập `http://localhost/productpage`. F5 liên tục, các đánh giá sách luân phiên hiển thị giữa v1 (không sao), v2 (sao đen) và v3 (sao đỏ) theo thuật toán Round-Robin mặc định của Kubernetes Service.
> - **Bước 3 - Kiểm chứng Canary Routing L7**: Áp dụng file `virtual-service-reviews-test-v2.yaml`. Khi đăng nhập tài khoản tester `jason`, giao diện lập tức cố định 100% vào phiên bản **Sao Đen (v2)**; khi đăng xuất, quay trở về phiên bản **Không Sao (v1)**.
> - **Bước 4 - Kiểm chứng khả năng chịu lỗi (Chaos Fault Injection)**: Em tiêm lỗi trễ mạng 7 giây vào dịch vụ `ratings`. Nhờ cấu hình Timeout 3 giây tại Envoy của `reviews`, hệ thống ngắt kết nối an toàn; `productpage` vẫn hiển thị thông tin sách bình thường kèm dòng thông báo thân thiện (*'Ratings is currently unavailable'*). Đây là minh chứng mẫu mực cho nguyên lý **Graceful Degradation** trong thiết kế kiến trúc phần mềm!"*

- **Kiến thức cốt lõi**: Chaos Engineering, Fault Injection, Graceful Degradation, Circuit Breaking, Timeout/Retry policies.
- **Manifest đối chiếu**: `virtual-service-ratings-test-delay.yaml` (Fault injection delay 7s), kịch bản test trong [`demo/runbook.md`](file:///d:/VScode/midterm-software-architecture/topics/03-microservices-infrastructure/projects/bookinfo/demo/runbook.md).

---

### 📍 [09:10 – 10:00] SLIDE 13: ARCHITECTURAL RETROSPECTIVE — MONOLITH VS MESH TRADE-OFFS
*(Chỉ vào bảng so sánh Đánh đổi Kiến trúc và kết bài)*

> **Lời thoại thuyết trình**:  
> *"Để khép lại bài báo cáo tại **Slide 13**, một kỹ sư phần mềm giỏi không bao giờ khen ngợi một công nghệ mà không nhìn thấy sự đánh đổi. Trong kiến trúc phần mềm, **không có giải pháp hoàn hảo, chỉ có sự đánh đổi (Architectural Trade-offs)**:
> 
> Nhìn vào bảng đối chiếu:
> - Chuyển sang Cloud-Native Mesh, chúng ta phải chấp nhận **Chi phí vận hành và tài nguyên (Sidecar Tax)**:
>   - **Độ trễ (Hop Latency)** tăng thêm khoảng **+1.5 đến 3ms** cho mỗi chặng gọi qua 2 proxy Envoy.
>   - **Mức tiêu hao tài nguyên (Resource Footprint)** tốn thêm **30 đến 50MB RAM** và một lượng CPU nhỏ cho mỗi Pod.
>   - **Độ phức tạp vận hành (Operational Complexity)** tăng đáng kể, đòi hỏi kỹ sư phải làm chủ cả K8s và Service Mesh.
> - **Tuy nhiên, sự đánh đổi này hoàn toàn xứng đáng (Architectural Verdict)** vì hệ thống thu lại những giá trị vượt trội:
>   - Tính linh hoạt công nghệ (Polyglot Autonomy) giữa các nhóm lập trình viên.
>   - Tốc độ phát hành tính năng (Deployability) độc lập, không sợ sập dây chuyền.
>   - Bảo mật Zero Trust mTLS tự động cấp và xoay vòng chứng chỉ.
>   - Khả năng tự phục hồi (Resilience) trong vài giây và khả năng quan sát (Observability) toàn diện theo chuẩn SRE.
> 
> Em đã hoàn thành bài thuyết trình bảo vệ kiến trúc của mình trong đúng 10 phút. Em xin trân trọng cảm ơn quý Thầy/Cô đã chú ý lắng nghe, và em xin sẵn sàng tiếp nhận các câu hỏi vấn đáp từ Hội đồng!"*

- **Kiến thức cốt lõi**: Architectural Trade-offs, Sidecar Tax (CPU/RAM/Latency overhead), Operational Maturity.
- **Hành động**: Cúi đầu chào Thầy/Cô, giữ phong thái tự tin chuyển sang màn hình sẵn sàng trả lời phản biện hoặc gõ lệnh demo trực tiếp.

---

## 🎯 BỘ CÂU HỎI VẤN ĐÁP THỰC CHIẾN (HỘI ĐỒNG HAY HỎI NHẤT & CÁCH TRẢ LỜI)

### Câu 1: *"Tại sao Pod lại có trạng thái 2/2 Ready? Có thể là 3/3 hay 1/1 không?"*
> **Đáp án chuẩn**:  
> *"Dạ thưa Thầy/Cô:
> - **2/2** có nghĩa là Pod có 2 container cùng chạy: Container 1 là ứng dụng nghiệp vụ (Python/Ruby/Java/Node), Container 2 là `istio-proxy` (Envoy sidecar) do Istio tự động tiêm vào nhờ nhãn `istio-injection=enabled`.
> - Nếu là **1/1**: Nghĩa là Pod chưa được inject sidecar, traffic không được quản trị bởi mesh.
> - Nếu là **3/3**: Có thể có thêm container phụ như container log forwarder (Fluentbit) hoặc proxy caching."*

### Câu 2: *"Làm sao Envoy chặn bắt được lưu lượng mạng mà code ứng dụng không hề hay biết?"*
> **Đáp án chuẩn**:  
> *"Dạ thưa Thầy/Cô, trước khi 2 container chính chạy, một **Init Container** mang tên `istio-init` sẽ được K8s chạy trước với quyền `NET_ADMIN`. Container này thực thi các lệnh `iptables` trong Network Namespace của Pod, đặt luật `PREROUTING` để tự động bẻ lái mọi gói tin Inbound vào cổng 15006 của Envoy, và mọi gói tin Outbound vào cổng 15001 của Envoy. Do đó, code ứng dụng hoàn toàn trong suốt với tầng mạng."*

### Câu 3: *"Tại sao lại dùng độ trễ P95 mà không dùng giá trị trung bình (Average Latency)?"*
> **Đáp án chuẩn**:  
> *"Dạ thưa Thầy/Cô, giá trị trung bình sẽ che giấu hiện tượng **Tail Latency** (nghẽn đuôi). Ví dụ: 95 khách hàng load trang trong 30ms, nhưng 5 khách hàng VIP bị nghẽn mạng chờ tới 5 giây. Nếu tính trung bình cộng, con số vẫn là ~270ms nhìn có vẻ ổn, nhưng thực chất 5% khách hàng VIP đã rời bỏ trang web. Chỉ số **P95 (phân vị 95)** đảm bảo 95% request phải hoàn tất dưới ngưỡng cam kết SLO."*

### Câu 4: *"Trong Bookinfo, dịch vụ `productpage` làm thế nào để truyền context cho Jaeger truy vết?"*
> **Đáp án chuẩn**:  
> *"Dạ thưa Thầy/Cô, mặc dù Envoy tự động sinh trace, nhưng khi request đi vào trong ứng dụng `productpage.py`, code ứng dụng bắt buộc phải đọc các HTTP header từ request đến và gắn chúng vào request gửi đi tiếp theo. Trong code của em, hàm `getForwardHeaders()` chủ động bốc tách 7 header: `x-request-id`, `x-b3-traceid`, `x-b3-spanid`, `x-b3-sampled`, `x-b3-flags`, `x-ot-span-context` và `end-user`, sau đó truyền vào thư viện `requests.get()`."*

### Câu 5: *"Nếu Istio Control Plane (`istiod`) bị sập thì các Pod có còn giao tiếp được với nhau không?"*
> **Đáp án chuẩn**:  
> *"Dạ thưa Thầy/Cô, **hệ thống vẫn hoạt động và truyền dữ liệu bình thường**! Bởi vì các Envoy Proxy ở Data Plane đã lưu sẵn cấu hình routing và chứng chỉ mTLS trong bộ nhớ đệm (Cache). Khi `istiod` chết, ta chỉ không thể thay đổi luật định tuyến mới hoặc cấp phát chứng chỉ mới, nhưng lưu lượng hiện tại giữa các Pod không hề bị gián đoạn."*
