# Bộ Slide Thuyết Trình Chuẩn: 10 Slide Trong 10 Phút

> **Chủ đề 3**: Kiến trúc Microservices & Hạ tầng Cloud-Native (Bộ Chuẩn 10 Slides)  
> **Các công nghệ cốt lõi**: Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana, Bookinfo  
> **Người báo cáo**: Tường — Báo cáo Giữa kỳ Kiến trúc Phần mềm  
> **Tài liệu kèm theo**: [Slide tiếng Anh (slides-en.md)](slides-en.md) · [Lời thoại 10 phút (speaker-notes.md)](speaker-notes.md)

---

## Slide 1: Đặt Vấn Đề & Chuyển Dịch Sang Cloud-Native

### Tiêu đề:
**MICROSERVICES & CLOUD-NATIVE INFRASTRUCTURE**  
*Thiết kế, Triển khai, Điều phối & Giám sát với Docker, Kubernetes, Istio, Prometheus & Grafana*

- **Sinh viên thực hiện**: Tường
- **Hệ thống thực nghiệm**: Bookinfo (Canonical Istio Polyglot Microservices Sample)

### 4 Thách thức Hạ tầng Sống còn:
1. **Giao tiếp Mạng & Định tuyến Phiên bản**: Điều phối lưu lượng L7 và phát hành Canary thế nào?
2. **Điều phối & Tự phục hồi (Kubernetes)**: Đảm bảo zero-downtime và tự động bù đắp lỗi ra sao?
3. **Bảo mật Mạng Nội bộ (Zero Trust)**: Mã hóa liên Pod bằng mTLS mà không sửa code ứng dụng bằng cách nào?
4. **Khả năng Quan sát (Prometheus & Grafana)**: Thu thập Golden Signals (RPS, Latency P95, Errors) tập trung như thế nào?

---

## Slide 2: Kiến Trúc Microservices & Tính Chất Polyglot

### 1. Bảng Đối Chiếu: Monolith vs Modular Monolith vs Microservices

| Tiêu chí | Monolith | Modular Monolith | Microservices (Bookinfo) |
|---|---|---|---|
| **Cấu trúc Runtime** | 1 process duy nhất chạy toàn bộ | 1 process duy nhất, phân chia module | Mỗi service là 1 container/process độc lập |
| **Cơ sở Dữ liệu** | 1 Shared Database tập trung | 1 Shared DB, phân schema | **Database-per-service** độc lập |
| **Công nghệ** | Đồng nhất 1 ngôn ngữ/framework | Đồng nhất 1 ngôn ngữ | **Polyglot**: Tối ưu tech stack theo domain |
| **Blast Radius** | Rất lớn: Lỗi 1 module sập cả app | Lớn: Lỗi runtime dừng cả process | **Nhỏ**: Lỗi được cô lập trong từng service |
| **Khả năng Scale** | Scale toàn bộ ứng dụng cồng kềnh | Scale toàn bộ binary | **Linh hoạt**: Scale riêng lẻ từng service nghẽn |
| **Độ phức tạp** | Thấp (Deploy đơn giản) | Trung bình | **Cao** (Đòi hỏi K8s, Mesh, Observability) |

### 2. Minh Chứng Polyglot trong Bookinfo:
- **Python (Flask)**: `productpage` — Xử lý giao diện web Jinja2 và tổng hợp API.
- **Ruby (WEBrick/Sinatra)**: `details` — Xử lý metadata xuất bản sách linh hoạt.
- **Java (Open Liberty)**: `reviews` — Xử lý nghiệp vụ bình luận đa phiên bản (v1, v2, v3).
- **Node.js (Express)**: `ratings` — Non-blocking I/O phục vụ tra cứu điểm số đánh giá.

---

## Slide 3: Phân Rã Domain (DDD) & Code Mapping trong Bookinfo

### 1. Bounded Context & Single Responsibility Principle (DDD):
- **`productpage`**: API Aggregator, điều phối hiển thị trang sách.
- **`details`**: Quản lý thông tin sách (thể loại, số trang, nhà xuất bản, ISBN).
- **`reviews`**: Quản lý bình luận độc giả với 3 phiên bản đồng thời:
  - *v1*: Bình luận thuần text, không có sao.
  - *v2*: Gọi `ratings`, hiển thị 1-5 sao màu đen (`STAR_COLOR=black`).
  - *v3*: Gọi `ratings`, hiển thị 1-5 sao màu đỏ (`STAR_COLOR=red`).
- **`ratings`**: Quản lý điểm số sao, hỗ trợ kết nối DB MySQL/MongoDB.

### 2. Code Mapping Thực Tế:
- `src/productpage/productpage.py`: Flask router, hàm `getProducts()`, `getProductDetails()`, `getProductReviews()`.
- `src/reviews/.../LibertyRestEndpoint.java`:
  ```java
  private final static Boolean ratings_enabled = Boolean.valueOf(System.getenv("ENABLE_RATINGS"));
  private final static String star_color = System.getenv("STAR_COLOR") == null ? "black" : System.getenv("STAR_COLOR");
  ```
  *Triển khai chuẩn 12-Factor App: Chung 1 codebase Java, hành vi v1/v2/v3 cấu hình qua biến môi trường.*

