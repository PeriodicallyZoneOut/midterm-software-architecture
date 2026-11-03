---
marp: true
theme: default
paginate: true
header: 'Chủ đề 3.1: Kiến trúc Microservices | Tường'
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

# SLIDE 1: ĐẶT VẤN ĐỀ & SỰ CHUYỂN DỊCH TỪ MONOLITH SANG MICROSERVICES
- **Học phần**: Kiến trúc Phần mềm — Báo cáo Chuyên sâu: **Microservices Architecture**
- **Người thực hiện**: Tường (Thời lượng: 10 phút)
- **Hệ thống minh chứng**: [Bookinfo](../../projects/bookinfo/README.md)

### Động Lực Chuyển Dịch:
- **Monolith Limitations**: Codebase khổng lồ, phụ thuộc chặt chẽ (tight coupling), thời gian build/test kéo dài hàng giờ.
- **Blast Radius**: Lỗi rò rỉ bộ nhớ ở module phụ có thể làm sập toàn bộ ứng dụng doanh nghiệp.
- **Scaling Bottleneck**: Buộc phải scale toàn bộ application process cồng kềnh dù chỉ một chức năng bị nghẽn.
- **Mục tiêu Microservices**: Tách biệt thành các dịch vụ nhỏ, tự trị (Autonomous), triển khai độc lập, tối ưu hóa theo domain.

---

# SLIDE 2: SO SÁNH 3 MÔ HÌNH: MONOLITH VS MODULAR MONOLITH VS MICROSERVICES

| Tiêu chí Đánh giá | Monolith | Modular Monolith | Microservices (Bookinfo) |
|---|---|---|---|
| **Cấu trúc Runtime** | 1 process duy nhất chạy toàn bộ | 1 process duy nhất, chia package | Mỗi service là 1 container/process độc lập |
| **Cơ sở Dữ liệu** | 1 Shared Database tập trung | 1 Shared DB, phân chia schema | **Database-per-service** hoàn toàn tự trị |
| **Công nghệ (Tech Stack)** | Đồng nhất 1 ngôn ngữ/framework | Đồng nhất 1 ngôn ngữ | **Polyglot**: Tối ưu tech stack theo tác vụ |
| **Blast Radius** | Rất lớn: Lỗi 1 module sập cả app | Lớn: Lỗi runtime dừng cả process | **Nhỏ**: Lỗi được cô lập trong từng service |
| **Khả năng Scale** | Scale toàn bộ ứng dụng cồng kềnh | Scale toàn bộ binary | **Linh hoạt**: Scale độc lập từng service nghẽn |
| **Vận hành (DevOps)** | Thấp (Deploy 1 file duy nhất) | Trung bình | **Cao** (Đòi hỏi K8s, Mesh, Observability) |

*Kết luận: Microservices đánh đổi sự đơn giản vận hành để đổi lấy tính độc lập phát triển và khả năng co giãn quy mô lớn.*

---

# SLIDE 3: DOMAIN-DRIVEN DESIGN (DDD) & BOUNDED CONTEXTS
*Nguyên tắc phân rã nghiệp vụ theo Eric Evans*

### 1. Bounded Contexts trong Bookinfo:
- **`productpage`**: Presentation Tier & API Aggregator — hiển thị trang tổng hợp.
- **`details`**: Book Catalog Context — chịu trách nhiệm quản lý thông tin xuất bản sách.
- **`reviews`**: Social Proof Context — quản lý các đánh giá và bình luận của độc giả.
- **`ratings`**: Scoring Context — quản lý điểm số sao từ 1 đến 5.

### 2. Nguyên tắc Single Responsibility (SRP):
- Mỗi microservice sở hữu đúng một năng lực nghiệp vụ duy nhất.
- Khi nghiệp vụ đánh giá sách thay đổi (thêm sao đỏ v3), chỉ team `reviews` can thiệp, team `details` không cần build hay test lại.

---

# SLIDE 4: NGUYÊN TẮC DATABASE-PER-SERVICE & TỰ TRỊ DỮ LIỆU
*Loại bỏ Shared Database Bottleneck trong Microservices*

### Tại sao Cấm Dùng Chung Database?
- Tránh việc service A truy vấn trực tiếp vào bảng của service B làm phá vỡ tính đóng gói dữ liệu (Encapsulation).
- Cho phép mỗi team tự do lựa chọn công nghệ lưu trữ (Polyglot Persistence): Relational SQL, NoSQL Document, hoặc In-memory Cache.

### Mô hình Lưu trữ trong Bookinfo:
```text
[ productpage ] ──REST──> [ details ]  (In-Memory Metadata)
      │
      └──REST──> [ reviews ] (In-Memory Liberty)
                     │
                     └──REST──> [ ratings ] ──TCP──> [ MySQL / MongoDB DB ]
```
- Dịch vụ `ratings` hỗ trợ kết nối database chuyên biệt (MySQL qua `src/ratings/mysqldb-init.sql`).
- Các dịch vụ khác muốn lấy điểm số bắt buộc phải gọi qua REST API của `ratings`, hoàn toàn không có quyền kết nối trực tiếp vào DB.

