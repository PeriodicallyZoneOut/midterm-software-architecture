# Kịch Bản Thuyết Trình Chuẩn: 10 Slide Trong 10 Phút
# Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana, Bookinfo

> **Người thực hiện**: Tường — Báo cáo Giữa kỳ Kiến trúc Phần mềm  
> **Cấu trúc**: **10 SLIDES TƯƠNG ỨNG 10 PHÚT**  
> **Phân bổ thời gian**:
> - **Phần 1: Báo cáo 10 Slide & Mapping Code**: 6.0 phút (Từ 0:00 đến 6:00, trung bình 35–40 giây/slide)
> - **Phần 2: Live Demo Trực Tiếp Trên Máy**: 3.5 phút (Từ 6:00 đến 9:30)
> - **Phần 3: Kết Bài & Mời Vấn Đáp**: 0.5 phút (Từ 9:30 đến 10:00)

---

## ⏱️ BẢNG TIẾN ĐỘ THEO TỪNG SLIDE & MAPPING CODE

| Slide | Chủ đề Công nghệ | Thời gian | Điểm mấu chốt cần nói | File Code / Manifest cần mở |
|---|---|---|---|---|
| **Slide 1** | Tổng quan & Đặt vấn đề | **0:00 – 0:35** | 4 thách thức: Network, K8s, mTLS, Observability | Slide 1 (Hệ thống Bookinfo) |
| **Slide 2** | **Microservices** & Polyglot | **0:35 – 1:10** | Monolith vs Microservices; Polyglot 4 ngôn ngữ | Bảng đối chiếu Slide 2 |
| **Slide 3** | **Bookinfo** & DDD Boundaries | **1:10 – 1:45** | Bounded context, SRP; 12-Factor App trong code | `src/reviews/.../LibertyRestEndpoint.java` |
| **Slide 4** | **Microservices** Tracing Header | **1:45 – 2:20** | Header Forwarding: `end-user`, `x-request-id`, `x-b3-*` | `src/productpage/productpage.py` (dòng 125) |
| **Slide 5** | **Docker** & Multi-Stage Build | **2:20 – 3:00** | Cgroups/Namespaces; Gradle builder ➔ Liberty runtime | `src/reviews/Dockerfile` (Stage 1 & 2) |
| **Slide 6** | **Kubernetes** Workloads & Labels | **3:00 – 3:40** | Pod `2/2 Running` (App + Envoy); Service ClusterIP | `platform/kube/bookinfo.yaml` |
| **Slide 7** | **Kubernetes** Self-Healing | **3:40 – 4:15** | Reconciliation loop; Pod chết tự sinh trong 1.8s | `kubectl get pods -w` (Lệnh delete pod) |
| **Slide 8** | **Istio** Service Mesh & Canary | **4:15 – 5:00** | Control Plane `istiod` vs Envoy; CRD VirtualService | `networking/virtual-service-reviews-test-v2.yaml` |
| **Slide 9** | **Istio** Zero Trust & mTLS | **5:00 – 5:35** | SPIFFE ID; SDS cấp cert X.509; mTLS STRICT | `PeerAuthentication` manifest |
| **Slide 10** | **Prometheus, Grafana** & Trade-offs | **5:35 – 6:00** | Pull `:15090`; PromQL RPS/P95; Bảng đánh đổi | `samples/addons/prometheus.yaml`, Grafana :3000 |
| **DEMO** | **Live Demo Thực Tế** | **6:00 – 9:30** | **Web Round-robin ➔ Canary jason ➔ Self-heal ➔ Grafana** | Trình duyệt + Terminal PowerShell |
| **KẾT** | Kết bài & Mời vấn đáp | **9:30 – 10:00** | Tuyên bố hoàn thành 4 trụ cột kiến trúc | Quay lại slide kết |

---

## 🎙️ LỜI THOẠI CHI TIẾT TỪNG SLIDE (BẬT ĐỒNG HỒ ĐO TẬP NÓI)