---

## Slide 4: Giao Tiếp Liên Dịch Vụ & Lan Truyền Tracing Headers

### 1. Thách thức Tracing trong Hệ Thống Phân Tán:
- Request đi qua chuỗi: `Browser` ➔ `productpage` ➔ `reviews` ➔ `ratings`.
- Nếu không có cơ chế chuyển tiếp ngữ cảnh (Context Propagation), chuỗi Distributed Trace sẽ đứt gãy và Envoy proxy không thể phân loại người dùng để định tuyến L7.

### 2. Code Deep-Dive: Hàm `getForwardHeaders` trong `productpage.py`:
```python
def getForwardHeaders(request):
    headers = {}
    # 1. Trích xuất & tiêm B3 tracing context (OpenTelemetry)
    ctx = propagator.extract(carrier={k.lower(): v for k, v in request.headers})
    propagator.inject(headers, ctx)

    # 2. Chuyển tiếp danh tính người dùng phục vụ Layer 7 Canary Routing
    if 'user' in session:
        headers['end-user'] = session['user']

    # 3. Chuyển tiếp tracing headers chuẩn của Istio Envoy
    for hdr in ['x-request-id', 'x-b3-traceid', 'x-b3-spanid', 'x-b3-sampled']:
        if hdr in request.headers:
            headers[hdr] = request.headers[hdr]
    return headers
```
- **Ý nghĩa sống còn**: Header `end-user: jason` là chìa khóa để Istio VirtualService định tuyến sang `reviews:v2`.

---

## Slide 5: Containerization & Docker Multi-Stage Build

### 1. Nguyên Lý Container & Linux Kernel Primitives:
- **Namespaces**: Cung cấp môi trường cách ly (PID - tiến trình, NET - card mạng riêng, MNT - hệ thống file).
- **Cgroups**: Áp đặt giới hạn cứng CPU limits và Memory limits, ngăn ngừa hiện tượng "Noisy Neighbor".

### 2. Code Deep-Dive: Multi-Stage Build trong `src/reviews/Dockerfile`:
```dockerfile
# STAGE 1: Môi trường biên dịch (Gradle + OpenJDK 8 Alpine)
FROM gradle:4.8.1-jdk8-alpine as builder
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src/reviews-wlpcfg
RUN gradle build

# STAGE 2: Runtime Image tối giản cho Production
FROM open-liberty:kernel-slim
COPY --chown=1001:0 --from=builder \
     /home/gradle/src/reviews-wlpcfg/build/libs/wlp/usr/servers/defaultServer \
     /opt/ibm/wlp/usr/servers/defaultServer
EXPOSE 9080
```
- **Tối ưu kích thước**: Giảm dung lượng image từ **>800MB** xuống còn **~150MB**.
- **Tối ưu an ninh**: Loại bỏ hoàn toàn compiler, Gradle và mã nguồn gốc khỏi container runtime ➔ **Thu hẹp tối đa bề mặt tấn công (Attack Surface)**.

---

## Slide 6: Kubernetes Workload Modeling & Label Selectors

### 1. Cấu Trúc Pod trong Service Mesh (`2/2 Running`):
- Container 1: **App Container Nghiệp Vụ** (`productpage`, `details`, `reviews`, `ratings`).
- Container 2: **Envoy Proxy Sidecar (`istio-proxy`)** được tự động tiêm qua Mutating Webhook.

### 2. Ánh Xạ Tài Nguyên trong `platform/kube/bookinfo.yaml`:
- **ClusterIP Service**: Cung cấp Virtual IP và DNS nội bộ ổn định (`http://reviews:9080`).
- **Label Selectors & Subsets**:
  ```text
  ClusterIP Service: reviews (Port 9080, Selector: app=reviews)
      ├── Deployment 'reviews-v1' (version=v1) ──▶ Không sao
      ├── Deployment 'reviews-v2' (version=v2) ──▶ Sao đen (gọi ratings)
      └── Deployment 'reviews-v3' (version=v3) ──▶ Sao đỏ (gọi ratings)
  ```
- **Cân bằng tải L4 mặc định**: Khi chưa có Istio, Kubernetes Service tự động chia đều tải Round-Robin 33% cho mỗi version.

---

## Slide 7: Kubernetes Self-Healing & Zero-Downtime Deployment

### 1. Cơ Chế Tự Phục Hồi (Self-Healing):
- Kubernetes vận hành theo vòng lặp đối soát (**Reconciliation Loop**):
  $$\text{Current State} \xrightarrow{\quad\text{Reconciliation Loop}\quad} \text{Desired State}$$
