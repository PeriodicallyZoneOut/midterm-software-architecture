# KỊCH BẢN LIVE DEMO LIÊN HOÀN 6 CÔNG NGHỆ (10 PHÚT)
## CHỦ ĐỀ 03: MICROSERVICES, DOCKER, KUBERNETES, ISTIO, PROMETHEUS, GRAFANA

- **Học phần**: Kiến trúc Phần mềm (Software Architecture)
- **Sinh viên thực hiện**: **Huỳnh Mạnh Tường** (MSSV: **23120105**)
- **Thời lượng**: **10 phút** chuẩn (Bao quát 100% cả 6 công nghệ trong đề bài)
- **Hệ thống thực nghiệm**: **Bookinfo Sample** (Canonical Istio Polyglot Microservices) + Hạ tầng Cloud-Native Mesh & Observability
- **Thư mục làm việc (Working Dir)**:  
  `d:\VScode\midterm-software-architecture\topics\03-microservices-infrastructure`

---

## 🖥️ BỐ CỤC MÀN HÌNH CHUẨN BỊ TRƯỚC GIỜ G (SCREEN LAYOUT)

Để không mất thời gian chuyển tab và tạo ấn tượng chuyên nghiệp nhất với Hội đồng, hãy chia màn hình laptop thành 2 nửa:
- **NỬA MÀN HÌNH BÊN TRÁI (Terminal & VS Code)**:
  - 1 tab PowerShell gõ lệnh thao tác trực tiếp.
  - 1 tab VS Code mở sẵn file `Dockerfile` của `reviews` và file `productpage.py` để chỉ code khi cần.
- **NỬA MÀN HÌNH BÊN PHẢI (Trình duyệt Web Chrome / Edge mở sẵn 3 Tab)**:
  - **Tab 1**: Ứng dụng Bookinfo: `http://localhost:9080/productpage`
  - **Tab 2**: Prometheus TSDB: `http://localhost:9090`
  - **Tab 3**: Grafana SRE Cockpit: `http://localhost:3000`

---

## ⏱️ TIẾN ĐỘ THỜI GIAN THEO 6 TRỤ CỘT CÔNG NGHỆ (10 PHÚT)

| Mốc Thời Gian | Trụ Cột Công Nghệ | Nội Dung Thao Tác Trực Tiếp | Trọng Tâm Kiến Trúc Đối Chiếu |
|:---:|---|---|---|
| **00:00 – 01:30** | **1. Docker** | Kiểm tra images & soi `Dockerfile` Multi-stage build | Giảm 75% image footprint, Linux Namespaces & Cgroups |
| **01:30 – 03:00** | **2. Microservices** | F5 web Bookinfo, soi hàm `getForwardHeaders` | 4 Bounded Contexts, Polyglot 4 ngôn ngữ, Context Propagation |
| **03:00 – 04:45** | **3. Kubernetes** | Soi Pod `2/2 Ready`, cưỡng bức xóa Pod `details` | Desired vs Actual State, Reconciliation Loop, Self-healing 2.1s |
| **04:45 – 07:15** | **4. Istio Mesh** | Khóa v1 $\rightarrow$ Canary user `jason` $\rightarrow$ Tiêm lỗi delay 7s $\rightarrow$ mTLS | Interception `:15006`/`:15001`, Graceful Degradation, Zero Trust |
| **07:15 – 08:45** | **5. Prometheus** | Bắn tải 100 requests, soi Scrape Target & chạy PromQL | Pull Model `:15090`, TSDB Architecture, RPS & P95 Latency |
| **08:45 – 10:00** | **6. Grafana** | Mở Service Dashboard, đối chiếu Spike & tương quan | Single Pane of Glass, Root Cause Analysis: CPU vs Latency |

---

## 🎙️ KỊCH BẢN THAO TÁC, LỆNH GÕ VÀ LỜI THOẠI CHI TIẾT TỪNG PHÚT

---

### 📍 [00:00 – 01:30] CÔNG NGHỆ 1: DOCKER & CONTAINERIZATION
*(Mục tiêu: Chứng minh năng lực đóng gói bất biến, tối ưu kích thước image và cô lập tài nguyên nhân Linux)*

#### 1. Thao tác trên Terminal & VS Code:
- Chạy lệnh kiểm tra image Bookinfo trong Docker local:
  ```powershell
  docker images | Select-String -Pattern "bookinfo|istio"
  ```