### [0:00 – 0:35] SLIDE 1: ĐẶT VẤN ĐỀ & CHUYỂN DỊCH CLOUD-NATIVE
> *"Kính thưa Thầy/Cô và các bạn, em là Tường, đại diện nhóm trình bày Chủ đề 3: Kiến trúc Microservices và Hạ tầng Cloud-Native với Docker, Kubernetes, Istio Service Mesh, Prometheus và Grafana.  
> Khi chuyển dịch từ Monolith sang Microservices, chúng ta phải giải quyết 4 bài toán hạ tầng then chốt:  
> 1. Làm sao định tuyến mạng đa ngôn ngữ và phát hành Canary an toàn?  
> 2. Làm sao điều phối cụm tự phục hồi và cập nhật không downtime?  
> 3. Làm sao triển khai bảo mật Zero Trust mà không phải sửa code ứng dụng?  
> 4. Và làm sao thu thập số liệu giám sát phân tán?  
> Hệ thống thực nghiệm được em triển khai và kiểm chứng hôm nay là **Bookinfo**."*

---

### [0:35 – 1:10] SLIDE 2: KIẾN TRÚC MICROSERVICES & TÍNH CHẤT POLYGLOT
> *"So với Monolith – nơi toàn bộ tính năng chạy chung 1 tiến trình và 1 database với blast radius rất lớn, Bookinfo khắc phục triệt để bằng kiến trúc **Polyglot Microservices**: gồm 4 services độc lập được viết bằng 4 ngôn ngữ và runtime riêng biệt:  
> - `productpage` viết bằng **Python (Flask)**: Tối ưu cho render giao diện web Jinja2 và tổng hợp API.  
> - `details` viết bằng **Ruby (Sinatra)**: Phục vụ tra cứu metadata sách gọn nhẹ.  
> - `reviews` viết bằng **Java (Open Liberty)**: Nền tảng enterprise vững chắc, quản trị đa phiên bản v1, v2, v3.  
> - `ratings` viết bằng **Node.js (Express)**: I/O bất đồng bộ tối ưu cho tra cứu điểm số đánh giá.  
> Mỗi service chạy trong container riêng và sở hữu dữ liệu độc lập (Database-per-service)."*

---

### [1:10 – 1:45] SLIDE 3: DOMAIN DECOMPOSITION & CODE MAPPING TRONG BOOKINFO
> *"Hệ thống áp dụng nguyên tắc Single Responsibility của DDD để phân chia Bounded Context. Đặc biệt, mời Thầy/Cô quan sát file mã nguồn `LibertyRestEndpoint.java` của dịch vụ `reviews`:  
> Trong code, hai biến môi trường `ENABLE_RATINGS` và `STAR_COLOR` quyết định hành vi của 3 phiên bản:  
> - **v1**: `ENABLE_RATINGS = false` ➔ Trả về bài đánh giá thuần text, không có sao.  
> - **v2**: `ENABLE_RATINGS = true`, `STAR_COLOR = black` ➔ Gọi downstream sang `ratings` và hiển thị sao đen.  
> - **v3**: `ENABLE_RATINGS = true`, `STAR_COLOR = red` ➔ Gọi `ratings` và hiển thị sao đỏ.  
> Đây là minh chứng chuẩn mực của phương pháp luận **12-Factor App**: dùng chung 1 codebase Java duy nhất, hành vi các version được cấu hình hoàn toàn qua môi trường."*

---

### [1:45 – 2:20] SLIDE 4: GIAO TIẾP LIÊN DỊCH VỤ & LAN TRUYỀN TRACING HEADERS
> *(Chỉ vào file `src/productpage/productpage.py` dòng 125)*:  
> *"Các microservice giao tiếp qua HTTP REST/JSON. Khi request đi qua chuỗi `productpage` ➔ `reviews` ➔ `ratings`, làm sao Envoy proxy có thể phân loại người dùng để định tuyến L7 và làm sao công cụ tracing kết nối được chuỗi gọi?  
> Câu trả lời nằm ở hàm `getForwardHeaders`: Khi nhận request từ trình duyệt, `productpage` trích xuất và chuyển tiếp các header tracing `x-request-id`, `x-b3-*` qua OpenTelemetry, và đặc biệt là header danh tính người dùng `end-user`.  
> Nếu không forward `end-user: jason`, Envoy proxy ở tầng L7 sẽ không thể nhận diện người dùng để định tuyến Canary, và chuỗi Distributed Trace sẽ bị đứt đoạn."*

---