- **Minh chứng thực nghiệm**: Khi xóa cưỡng bức Pod `details` (`kubectl delete pod -l app=details`), ReplicaSet Controller phát hiện sai lệch và tái sinh Pod mới đạt `Running (2/2)` chỉ trong **1.8 giây**.
- Khách truy cập web không hề gặp lỗi kết nối (Zero Downtime).

### 2. Quy Trình Rolling Update Không Gián Đoạn:
1. Khởi tạo Pod phiên bản mới song song với Pod cũ.
2. Kiểm tra `readinessProbe` pass 100% mới cho phép gia nhập danh sách Service Endpoints.
3. Gửi tín hiệu `SIGTERM` dừng Pod cũ an toàn sau khi hoàn tất các request dở dang.

---

## Slide 8: Istio Service Mesh & Quản Trị Luồng (Canary Routing)

### 1. Kiến Trúc 2 Tầng của Istio:
- **Control Plane (`istiod`)**: Quản lý cấu hình xDS, cấp phát chứng chỉ số mTLS.
- **Data Plane (Envoy Sidecars)**: Chặn bắt toàn bộ traffic Inbound (:15006) và Outbound (:15001) qua `iptables`.

### 2. Bộ Ba Custom Resource Definitions (CRDs) Cốt Lõi:
- **`Gateway`**: Cấu hình mở cổng biên Ingress tiếp nhận traffic HTTP (Port 80) vào cluster.
- **`VirtualService`**: Định nghĩa quy tắc định tuyến L7:
  ```yaml
  match:
  - headers:
      end-user:
        exact: jason
    route:
    - destination: { host: reviews, subset: v2 } # User jason thấy sao đen
  - route:
    - destination: { host: reviews, subset: v1 } # Khách thường thấy không sao
  ```
- **`DestinationRule`**: Khai báo danh sách Subsets (`v1`, `v2`, `v3`) ánh xạ theo label Kubernetes.

---

## Slide 9: Bảo Mật Zero Trust Với Transparent mTLS

### 1. Triết Lý Zero Trust trong Kubernetes:
- Mạng nội bộ cluster không an toàn; bất kỳ Pod nào cũng có thể bị thỏa hiệp.
- Mọi kết nối liên Pod bắt buộc phải được: **Xác thực**, **Ủy quyền** và **Mã hóa**.

### 2. Cơ Chế Transparent mTLS của Istio:
1. **SPIFFE ID**: Mỗi workload được cấp định danh mật mã bất biến:  
   `spiffe://cluster.local/ns/default/sa/bookinfo-productpage`
2. **Xoay vòng Chứng chỉ Tự động**: `istiod` (Citadel) cấp chứng chỉ X.509 ngắn hạn qua cơ chế SDS (Secret Discovery Service).
3. **Mã hóa Trong Suốt**: Hai Envoy sidecar tự động thực hiện bắt tay mã hóa TLS hai chiều. Code Python, Ruby hay Java hoàn toàn truyền plain HTTP nội bộ mà không cần cấu hình chứng chỉ.
4. **Chế độ `PeerAuthentication` STRICT**: Bắt buộc 100% traffic nội bộ phải có mTLS, từ chối mọi kết nối plaintext.

---

## Slide 10: Giám Sát Prometheus & Grafana + Đánh Đổi Kiến Trúc

### 1. Khả Năng Quan Sát (4 Golden Signals) với Prometheus & Grafana:
- **Pull-based Scraping**: Prometheus định kỳ 15 giây cào số liệu từ cổng `:15090/stats/prometheus` của từng Envoy sidecar.
- **PromQL Cốt lõi**:
  - *RPS theo Workload*: `sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)`
  - *Độ trễ P95*: `histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le))`
- **Grafana**: Trực quan hóa bảng điều khiển Istio Mesh Dashboard và Istio Service Dashboard.

### 2. Bảng Đánh Đổi Kiến Trúc (Architectural Trade-offs):

| Khía cạnh | Lợi thế Vượt trội | Chi phí & Đánh đổi Thực tế |
|---|---|---|
| **Polyglot Microservices** | Tối ưu tech stack từng domain, deploy độc lập, blast radius nhỏ. | Quản lý phức tạp nhiều runtime, build tool và distributed debug. |
| **Envoy Sidecar Mesh** | Tách 100% logic mạng, mTLS, telemetry ra khỏi code app. | **Hop Latency**: Tăng thêm +1.5–3ms/chặng; **RAM**: Tốn 30–50MB/Pod. |
| **Zero Trust mTLS** | Tự động mã hóa 100% lưu lượng mạng nội bộ với SPIFFE ID. | CPU overhead cho việc bắt tay mã hóa TLS liên tục giữa các proxy. |
| **Prometheus Telemetry** | Chuẩn hóa giám sát Golden Signals tập trung, phát hiện lỗi nhanh. | Tần suất cào metrics (scrape interval) tạo thêm lưu lượng mạng nền. |