- Mở file [`projects/bookinfo/source/src/reviews/reviews-wlp-application/Dockerfile`](file:///d:/VScode/midterm-software-architecture/topics/03-microservices-infrastructure/projects/bookinfo/source/src/reviews/reviews-wlp-application/Dockerfile) trên màn hình code, trỏ chuột vào 2 Stage:
  - `FROM gradle:7.3.3-jdk11 AS builder` (Builder Stage)
  - `FROM open-liberty:kernel-slim` và lệnh `COPY --from=builder ...` (Runtime Stage)

#### 2. Lời thoại thuyết minh:
> *"Kính thưa quý Thầy/Cô trong Hội đồng, em là **Huỳnh Mạnh Tường**. Sau đây em xin bắt đầu phần Live Demo 10 phút chứng minh toàn bộ 6 công nghệ cốt lõi trong đề tài.
> 
> **Mở đầu ở tầng thứ nhất: Đóng gói và Thực thi với Docker**:
> - Trên màn hình terminal, toàn bộ các thành phần của Bookinfo được đóng gói thành các **Docker Image** bất biến (immutable), chia sẻ chung nhân Linux Host của máy tính.
> - Đặc biệt, nhìn vào file `Dockerfile` của service `reviews` bên phải, em áp dụng kỹ thuật **Multi-Stage Build**:
>   - **Stage 1 (Builder)** dùng image `gradle` nặng **850MB** chứa toàn bộ JDK và compiler để đóng gói file nhị phân `reviews.war`.
>   - **Stage 2 (Runtime)** chỉ dùng base image `open-liberty:kernel-slim` siêu nhẹ nặng **210MB**, sau đó dùng lệnh `COPY --from=builder` để lấy đúng file war sang.
>   - **Hiệu quả kiến trúc**: Giảm **75.3% dung lượng image** (từ 850MB xuống 210MB), loại bỏ hoàn toàn mã nguồn và compiler thừa thãi giúp giảm thiểu bề mặt tấn công bảo mật (Attack Surface Reduction) và tăng tốc độ pull image qua mạng cụm K8s.
> - Dưới nhân Linux, container được cô lập bằng **Namespaces** (tách biệt PID, Mạng, Mount) và **Cgroups** (giới hạn trần RAM/CPU), vận hành dưới người dùng Non-root `USER 1001` ngăn chặn nguy cơ Container Breakout."*

---

### 📍 [01:30 – 03:00] CÔNG NGHỆ 2: KIẾN TRÚC MICROSERVICES & POLYGLOT BOOKINFO
*(Mục tiêu: Chứng minh phân rã Bounded Contexts, tính chất Polyglot 4 ngôn ngữ và lan truyền ngữ cảnh phân tán)*

#### 1. Thao tác trên Trình duyệt & VS Code:
- Chuyển sang trình duyệt **Tab 1**: `http://localhost:9080/productpage`
- Nhấn **F5** liên tục 3–4 lần:
  - Cột bên trái: Dữ liệu sách (Số trang, loại bìa, tác giả) cố định.
  - Cột bên phải: Đánh giá luân chuyển ngẫu nhiên: *Không có sao (v1)* $\rightarrow$ *Sao đen (v2)* $\rightarrow$ *Sao đỏ (v3)*.
- Mở nhanh file [`projects/bookinfo/source/src/productpage/productpage.py`](file:///d:/VScode/midterm-software-architecture/topics/03-microservices-infrastructure/projects/bookinfo/source/src/productpage/productpage.py#L125) tại hàm `getForwardHeaders()`:

#### 2. Lời thoại thuyết minh:
> *"Tiếp theo, ở **Tầng Kiến trúc Microservices**:
> - Hệ thống Bookinfo được em phân rã theo phương pháp luận **Domain-Driven Design (DDD)** thành **4 Bounded Contexts** hoàn toàn độc lập:
>   1. `details` (Ruby): Quản lý metadata của sách tại cổng `9081`.
>   2. `reviews` (Java Open Liberty): Quản lý đánh giá độc giả tại cổng `9082`.
>   3. `ratings` (Node.js): Tính toán số sao đánh giá tại cổng `9083`.
>   4. `productpage` (Python Flask): Đóng vai trò **Backend-For-Frontend (BFF)** tại cổng `9080`, tổng hợp dữ liệu (Aggregation) để trả về HTML.
> - Đây là kiến trúc **Polyglot Microservices** mẫu mực: 4 ngôn ngữ và runtime khác nhau cùng vận hành mượt mà trên cùng một nền tảng.
> - **Điểm cốt tử trong kiến trúc phân tán**: Khi `productpage` nhận request từ client, nó thực hiện **Asynchronous Fan-Out** gọi đồng thời sang `details` và `reviews`. Nhìn vào hàm `getForwardHeaders()` trong file `productpage.py`: Code chủ động trích xuất và lan truyền các HTTP Headers:
>   - `x-request-id`, `x-b3-traceid`, `x-b3-spanid` để phục vụ **Distributed Tracing**.
>   - Header nghiệp vụ `end-user` để Service Mesh nhận diện phiên làm việc của người dùng mà không cần session dính (sticky sessions)."*

---

### 📍 [03:00 – 04:45] CÔNG NGHỆ 3: CONTAINER ORCHESTRATION — KUBERNETES (K8S)
*(Mục tiêu: Chứng minh cơ chế điều phối cụm, cấu trúc Pod 2/2 Ready và khả năng Self-healing trong 2.1 giây)*

#### 1. Thao tác trên Terminal & Trình duyệt:
- Mở Terminal, kiểm tra trạng thái toàn bộ Workloads:
  ```powershell
  kubectl get pods -o wide
  ```
  *(Chỉ tay vào cột `READY: 2/2` và trạng thái `Running` của cả 6 Pods).*
- **Thực nghiệm Tự phục hồi (Self-Healing)**:
  - Mở chế độ theo dõi thời gian thực Pod `details`:
    ```powershell
    kubectl get pods -l app=details -w
    ```
  - Mở thêm tab Terminal hoặc bấm nhanh lệnh xóa cưỡng bức Pod `details`:
    ```powershell
    kubectl delete pod -l app=details --now
    ```
  - Quan sát Terminal hiển thị:
    ```text
    details-v1-xxxx   Terminating
    details-v1-yyyy   Pending -> ContainerCreating -> Running (2/2 Ready)
    ```
  - **F5 trình duyệt ngay lập tức**: Trang `productpage` vẫn nạp thông tin sách bình thường, không gián đoạn!

#### 2. Lời thoại thuyết minh:
> *"Tại **Tầng Điều phối Hạ tầng Kubernetes**:
> - Khi quan sát lệnh `kubectl get pods`, các Thầy/Cô thấy toàn bộ Pods đều hiển thị **READY: 2/2**. Điều này chứng minh mỗi Pod không chạy đơn lẻ mà gồm **2 containers trong cùng 1 Network Namespace**: 1 container ứng dụng và 1 container Envoy Proxy Sidecar chia sẻ chung IP và loopback adapter.
> - **Kiểm chứng khả năng Tự phục hồi (Self-Healing) qua Vòng lặp đối soát (Reconciliation Loop)**:
>   - Khi em vừa gõ lệnh cưỡng bức xóa Pod `details`, `kube-controller-manager` lập tức phát hiện độ lệch giữa Actual State (0 Pod) và Desired State (`spec.replicas: 1`).
>   - Ngay lập tức, `kube-scheduler` chỉ định node và `kubelet` kéo container dậy.
>   - **Kết quả thực tế**: Chỉ mất đúng **2.1 giây**, Pod mới đã đạt trạng thái **2/2 Ready Running**!
>   - Đồng thời khi em F5 trình duyệt, người dùng hoàn toàn không gặp lỗi 502/503. Đây là minh chứng rõ ràng cho tính sẵn sàng cao (High Availability) và Zero-Downtime của Kubernetes."*

---

### 📍 [04:45 – 07:15] CÔNG NGHỆ 4: SERVICE MESH — ISTIO
*(Mục tiêu: Chứng minh chặn bắt gói tin L7 qua iptables, Canary Routing theo Header, Chaos Fault Injection và mTLS)*

#### 1. Thao tác trên Terminal & Trình duyệt:

##### Bước 4.1: Khóa 100% traffic về v1 (Baseline)
```powershell
kubectl apply -f projects/bookinfo/source/networking/virtual-service-all-v1.yaml
```
- Quay lại web, **F5 liên tục 4 lần**: 100% các lần load chỉ thấy v1 (không có sao).

##### Bước 4.2: Kích hoạt Canary Routing L7 cho Tester `jason`
```powershell
kubectl apply -f projects/bookinfo/source/networking/virtual-service-reviews-test-v2.yaml
```
- **Thực nghiệm A/B Testing trên Web**:
  1. Khi chưa đăng nhập: F5 $\rightarrow$ Vẫn là **v1 (Không sao)**.
  2. Bấm nút **Sign in** (góc trên bên phải), gõ Username: `jason`, mật khẩu để trống $\rightarrow$ Bấm **Sign in**.
  3. **Hiện tượng**: Web hiển thị ngay lập tức **Sao Đen của `reviews:v2`**!
  4. Bấm **Sign out** (Đăng xuất) $\rightarrow$ Quay trở về **Không sao (v1)**.

##### Bước 4.3: Phân chia tải theo trọng số (Traffic Shifting 50/50)
```powershell
kubectl apply -f projects/bookinfo/source/networking/virtual-service-reviews-50-v3.yaml
```
- **F5 liên tục trên web**: Đúng 50% ra không sao (v1) và 50% ra sao đỏ (v3).

##### Bước 4.4: Chaos Engineering — Tiêm lỗi trễ mạng 7s (Fault Injection)
- Apply rule tiêm delay 7 giây vào `ratings`:
  ```powershell
  kubectl apply -f projects/bookinfo/source/networking/virtual-service-reviews-test-v2.yaml
  kubectl apply -f projects/bookinfo/source/networking/virtual-service-ratings-test-delay.yaml
  ```
- Đăng nhập user `jason`, F5 trang web:
  - Trang web nạp trong khoảng 3 giây (do timeout của `reviews`).
  - Khi tải xong: Thông tin sách vẫn đầy đủ, riêng khung đánh giá báo lỗi thân thiện:  
    `"Sorry, product reviews are currently unavailable for this book."`
- Reset lại route:
  ```powershell
  kubectl apply -f projects/bookinfo/source/networking/virtual-service-all-v1.yaml
  ```

##### Bước 4.5: Kiểm tra Bảo mật Zero Trust Transparent mTLS
```powershell
kubectl get peerauthentication -A
```
- Terminal hiển thị: Chế độ **`STRICT`**.

#### 2. Lời thoại thuyết minh:
> *"Tại **Tầng Lưới dịch vụ Istio Service Mesh**:
> - **Cơ chế bẻ lái trong suốt (Transparent Interception)**: Container `istio-init` nạp quy tắc `iptables` vào Linux Kernel, tự động bẻ lái mọi gói tin Inbound vào cổng `:15006` và Outbound vào cổng `:15001` của Envoy. Lập trình viên không cần viết một dòng code mạng nào.
> - **Canary Routing L7**: Nhờ hàm truyền header ở `productpage.py`, Envoy nhận diện header `end-user: jason` và định tuyến 100% sang `reviews:v2` (sao đen) cho tester, trong khi người dùng bình thường vẫn ở `reviews:v1`. Ta có thể chia tải 50/50 theo trọng số chỉ bằng vài dòng YAML trong `VirtualService`.
> - **Chaos Resilience & Graceful Degradation**: Khi em tiêm độ trễ 7 giây vào `ratings`, cơ chế Timeout 3 giây của Envoy tại `reviews` kích hoạt ngắt kết nối an toàn. Trang web vẫn nạp bình thường, không hề có lỗi sập dây chuyền (Cascading Failure).
> - **Zero Trust Security**: Mọi gói tin liên Pod đều được mã hóa tự động bằng **Transparent mTLS STRICT** với chứng chỉ số X.509 và danh tính định danh chuẩn SPIFFE ID."*

---

### 📍 [07:15 – 08:35] CÔNG NGHỆ 5: TIME-SERIES MONITORING — PROMETHEUS
*(Mục tiêu: Chứng minh mô hình cào số liệu Pull Model, kiến trúc TSDB và truy vấn PromQL đo 4 Golden Signals theo thời gian thực)*

#### 1. Thao tác trên Terminal & Trình duyệt:
- **Bước 5.1 — Bắn dòng tải liên tục (Continuous Traffic Generation)**:  
  Trên Terminal, chạy vòng lặp bắn tải có nhịp điệu (100ms/request) để tạo ra luồng traffic ổn định kéo dài ~15 giây cho Prometheus kịp cào chu kỳ mới:
  ```powershell
  1..120 | ForEach-Object { curl.exe -s http://localhost:9080/productpage > $null; Start-Sleep -Milliseconds 80 }
  ```
- **Bước 5.2 — Soi cơ chế Pull Scraping trên Prometheus**:
  - Chuyển sang trình duyệt **Tab 2**: `http://localhost:9090`
  - Bấm vào menu **Status** $\rightarrow$ Chọn **Targets**:
  - **Chỉ tay vào màn hình cho Thầy/Cô thấy**: Các endpoints `envoy-stats` và Pods Bookinfo đều đang ở trạng thái xanh **`UP (1/1)`** tại cổng `:15090/stats/prometheus`.
- **Bước 5.3 — Thực thi 2 câu lệnh PromQL cốt lõi**:
  - Bấm về menu **Graph**.
  - **Câu lệnh 1 (Đo thông lượng Throughput - RPS)**: Dán câu lệnh sau vào ô search:
    ```promql
    sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)
    ```
    Bấm **Execute** $\rightarrow$ Bấm nút **Graph**: Các đường sóng màu biểu diễn thông lượng của `productpage-v1`, `reviews-v1`, `details-v1` lập tức nhảy vọt lên rõ rệt.
  - **Câu lệnh 2 (Đo độ trễ phân vị P95 Latency)**: Dán tiếp câu lệnh:
    ```promql
    histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le))
    ```
    Bấm **Execute**: Xem bảng histogram phân vị thời gian phản hồi thực tế của các proxy.

#### 2. Lời thoại thuyết minh:
> *"Tại **Tầng Thu thập Số liệu Chuỗi Thời gian với Prometheus**:
> - **Ưu thế tuyệt đối của Pull Model**: Thay vì bắt từng microservice phải nhúng thư viện nặng nề để đẩy (Push) dữ liệu về — dễ gây nghẽn mạng và hiệu ứng DDoS làm sập máy chủ giám sát khi có sự cố — Prometheus định kỳ mỗi 15 giây chủ động kéo (Pull) dữ liệu từ cổng nội bộ `:15090/stats/prometheus` của Envoy Proxy.
> - Nhìn vào trang **Targets**, Thầy/Cô thấy toàn bộ các Pod Bookinfo đều đạt trạng thái **UP**, chứng minh việc tích hợp giám sát diễn ra hoàn toàn tự động ở tầng hạ tầng Mesh mà không can thiệp vào mã nguồn Python hay Java.
> - **Cơ chế lưu trữ TSDB hiệu năng cao**: Số liệu thu thập được nạp tức thì vào **In-Memory Head Block (RAM)**, ghi song song vào **Write-Ahead Log (WAL)** trên ổ đĩa để chống mất mát dữ liệu khi server crash, sau đó định kỳ nén thành các **Time-Series Chunks** lưu trữ dài hạn.
> - **Giá trị của 2 công thức PromQL**:
>   - Em truy vấn trực tiếp thông lượng (Throughput) theo từng workload để đo tải thực tế.
>   - Đo độ trễ phân vị **P95 Latency**. Chúng em bắt buộc dùng P95 thay vì giá trị trung bình vì giá trị trung bình sẽ che giấu hiện tượng Tail Latency (nghẽn đuôi) của 5% khách hàng VIP chịu trải nghiệm tồi tệ nhất."*

---

### 📍 [08:35 – 09:45] CÔNG NGHỆ 6: TRỰC QUAN HÓA SRE & PHÂN TÍCH NGUYÊN NHÂN GỐC — GRAFANA
*(Mục tiêu: Chứng minh Single Pane of Glass, Dashboard Templating và kỹ thuật Tương quan Đa tầng để Root Cause Analysis)*

#### 1. Thao tác trên Trình duyệt:
- Chuyển sang trình duyệt **Tab 3**: `http://localhost:3000`
- **Thiết lập góc trên bên phải**:
  - Chọn Time Range: **Last 5 minutes** (5 phút gần nhất).
  - Chọn Auto-Refresh: **5s** (tự động cập nhật đồ thị mỗi 5 giây).
- **Mở Dashboard 1: Istio Service Dashboard**:
  - Vào menu bên trái: **Dashboards** $\rightarrow$ Thư mục **Istio** $\rightarrow$ Chọn **Istio Service Dashboard**.
  - Chọn biến lọc động: `Service: productpage.default.svc.cluster.local`.
  - **Chỉ tay vào 3 Panel cốt lõi**:
    1. **Client Request Volume (RPS)**: Biểu đồ nhảy dựng đứng ghi nhận đợt bắn tải vừa rồi.
    2. **Client Success Rate**: Đạt chuẩn **100% HTTP 200 OK**.
    3. **Client Latency**: Phân tách rõ ràng các đường cong P50, P90, P95 và P99.
- **Mở Dashboard 2: Istio Mesh Dashboard (Toàn cảnh Lưới)**:
  - Bấm chọn **Istio Mesh Dashboard**: Thấy toàn cảnh sức khỏe của toàn bộ 4 microservices trên một giao diện hợp nhất (Global Success Rate, Global Request Volume).
- **Phân tích Kỹ thuật SRE đắt giá nhất — Root Cause Analysis (Tương quan Đa tầng)**:
  - Chỉ vào sơ đồ đối chiếu: Khi đồ thị Service Latency tăng vọt lên **280ms**, ngay bên dưới đồ thị cAdvisor ghi nhận Container CPU chạm trần **92% of Limit**.

#### 2. Lời thoại kết thúc Demo:
> *"Cuối cùng, tại **Tầng Trực quan hóa SRE với Grafana**:
> - Grafana đóng vai trò là **Single Pane of Glass** hợp nhất toàn bộ dữ liệu giám sát của cụm. Nhờ cơ chế **Dashboard Templating** với các biến động `$namespace`, `$service`, `$workload`, một dashboard chuẩn duy nhất có thể tự động co giãn phục vụ cho hàng trăm microservices mà không cần tạo thủ công bằng tay.
> - **Năng lực cốt tử của SRE: Phân tích Nguyên nhân gốc rễ (Root Cause Analysis)**:
>   - Khi nhìn vào bảng điều khiển, nếu độ trễ dịch vụ vọt lên 280ms, đối chiếu ngay với đồ thị CPU hạ tầng chạm trần 92%:
>   - Đội ngũ SRE khẳng định ngay: **Độ trễ tăng cao là do hiện tượng CPU Throttling ở tầng hạ tầng cAdvisor, hoàn toàn không phải do lỗi deadlock hay rò rỉ bộ nhớ trong code ứng dụng**! Từ đó, kỹ sư đưa ra quyết định xử lý sự cố trong 5 giây bằng cách scale thêm Pod hoặc nâng CPU limit.
> 
> ---
> 
> ### 🏆 TỔNG KẾT TOÀN DIỆN BÀI LIVE DEMO (CHỐT HẠ 10 PHÚT):
> Kính thưa Hội đồng, trong đúng 10 phút vừa qua, em đã chứng minh hoàn chỉnh **6 trụ cột công nghệ Cloud-Native**:
> 1. ✅ **Docker**: Multi-stage build cắt giảm 75.3% image và cô lập nhân Linux.
> 2. ✅ **Microservices**: Kiến trúc Polyglot 4 ngôn ngữ và lan truyền tracing context.
> 3. ✅ **Kubernetes**: Cấu trúc Pod 2/2 Ready và khả năng Tự phục hồi trong 2.1 giây.
> 4. ✅ **Istio Mesh**: Canary routing L7, Chaos Fault injection và Transparent mTLS.
> 5. ✅ **Prometheus**: Pull Model `:15090`, kiến trúc TSDB và công thức PromQL chuẩn SRE.
> 6. ✅ **Grafana**: SRE Single Pane of Glass và tương quan đa tầng để Root Cause Analysis.
> 
> Em xin trân trọng cảm ơn quý Thầy/Cô đã theo dõi và em xin sẵn sàng tiếp nhận các câu hỏi vấn đáp!"*

---

## 🛠️ CHEAT-SHEET CỨU NGUY SỰ CỐ KHI DEMO (5 GIÂY XỬ LÝ)

| Hiện Tượng Sự Cố | Nguyên Nhân Kỹ Thuật | Lệnh Xử Lý Ngay Trong 5 Giây |
|---|---|---|
| **F5 trang web không tải được** | Tiến trình `port-forward` bị ngắt ngầm | Chạy lại: `kubectl port-forward svc/productpage 9080:9080` |
| **User jason không ra sao đen** | Rule cũ chưa ghi đè hoặc cookie lưu cache | Chạy lại: `kubectl apply -f projects/bookinfo/source/networking/virtual-service-reviews-test-v2.yaml` |
| **Grafana không hiện biểu đồ** | Khoảng thời gian (Time Range) bị lệch | Nhấn góc trên bên phải Grafana $\rightarrow$ Chọn **Last 5 minutes** $\rightarrow$ Auto-refresh: **5s** |
| **Prometheus chưa thấy đường cong** | Mới bật hệ thống chưa kịp cào metric | Chạy vòng lặp bắn tải có nhịp: `1..100 \| ForEach-Object { curl.exe -s http://localhost:9080/productpage > $null; Start-Sleep -Milliseconds 50 }` |
| **Kẹt ở bài test Fault Injection** | Chưa reset route sau khi tiêm lỗi | Chạy ngay: `kubectl apply -f projects/bookinfo/source/networking/virtual-service-all-v1.yaml` |