### [2:20 – 3:00] SLIDE 5: DOCKERIZATION & MULTI-STAGE BUILD TRONG REVIEWS
> *(Mở file `src/reviews/Dockerfile`)*:  
> *"Về đóng gói container, chúng ta áp dụng Linux Kernel Primitives: Namespaces để cách ly PID, Network, Mount; và Cgroups để áp đặt giới hạn cứng CPU/RAM limits, ngăn ngừa hiện tượng cạn kiệt tài nguyên host.  
> Đặc biệt trong `src/reviews/Dockerfile`, em áp dụng kỹ thuật **Multi-stage Build**:  
> - **Stage 1**: Sử dụng image `gradle:4.8.1-jdk8-alpine` chứa đầy đủ JDK và công cụ build để biên dịch code.  
> - **Stage 2**: Chỉ copy file `.war` thành phẩm sang runtime image siêu nhẹ `open-liberty:kernel-slim`.  
> Kết quả: Dung lượng image giảm từ **hơn 800MB** xuống còn **150MB**, loại bỏ hoàn toàn compiler và source code khỏi production, giúp thu hẹp tối đa bề mặt tấn công bảo mật."*

---

### [3:00 – 3:40] SLIDE 6: KUBERNETES WORKLOAD MODELING & LABEL SELECTORS
> *(Chỉ vào file `platform/kube/bookinfo.yaml`)*:  
> *"Khi đưa lên Kubernetes, mỗi Pod trong Bookinfo đều ở trạng thái `2/2 Running`. Nghĩa là trong 1 Pod có đúng 2 containers: 1 container app nghiệp vụ và 1 container `istio-proxy` (Envoy) được tự động tiêm qua Mutating Webhook.  
> Cả 3 Deployments `reviews-v1`, `reviews-v2`, `reviews-v3` đều chia sẻ chung một Kubernetes Service ClusterIP mang nhãn `app: reviews` trên cổng 9080.  
> Mặc định ở tầng L4, Kubernetes Service sẽ cân bằng tải Round-Robin chia đều request sang cả 3 phiên bản. Đó là lý do chúng ta cần đến Istio để kiểm soát luồng tải có chủ đích."*

---

### [3:40 – 4:15] SLIDE 7: KUBERNETES SELF-HEALING & ZERO-DOWNTIME
> *"Kubernetes vận hành dựa trên cơ chế **Reconciliation Loop**: liên tục đối soát giữa trạng thái thực tế (Current State) và trạng thái mong muốn (Desired State).  
> Khi một Pod gặp sự cố hoặc bị xóa cưỡng bức, ReplicaSet Controller phát hiện ngay lập tức và tự động khởi tạo Pod mới đạt trạng thái `2/2 Running` chỉ trong **1.8 giây**.  
> Kết hợp với `readinessProbe` và tín hiệu `SIGTERM`, quy trình rolling update và tự phục hồi của Kubernetes bảo đảm hệ thống đạt mức **Zero Downtime**, người dùng không hề gặp lỗi kết nối."*

---

### [4:15 – 5:00] SLIDE 8: ISTIO SERVICE MESH & QUẢN TRỊ LUỒNG CANARY
> *(Chỉ vào file `networking/virtual-service-reviews-test-v2.yaml`)*:  
> *"Để không phải code lại logic mạng bằng cả 4 ngôn ngữ, Istio tách đôi kiến trúc: **Control Plane (`istiod`)** tiếp nhận cấu hình YAML; còn **Data Plane (Envoy Sidecars)** chặn bắt toàn bộ traffic Inbound 15006 và Outbound 15001 qua iptables.  
> Istio cung cấp bộ ba CRD cốt lõi: `Gateway` mở cổng Ingress ở biên cụm; `VirtualService` định nghĩa luật routing L7; và `DestinationRule` định nghĩa các tập con Subsets v1, v2, v3.  
> Nhờ đó, em có thể cấu hình Canary Routing: 100% khách thông thường vào `reviews:v1` (không sao); nhưng riêng người dùng đăng nhập `jason` sẽ được Envoy tự động điều hướng sang `reviews:v2` (sao đen) mà code Java không cần sửa một dòng nào."*

---

### [5:00 – 5:35] SLIDE 9: BẢO MẬT ZERO TRUST VỚI TRANSPARENT mTLS
> *"Với triết lý **Zero Trust**, mọi giao tiếp mạng nội bộ giữa các Pod đều bị coi là không an toàn.  
> Istio tự động gán cho mỗi service một danh tính bất biến dạng **SPIFFE ID** và cấp phát chứng chỉ số X.509 ngắn hạn qua cơ chế SDS của `istiod`.  
> Hai Envoy sidecar tự động thực hiện bắt tay mã hóa hai chiều (**Transparent mTLS**) mà các lập trình viên Python, Ruby hay Java hoàn toàn truyền plain HTTP nội bộ, không cần cấu hình chứng chỉ. Chế độ `PeerAuthentication` STRICT đảm bảo ngăn chặn 100% kết nối plaintext không có sidecar."*