---

# SLIDE 5: KIẾN TRÚC POLYGLOT TRONG MÃ NGUỒN BOOKINFO
*Tối ưu hóa ngôn ngữ và runtime theo đặc thù tác vụ*

### Phân tích 4 Ngôn ngữ trong Codebase:
1. **Python (Flask)** — `src/productpage/productpage.py`: Cú pháp tinh gọn, template engine Jinja2 mạnh mẽ để render HTML nhanh chóng.
2. **Ruby (WEBrick/Sinatra)** — `src/details/details.rb`: Cú pháp linh hoạt, gọn nhẹ cho việc tra cứu dữ liệu cấu trúc JSON.
3. **Java (Open Liberty / JAX-RS)** — `src/reviews/`: Nền tảng enterprise vững chắc, quản lý đa luồng an toàn cho các tác vụ nghiệp vụ phức tạp.
4. **Node.js (Express)** — `src/ratings/ratings.js`: Non-blocking Event Loop xử lý I/O bất đồng bộ cực nhanh cho dịch vụ tra cứu điểm số.

*Chứng minh: Microservices giải phóng các đội ngũ kỹ sư khỏi sự trói buộc vào một ngôn ngữ duy nhất của Monolith.*

---

# SLIDE 6: GIAO TIẾP LIÊN DỊCH VỤ — REST/JSON CONTRACTS & 12-FACTOR APP
*Phân tích mã nguồn `src/reviews/.../LibertyRestEndpoint.java`*

### 1. HTTP REST/JSON Contracts:
- Các microservice giao tiếp phi trạng thái (Stateless) qua HTTP REST API tiêu chuẩn.
- Endpoint `/reviews/<id>` trả về payload JSON chuẩn hóa chứa danh sách bài đánh giá và điểm số sao.

### 2. Code Mapping: 12-Factor App Methodology:
```java
public class LibertyRestEndpoint extends Application {
    private final static Boolean ratings_enabled = Boolean.valueOf(System.getenv("ENABLE_RATINGS"));
    private final static String star_color = System.getenv("STAR_COLOR") == null ? "black" : System.getenv("STAR_COLOR");

    private JsonObject getRatings(int productId, JsonObjectBuilder builder, HttpHeaders requestHeaders) {
        if (ratings_enabled) {
            JsonObject ratingsResponse = getRatingsFromRatingsService(productId, requestHeaders);
            if (ratingsResponse != null && ratingsResponse.containsKey("ratings")) {
                builder.add("ratings", ratingsResponse.getJsonObject("ratings"));
                builder.add("color", star_color);
            }
        }
        return builder.build();
    }
}
```
- Cùng 1 codebase Java, hành vi của 3 phiên bản (v1 không sao, v2 sao đen, v3 sao đỏ) được cấu hình 100% qua biến môi trường.

---

# SLIDE 7: CONTEXT PROPAGATION & DISTRIBUTED TRACING
*Giải quyết bài toán mất dấu vết trong hệ thống phân tán*

### Code Deep-Dive: Hàm `getForwardHeaders` trong `productpage.py`:
```python
def getForwardHeaders(request):
    headers = {}
    # 1. Trích xuất và tiêm B3 tracing context (OpenTelemetry)
    ctx = propagator.extract(carrier={k.lower(): v for k, v in request.headers})
    propagator.inject(headers, ctx)

    # 2. Chuyển tiếp danh tính người dùng phục vụ Canary Routing
    if 'user' in session:
        headers['end-user'] = session['user']

    # 3. Chuyển tiếp tracing headers chuẩn của Istio
    for hdr in ['x-request-id', 'x-b3-traceid', 'x-b3-spanid', 'x-b3-sampled']:
        if hdr in request.headers:
            headers[hdr] = request.headers[hdr]
    return headers
```
- **Tại sao bắt buộc?**: Nếu `productpage` không chuyển tiếp `x-request-id`, hạ tầng giám sát không thể liên kết chuỗi gọi giữa 4 services độc lập.

---

# SLIDE 8: API GATEWAY & AGGREGATOR PATTERN
*Tập trung hóa điểm truy cập từ phía Client*

### 1. Vấn đề khi Client gọi trực tiếp từng Microservice:
- Trình duyệt phải thực hiện quá nhiều round-trip calls qua Internet có độ trễ cao.
- Client bị phụ thuộc vào địa chỉ IP/Port nội bộ của từng service, gây khó khăn khi tái cấu trúc backend.

### 2. Áp dụng Aggregator Pattern trong Bookinfo:
- `productpage` đóng vai trò là **Frontend Aggregator**:
  - Nhận 1 request duy nhất từ trình duyệt: `GET /productpage`.
  - Thực hiện gọi nội bộ song song (In-cluster calls) tới `details` và `reviews`.
  - Tổng hợp toàn bộ dữ liệu JSON thành một trang HTML hoàn chỉnh trước khi trả lời Client.
- Giảm số lượng request ra ngoài Internet từ 3-4 calls xuống còn đúng **1 HTTP call duy nhất**.

---

