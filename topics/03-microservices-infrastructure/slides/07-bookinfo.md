---
marp: true
theme: default
paginate: true
header: 'Chủ đề 3.7: Ứng dụng Thực nghiệm Bookinfo & Đánh giá Kiến trúc | Tường'
footer: 'Kiến trúc Phần mềm — Báo cáo Giữa kỳ'
style: |
  section { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 35px; }
  h1 { color: #58a6ff; font-size: 26px; }
  h2, h3 { color: #79c0ff; font-size: 20px; }
  table { font-size: 13px; color: #c9d1d9; width: 100%; }
  th { background-color: #161b22; color: #58a6ff; }
  code { background-color: #161b22; color: #ff7b72; font-size: 12px; }
  pre { background-color: #161b22; font-size: 11px; padding: 10px; }
---

# SLIDE 1: ĐẶT VẤN ĐỀ & GIỚI THIỆU HỆ THỐNG THỰC NGHIỆM BOOKINFO
- **Học phần**: Kiến trúc Phần mềm — Báo cáo Chuyên sâu: **Bookinfo Application**
- **Người thực hiện**: Tường (Thời lượng: 10 phút)
- **Mã nguồn dự án**: [Bookinfo Source Code](../../projects/bookinfo/source)

### Tại Sao Chọn Bookinfo Làm Hệ Thống Thực Nghiệm Tiêu Chuẩn?
- Là ứng dụng chuẩn mực (canonical benchmark) được Linux Foundation / CNCF và cộng đồng Istio tin dùng.
- Mô phỏng hoàn chỉnh một trang bán sách trực tuyến với đầy đủ: Thông tin sách, Đánh giá của độc giả, Điểm xếp hạng.
- **Tính chất Đa Ngôn Ngữ (Polyglot)**: Được xây dựng từ 4 ngôn ngữ lập trình khác nhau (Python, Ruby, Java, Node.js).
- Thử thách toàn diện hạ tầng Container (Docker), Điều phối (Kubernetes), Lưới dịch vụ (Istio), và Giám sát (Prometheus/Grafana).

---

# SLIDE 2: TỔNG QUAN KIẾN TRÚC ĐA DỊCH VỤ (POLYGLOT TOPOLOGY)

```text
                                [ Internet / Client ]
                                          │
                        ┌─────────────────▼─────────────────┐
                        │    Istio Ingress Gateway (:80)    │
                        └─────────────────┬─────────────────┘
                                          │
                        ┌─────────────────▼─────────────────┐
                        │   productpage (Python / Flask)    │
                        │   - Aggregator & Web Frontend     │
                        └─────────┬─────────────────┬───────┘
                                  │                 │
                 ┌────────────────┘                 └────────────────┐
                 │                                                   │
  ┌──────────────▼──────────────┐                     ┌──────────────▼──────────────┐
  │   details (Ruby / Sinatra)  │                     │ reviews (Java / OpenLiberty)│
  │   - Book Metadata           │                     │ - v1: No ratings            │
  └─────────────────────────────┘                     │ - v2: Black stars           │
                                                      │ - v3: Red stars             │
                                                      └──────────────┬──────────────┘
                                                                     │ (v2 & v3 only)
                                                      ┌──────────────▼──────────────┐
                                                      │    ratings (Node.js/Express)│
                                                      │    - Numerical ratings (1-5)│
                                                      └─────────────────────────────┘
```

---

# SLIDE 3: MICROSERVICE 1 — `productpage` (PYTHON / FLASK)
*Dịch vụ cửa ngõ tiếp nhận tương tác người dùng và tổng hợp dữ liệu (Aggregator Pattern)*

- **Vị trí mã nguồn**: `src/productpage/productpage.py`
- **Công nghệ**: Python 3.12, Flask Framework, Jinja2 Templates, Bootstrap UI.

### Luồng Nghiệp Vụ Chính:
1. Nhận yêu cầu từ người dùng tại endpoint `/productpage`.
2. Gửi đồng thời 2 HTTP GET request không đồng bộ:
   - Gọi `http://details:9080/details/0` để lấy thông tin xuất bản, số trang, loại bìa.
   - Gọi `http://reviews:9080/reviews/0` để lấy danh sách đánh giá của bạn đọc.
3. Ghép nối kết quả vào JSON context và render ra trang HTML hoàn chỉnh cho trình duyệt.
4. Tích hợp sẵn endpoint nội bộ `/metrics` (Prometheus Python Client) để đo lường.

---

# SLIDE 4: MICROSERVICES 2 & 4 — `details` (RUBY) & `ratings` (NODE.JS)
*Hai dịch vụ nền tảng cung cấp dữ liệu độc lập tuân thủ nguyên tắc Single Responsibility*

### 1. Dịch Vụ `details` (Ruby / Sinatra):
- **Vị trí**: `src/details/details.rb`
- **Nhiệm vụ**: Cung cấp thông tin chi tiết về sách (ISBN, tác giả, nhà xuất bản, số trang).
- **Endpoint**: `/details/:id` trả về JSON thuần túy.
- **Kiến trúc**: Lightweight REST service, hoàn toàn Stateless, phản hồi siêu nhanh (< 5ms).

### 2. Dịch Vụ `ratings` (Node.js / Express):
- **Vị trí**: `src/ratings/ratings.js`
- **Nhiệm vụ**: Trả về số sao đánh giá (1 đến 5 sao) của người đọc cho từng cuốn sách.
- **Endpoint**: `/ratings/:id` trả về JSON `{"id": 0, "ratings": {"Reviewer1": 5, "Reviewer2": 4}}`.
- **Hỗ trợ Backend**: Có khả năng đọc trực tiếp từ in-memory JSON hoặc kết nối Database MySQL bên ngoài.

---

# SLIDE 5: MICROSERVICE 3 — `reviews` (JAVA) VỚI 3 BIẾN THỂ PHIÊN BẢN
*Minh chứng sống động nhất cho quá trình tiến hóa phần mềm (Evolutionary Architecture)*

- **Vị trí**: `src/reviews/reviews-application/.../LibertyRestEndpoint.java`
- **Công nghệ**: Java 17, IBM Open Liberty, JAX-RS RESTful Web Services.

### 3 Phiên Bản Khác Biệt Triển Khai Đồng Thời:

| Phiên Bản | Giao Tiếp Mạng Outbound | Giao Diện Hiển Thị Người Dùng | Mục Đích Kiến Trúc |
|---|---|---|---|
| **`reviews:v1`** | **Không** gọi sang service `ratings` | Hiển thị nhận xét dạng text thuần, **không có ngôi sao** nào | Phiên bản gốc ổn định, tiêu thụ ít tài nguyên nhất |
| **`reviews:v2`** | Gọi sang `http://ratings:9080/ratings/0` | Hiển thị nhận xét kèm **Ngôi Sao Đen (Black Stars)** | Phiên bản thử nghiệm tính năng đánh giá mới |
| **`reviews:v3`** | Gọi sang `http://ratings:9080/ratings/0` | Hiển thị nhận xét kèm **Ngôi Sao Đỏ (Red Stars)** | Phiên bản hoàn thiện giao diện thương mại |

---

# SLIDE 6: CƠ CHẾ LAN TRUYỀN NGỮ CẢNH (HEADER PROPAGATION)
*Làm sao Istio và Tracing có thể nhận diện danh tính người dùng xuyên suốt chuỗi gọi phân tán?*

### Vấn Đề Lớn Trong Microservices:
- Khi request đi qua: `Client ──> productpage ──> reviews ──> ratings`.
- Envoy sidecar có thể tự sinh trace ID, nhưng ứng dụng phải **chủ động forward header** sang request tiếp theo, nếu không chuỗi trace sẽ bị đứt gãy.

### Phân Tích Hàm `getForwardHeaders()` trong `productpage.py`:
```python
def getForwardHeaders(request):
    headers = {}
    # 1. Trích xuất Trace Context (B3 Zipkin / OpenTelemetry)
    ctx = propagator.extract(carrier={k.lower(): v for k, v in request.headers})
    propagator.inject(headers, ctx)

    # 2. Lan truyền danh tính người dùng đăng nhập cho Istio Canary
    if 'user' in session:
        headers['end-user'] = session['user']

    # 3. Lan truyền x-request-id để bám vết log đồng nhất giữa các Pod
    if 'x-request-id' in request.headers:
        headers['x-request-id'] = request.headers['x-request-id']
    return headers
```

---

# SLIDE 7: TRIỂN KHAI HẠ TẦNG KUBERNETES (`bookinfo.yaml`)
*Đóng gói toàn bộ kiến trúc thành các tài nguyên khai báo (Declarative Manifests)*

### Phân Tích File `platform/kube/bookinfo.yaml`:
- **4 Kubernetes Services**: `productpage`, `details`, `reviews`, `ratings` (cùng expose cổng 9080).
- **6 Kubernetes Deployments**:
  - `details-v1` (1 replica)
  - `ratings-v1` (1 replica)
  - `productpage-v1` (1 replica)
  - `reviews-v1`, `reviews-v2`, `reviews-v3` (mỗi bản 1 replica chạy song song).

### Mô Hình Pod "2/2 Containers Ready":
```text
$ kubectl get pods
NAME                              READY   STATUS    RESTARTS   AGE
details-v1-65cfcf56f9-m7pzw       2/2     Running   0          5h
productpage-v1-d5789fdfb-k8x5n    2/2     Running   0          5h
ratings-v1-7c9948f57b-9wpl4       2/2     Running   0          5h
reviews-v1-7598cc9867-q2j5d       2/2     Running   0          5h
reviews-v2-5b667bcbf8-6dptx       2/2     Running   0          5h
reviews-v3-84779c7bbc-xghzt       2/2     Running   0          5h
```
*Mỗi Pod gồm 1 container ứng dụng và 1 container `istio-proxy` (Envoy) được inject tự động.*

---

# SLIDE 8: ĐỊNH TUYẾN LƯỚI ISTIO — KIỂM SOÁT LUỒNG NGHIỆP VỤ
*Kết hợp các Custom Resource Definitions để điều khiển luồng Bookinfo linh hoạt*

```text
[ Client Request ]
       │
       ▼
1. bookinfo-gateway.yaml       ── Mở Ingress Gateway đón traffic đường dẫn /productpage
       │
       ▼
2. destination-rule-all.yaml   ── Định nghĩa rõ ràng 3 Subsets (v1, v2, v3) của reviews
       │
       ▼
3. virtual-service-reviews-test-v2.yaml ── LUẬT ĐỊNH TUYẾN THÔNG MINH:
   ├── Khách vãng lai:                ──> Reviews v1 (Không gọi ratings)
   └── Đăng nhập user "jason":        ──> Reviews v2 (Gọi ratings, hiển thị sao đen)
```

- **Lợi ích thực tế**: Triển khai tính năng mới (Feature Flagging / Canary Release) mà không cần can thiệp hay redeploy lại bất kỳ Pod nào!

---

# SLIDE 9: QUY TRÌNH 4 BƯỚC LIVE DEMO & KIỂM CHỨNG HỆ THỐNG

### Bước 1: Khởi Tạo Môi Trường Toàn Diện
```powershell
.\setup-and-run.ps1
```
*Tự động deploy Bookinfo, cấu hình Gateway, kiểm tra trạng thái 2/2 ready của toàn bộ Pods.*

### Bước 2: Truy Cập & Kiểm Chứng Phiên Bản Mặc Định (Baseline)
- Mở `http://localhost/productpage`.
- Chưa đăng nhập: F5 nhiều lần, thấy reviews luân phiên xuất hiện giữa v1, v2, v3 theo thuật toán Round-Robin mặc định của Kubernetes Service.

### Bước 3: Áp Dụng Canary Routing Cho Tester `jason`
```powershell
kubectl apply -f networking/virtual-service-reviews-test-v2.yaml
```
- Đăng nhập với tên `jason` (mật khẩu bất kỳ) ➔ Luôn luôn thấy **Sao Đen (v2)**.
- Đăng xuất ➔ Quay trở lại **Không Sao (v1)** 100%.

### Bước 4: Kiểm Chứng Khả Năng Chịu Lỗi (Fault Injection)
- Apply rule chèn delay 7s vào `ratings` ➔ Web vẫn hiển thị nội dung sách bình thường, phần đánh giá hiện fallback thông báo lỗi nhẹ chứ toàn bộ trang web không bị crash!

---

# SLIDE 10: TỔNG KẾT & ĐÁNH GIÁ KIẾN TRÚC: MONOLITH VS BOOKINFO

### Bảng Đánh Đổi Kiến Trúc Toàn Diện (Architectural Trade-offs):

| Tiêu Chí So Sánh | Ứng Dụng Đơn Khối (Monolith) | Kiến Trúc Bookinfo Microservices |
|---|---|---|
| **Công Nghệ (Technology Stack)** | Bị trói buộc vào 1 ngôn ngữ duy nhất cho toàn bộ hệ thống | **Polyglot linh hoạt**: Python cho UI, Ruby cho dữ liệu, Java cho xử lý nặng |
| **Độc Lập Triển Khai (Deployment)** | Mỗi lần sửa 1 dòng code phải build và deploy lại toàn bộ ứng dụng | **Độc lập hoàn toàn**: Nâng cấp `reviews` từ v1 lên v3 mà `productpage` không ngừng hoạt động |
| **Mức Độ Phức Tạp Vận Hành** | Đơn giản, chỉ cần 1 pipeline CI/CD và 1 process duy nhất | **Rất phức tạp**: Cần Kubernetes để điều phối, Istio để định tuyến, Prometheus để giám sát |
| **Lan Truyền Sự Cố (Failure Cascade)** | Một lỗi rò rỉ bộ nhớ (Memory Leak) có thể làm sập toàn bộ hệ thống | **Khoanh vùng sự cố**: Service `ratings` bị sập thì trang sách vẫn đọc được bình thường |

---

## 🎙️ KỊCH BẢN THUYẾT TRÌNH 10 PHÚT — CHỦ ĐỀ BOOKINFO APPLICATION

- **[0:00 – 1:00] Slide 1: Đặt Vấn Đề**: *"Kính thưa Thầy/Cô, em là Tường. Để kiểm chứng toàn bộ lý thuyết về Microservices, Docker, Kubernetes, Istio, Prometheus và Grafana, em đã xây dựng và triển khai hệ thống thực nghiệm Bookinfo. Đây là ứng dụng benchmark kinh điển mô phỏng website bán sách trực tuyến với 4 microservices đa ngôn ngữ."*
- **[1:00 – 2:30] Slide 2, 3 & 4: Topo Đa Dịch Vụ & Chi Tiết Service**: *(Chỉ vào sơ đồ kiến trúc)*: *"Kiến trúc Bookinfo gồm 4 service: `productpage` viết bằng Python Flask đóng vai trò Aggregator đón nhận request và render HTML; `details` viết bằng Ruby Sinatra cung cấp thông tin xuất bản sách; và `ratings` viết bằng Node.js Express cung cấp điểm đánh giá số học."*
- **[2:30 – 4:00] Slide 5 & 6: Reviews 3 Phiên Bản & Lan Truyền Header**: *(Mở file `LibertyRestEndpoint.java` và `productpage.py`)*: *"Trái tim của dự án là dịch vụ `reviews` viết bằng Java Open Liberty với 3 phiên bản: v1 không sao, v2 sao đen, và v3 sao đỏ. Điểm mấu chốt trong code là hàm `getForwardHeaders()` ở `productpage.py` tự động lan truyền header `end-user` và trace ID `x-request-id` xuống các service sau, tạo điều kiện cho Istio nhận diện danh tính người dùng."*
- **[4:00 – 5:30] Slide 7 & 8: Hạ Tầng Kubernetes & Định Tuyến Istio**: *(Chỉ vào file `bookinfo.yaml` và `bookinfo-gateway.yaml`)*: *"Trên Kubernetes, hệ thống chạy 6 Deployments và 4 Services. Nhờ cơ chế sidecar injection, mỗi Pod đều đạt trạng thái 2/2 ready. Istio điều phối luồng thông qua Gateway mở cổng 80, DestinationRule phân loại subset v1, v2, v3, và VirtualService điều hướng chính xác tester `jason` vào bản v2."*
- **[5:30 – 6:30] Slide 9 & 10: Tổng Kết & Đánh Đổi**: *"So với Monolith, Bookinfo đem lại sự độc lập công nghệ tuyệt đối giữa các nhóm phát triển và khả năng cô lập lỗi xuất sắc. Đánh đổi lại là độ phức tạp vận hành mạng đòi hỏi phải có nền tảng Cloud-Native vững chắc."*
- **[6:30 – 9:30] Live Demo Thực Nghiệm 4 Bước**: *(Mở trình duyệt thực hiện trực tiếp)*:
  1. Mở `http://localhost/productpage`, F5 kiểm chứng Round-Robin v1/v2/v3.
  2. Apply `virtual-service-reviews-test-v2.yaml`.
  3. Đăng nhập user `jason` ➔ Thấy sao đen ổn định.
  4. Đăng xuất ➔ Thấy bản v1 không sao. Chứng minh Canary Routing thành công 100%.
- **[9:30 – 10:00] Kết Luận Toàn Bộ Chuyên Đề**: Tuyên bố hoàn thành toàn bộ bài báo cáo giữa kỳ và sẵn sàng trả lời các câu hỏi phản biện của Hội đồng.