---

### [5:35 – 6:00] SLIDE 10: OBSERVABILITY (PROMETHEUS/GRAFANA) & TRADE-OFFS
> *"Về giám sát, hệ thống áp dụng mô hình Pull-based của **Prometheus**: định kỳ 15 giây cào metrics từ cổng `:15090/stats/prometheus` của từng Envoy sidecar để đo 4 Golden Signals (Latency, Traffic, Errors, Saturation). Bằng ngôn ngữ PromQL, **Grafana** trực quan hóa chi tiết lưu lượng RPS và độ trễ P95/P99 theo thời gian thực.  
> Cuối cùng là bảng đánh đổi kiến trúc: Để đổi lấy tính độc lập công nghệ và quản trị luồng tinh tế, cái giá phải trả là: Mỗi chặng mạng tốn thêm **1.5 đến 3ms độ trễ (Hop Latency)** do đi qua 2 proxy Envoy, và mỗi Pod tốn thêm **30 đến 50MB RAM**. Đây là sự đánh đổi có chủ đích và hoàn toàn xứng đáng cho các hệ thống Cloud-Native lớn."*

---

### [6:00 – 9:30] PHẦN 2: LIVE DEMO TRỰC TIẾP TRÊN MÁY TÍNH (3.5 PHÚT)

*(Tường chuyển màn hình sang Trình duyệt web và 2 cửa sổ PowerShell)*

#### Thao tác 1 (0.5p) — Web Bookinfo & K8s L4 Round-Robin:
- Mở `http://localhost:9080/productpage`, nhấn `F5` 3 lần:
- *Nói*: *"Khi chưa áp dụng luật Istio, F5 trang web lúc thì không sao (v1), lúc sao đen (v2), lúc sao đỏ (v3). Đây là cơ chế cân bằng tải Round-Robin L4 mặc định của Kubernetes Service giữa 4 microservices đa ngôn ngữ."*

#### Thao tác 2 (1.5p) — Canary Routing theo User Header `jason`:
- Chạy lệnh: `kubectl apply -f projects/bookinfo/source/networking/virtual-service-reviews-test-v2.yaml`.
- Trên trình duyệt (chưa đăng nhập): F5 ➔ Luôn ra **v1 (không sao)**.
- Bấm **Sign in**, gõ `jason` ➔ F5: Xuất hiện ngay lập tức **sao đen của v2**!
- Bấm **Sign out** ➔ F5: Quay trở lại **v1 (không sao)**.
- *Nói*: *"Envoy proxy đã chặn request ở tầng L7, bắt header `end-user: jason` và định tuyến chính xác sang Pod subset v2 mà không cần sửa 1 dòng code Java nào."*

#### Thao tác 3 (1.0p) — Kubernetes Pod Self-Healing:
- Chạy lệnh kill Pod: `kubectl delete pod -l app=details`.
- Quan sát lệnh `kubectl get pods -w`: Pod cũ Terminating và Pod mới lập tức đạt `2/2 Running` trong 2 giây. F5 web vẫn chạy bình thường.
- *Nói*: *"Reconciliation loop đã tự động bù đắp Pod chết, chứng minh khả năng tự phục hồi Zero Downtime của Kubernetes."*

#### Thao tác 4 (0.5p) — Giám sát Telemetry trên Grafana:
- Mở tab Grafana tại `http://localhost:3000` (Istio Service Dashboard).
- Chạy lệnh bơm tải: `1..50 | % { curl.exe -s http://localhost:9080/productpage > $null }`.
- Chỉ vào đồ thị: *"Panel Request Volume (RPS) dựng đứng và Panel P95 Latency phản ánh chính xác độ trễ qua Envoy proxy."*

---

### [9:30 – 10:00] PHẦN 3: KẾT BÀI & MỜI VẤN ĐÁP
> *"Kính thưa Thầy/Cô, qua bài báo cáo 10 slide và phần demo thực tế trên Bookinfo, em đã chứng minh đầy đủ 4 năng lực cốt lõi: Phân rã Polyglot Microservices, đóng gói Multi-stage Docker, điều phối Kubernetes tự phục hồi, quản trị luồng và bảo mật Zero Trust với Istio, cùng giám sát thời gian thực với Prometheus/Grafana.  
> Em xin chân thành cảm ơn Thầy/Cô đã lắng nghe và em sẵn sàng trả lời các câu hỏi vấn đáp!"*