# SLIDE 9: KIỂM SOÁT LỖI LAN TRUYỀN (CASCADING FAILURE & RESILIENCE)
*Xây dựng hệ thống có khả năng chịu lỗi bền bỉ*

### Nguy cơ Cascading Failure trong Chuỗi Gọi Đồng Bộ:
$$T_{\text{total}} = T_{\text{productpage}} + T_{\text{reviews}} + T_{\text{ratings}}$$
- Nếu `ratings` bị treo hoặc nghẽn mạng, luồng xử lý của `reviews` sẽ bị giữ lại (blocked thread), kéo theo `productpage` bị cạn kiệt connection pool.

### Cơ Chế Phòng Vệ trong Code & Hạ Tầng:
1. **Client Timeout**: Đặt ngưỡng timeout tối đa 2.5 giây khi `reviews` gọi `ratings`.
2. **Graceful Degradation (Suy thoái Duyên dáng)**: Nếu `ratings` timeout, code bắt ngoại lệ và trả về bài đánh giá không kèm sao, thay vì trả lỗi HTTP 500 sập toàn bộ web.
3. **Circuit Breaker (Ngắt mạch)**: Ngắt kết nối tạm thời tới service lỗi để tránh làm nghẽn dây chuyền.

---

# SLIDE 10: TỔNG KẾT & ARCHITECTURAL TRADE-OFFS CỦA MICROSERVICES

### Bảng Đánh Đổi Kiến Trúc (Trade-offs):

| Lợi Thế Đạt Được (Pros) | Đánh Đổi & Chi Phí Thực Tế (Cons) | Giải Pháp Khắc Phục |
|---|---|---|
| **Independent Deployability**: Release từng service riêng rẽ không sợ ảnh hưởng. | **Distributed Complexity**: Khó debug lỗi qua nhiều chặng mạng. | Áp dụng Distributed Tracing (Jaeger/Zipkin) & OpenTelemetry. |
| **Fault Isolation**: Lỗi ở `ratings` không làm sập `productpage`. | **Network Latency**: Tăng độ trễ do gọi qua giao thức HTTP so với in-memory call. | Tối ưu payload JSON, kết nối HTTP/2 hoặc gRPC nội bộ. |
| **Tech Diversity**: Tự do chọn Python, Ruby, Java, Node.js. | **Operational Burden**: Phức tạp trong việc build, deploy và monitor nhiều runtime. | Chuẩn hóa Docker container và hạ tầng Kubernetes. |

---

## 🎙️ KỊCH BẢN THUYẾT TRÌNH 10 PHÚT — CHỦ ĐỀ MICROSERVICES

- **[0:00 – 1:00] Slide 1 & 2**: *"Kính thưa Thầy/Cô, em là Tường, trình bày về Kiến trúc Microservices. Nhược điểm lớn nhất của Monolith là Blast Radius: lỗi 1 module sập cả hệ thống. Để giải quyết, hệ thống Bookinfo phân rã thành các dịch vụ độc lập, đánh đổi độ phức tạp vận hành để lấy tính tự trị và khả năng mở rộng linh hoạt."*
- **[1:00 – 2:30] Slide 3 & 4**: *"Bookinfo áp dụng nguyên tắc Single Responsibility của DDD: `productpage`, `details`, `reviews`, `ratings` là các Bounded Context riêng biệt. Mỗi dịch vụ sở hữu dữ liệu độc lập (Database-per-service), tuyệt đối không truy cập trực tiếp DB của nhau để bảo vệ tính đóng gói."*
- **[2:30 – 4:00] Slide 5 & 6**: *(Mở file `LibertyRestEndpoint.java`)*: *"Bookinfo minh chứng tính Polyglot hoàn hảo: Python cho web, Ruby cho metadata, Java cho enterprise logic và Node.js cho I/O. Mã nguồn Java tuân thủ phương pháp 12-Factor App: chung 1 codebase, hành vi v1, v2, v3 được cấu hình qua biến môi trường."*
- **[4:00 – 5:30] Slide 7 & 8**: *(Mở file `productpage.py` dòng 125)*: *"Trong môi trường phân tán, hàm `getForwardHeaders` bắt buộc phải chuyển tiếp các header `end-user`, `x-request-id`, `x-b3-*`. Nếu không forward, chuỗi Distributed Trace sẽ đứt gãy. Đồng thời `productpage` đóng vai trò API Aggregator gom các lời gọi nội bộ để tối ưu trải nghiệm người dùng."*
- **[5:30 – 6:30] Slide 9 & 10**: *"Để chống lỗi lan truyền (Cascading Failure), hệ thống áp dụng cơ chế Graceful Degradation và Circuit Breaker. Đánh đổi lớn nhất của Microservices là độ trễ mạng và độ phức tạp vận hành phân tán, nhưng đây là giải pháp bắt buộc cho các hệ thống quy mô lớn."*
- **[6:30 – 9:30] Live Demo**: Chạy `kubectl port-forward svc/productpage 9080:9080`, F5 web chứng minh 4 microservices hoạt động, giải thích luồng gọi dữ liệu.
- **[9:30 – 10:00] Kết bài & Vấn đáp**: Tuyên bố kết thúc bài thuyết trình Microservices.

