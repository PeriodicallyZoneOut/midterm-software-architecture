# Triển khai chi tiết (Implementation Details) — Bookinfo

Tài liệu này đi sâu vào phân tích mã nguồn thực tế, các tệp Dockerfile đa tầng, cấu hình tài nguyên Kubernetes và các tệp Custom Resource Definition (CRD) của Istio Service Mesh trong Bookinfo.

---

## 1. Phân tích Mã Nguồn các Microservices

### 1.1. `productpage` (Python / Flask) — Aggregator & Tracing Propagation
Nằm tại: [`src/productpage/productpage.py`](../source/src/productpage/productpage.py)

#### Cơ chế Lan truyền Tracing Headers (`getForwardHeaders`):
Khi nhận request từ trình duyệt, `productpage` bắt buộc phải trích xuất các header liên quan đến tracing và user context để chuyển tiếp sang các service nội bộ:
```python
def getForwardHeaders(request):
    headers = {}

    # Trích xuất và tiêm B3 tracing context qua OpenTelemetry
    ctx = propagator.extract(carrier={k.lower(): v for k, v in request.headers})
    propagator.inject(headers, ctx)

    # Chuyển tiếp user context phục vụ Canary Routing
    if 'user' in session:
        headers['end-user'] = session['user']

    # Danh sách header tiêu chuẩn của Istio
    incoming_headers = [
        'x-request-id',
        'x-b3-traceid',
        'x-b3-spanid',
        'x-b3-sampled',
        'x-b3-flags',
        'x-ot-span-context',
        'user-agent',
    ]

    for ihdr in incoming_headers:
        val = request.headers.get(ihdr)
        if val is not None:
            headers[ihdr] = val

    return headers
```
- **Ý nghĩa kiến trúc**: Nếu không forward `end-user`, Istio không thể nhận diện được người dùng `jason` để định tuyến sang phiên bản `reviews:v2`. Nếu không forward `x-request-id` và `x-b3-*`, chuỗi vết distributed trace sẽ bị đứt gãy.

#### Endpoint `/metrics` phục vụ Prometheus:
```python
from prometheus_client import Counter, generate_latest

@app.route('/metrics')
def metrics():
    return generate_latest()
```

---

### 1.2. `reviews` (Java / Open Liberty) — Quản lý Phiên bản qua Biến Môi trường
Nằm tại: [`src/reviews/reviews-application/src/main/java/application/rest/LibertyRestEndpoint.java`](../source/src/reviews/reviews-application/src/main/java/application/rest/LibertyRestEndpoint.java)

#### Logic phân nhánh v1, v2, v3:
Mã nguồn Java của cả 3 phiên bản là **chung một codebase**, sự khác biệt hành vi được cấu hình hoàn toàn qua biến môi trường (12-Factor App methodology):
```java
public class LibertyRestEndpoint extends Application {
    private final static Boolean ratings_enabled = Boolean.valueOf(System.getenv("ENABLE_RATINGS"));
    private final static String star_color = System.getenv("STAR_COLOR") == null ? "black" : System.getenv("STAR_COLOR");

    private JsonObject getRatings(int productId, JsonObjectBuilder builder, HttpHeaders requestHeaders) {
        if (ratings_enabled) { // Chỉ v2 và v3 mới gọi downstream ratings
            JsonObject ratingsResponse = getRatingsFromRatingsService(productId, requestHeaders);
            if (ratingsResponse != null) {
                if (ratingsResponse.containsKey("ratings")) {
                    JsonObject ratings = ratingsResponse.getJsonObject("ratings");
                    builder.add("ratings", ratings);
                    builder.add("color", star_color); // "black" với v2, "red" với v3
                }
            }
        }
        return builder.build();
    }
}
```
- **v1**: `ENABLE_RATINGS = false` -> Trả về danh sách review ngay lập tức, không gọi service `ratings`.
- **v2**: `ENABLE_RATINGS = true`, `STAR_COLOR = black` -> Gọi sang `http://ratings:9080/ratings/0`, trả về sao đen.
- **v3**: `ENABLE_RATINGS = true`, `STAR_COLOR = red` -> Gọi sang `http://ratings:9080/ratings/0`, trả về sao đỏ.

---

### 1.3. `ratings` (Node.js / Express) — Giả lập Lỗi & Độ trễ
Nằm tại: [`src/ratings/ratings.js`](../source/src/ratings/ratings.js)

Dịch vụ này hỗ trợ các cờ môi trường đặc biệt để phục vụ kiểm thử hỗn loạn (Chaos Engineering):
```javascript
if (process.env.SERVICE_VERSION === 'v-unavailable') {
    // Làm dịch vụ gián đoạn ngắt quãng mỗi 60 giây
    setInterval(function () {
        unavailable = !unavailable;
    }, 60000);
}
```

---

## 2. Dockerization & Multi-stage Build

### Phân tích `src/reviews/Dockerfile`:
Để tối ưu kích thước image và bảo mật, `reviews` áp dụng kỹ thuật Multi-stage build của Docker:
```dockerfile
# Stage 1: Build Java Application bằng Gradle
FROM gradle:4.8.1-jdk8-alpine as builder
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src/reviews-wlpcfg
RUN gradle build

# Stage 2: Chuyển artifact sang Runtime Image gọn nhẹ
FROM open-liberty:kernel-slim
COPY --chown=1001:0 --from=builder /home/gradle/src/reviews-wlpcfg/build/libs/wlp/usr/servers/defaultServer /opt/ibm/wlp/usr/servers/defaultServer
EXPOSE 9080
```
- **Lợi ích**: Toàn bộ công cụ biên dịch (Gradle, JDK, cache thư viện build) ở Stage 1 bị loại bỏ hoàn toàn khỏi image cuối cùng, chỉ giữ lại WebSphere Liberty kernel slim và file `.war`. Giúp giảm kích thước image từ >800MB xuống còn ~150MB, giảm bề mặt tấn công bảo mật (Attack surface).

---

## 3. Cấu hình Tài nguyên Kubernetes (`platform/kube/bookinfo.yaml`)

### 3.1. Phân tách Service và Pods qua Label Selectors
Mỗi service trong Bookinfo là một `ClusterIP`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: reviews
  labels:
    app: reviews
    service: reviews
spec:
  ports:
  - port: 9080
    name: http
  selector:
    app: reviews # Ánh xạ tới cả 3 Deployment: reviews-v1, reviews-v2, reviews-v3!
```
- Khi chưa có Istio VirtualService, Kubernetes Service mặc định định tuyến ngẫu nhiên (Round-Robin) tới tất cả các Pod có nhãn `app: reviews`, bất kể là `version: v1`, `v2` hay `v3`.

### 3.2. Khai báo Deployment với nhãn Version rõ ràng:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reviews-v2
  labels:
    app: reviews
    version: v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: reviews
      version: v2
  template:
    metadata:
      labels:
        app: reviews
        version: v2
    spec:
      serviceAccountName: bookinfo-reviews
      containers:
      - name: reviews
        image: docker.io/istio/examples-bookinfo-reviews-v2:1.20.0
        env:
        - name: ENABLE_RATINGS
          value: "true"
        - name: STAR_COLOR
          value: "black"
        ports:
        - containerPort: 9080
```

---

## 4. Cấu hình Istio Custom Resource Definitions (CRDs)

### 4.1. Istio Ingress Gateway & VirtualService (`networking/bookinfo-gateway.yaml`)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: bookinfo-gateway
spec:
  selector:
    istio: ingressgateway # Sử dụng Istio Ingress Gateway mặc định
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: bookinfo
spec:
  hosts:
  - "*"
  gateways:
  - bookinfo-gateway
  http:
  - match:
    - uri:
        exact: /productpage
    - uri:
        prefix: /static
    - uri:
        exact: /login
    - uri:
        exact: /logout
    - uri:
        prefix: /api/v1/products
    route:
    - destination:
        host: productpage
        port:
          number: 9080
```

### 4.2. Khai báo Subsets qua DestinationRule (`networking/destination-rule-all.yaml`)
`DestinationRule` định nghĩa các tập hợp con (subsets) của từng service dựa trên nhãn Kubernetes:
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  - name: v3
    labels:
      version: v3
```

### 4.3. Canary Routing theo HTTP Header (`networking/virtual-service-reviews-test-v2.yaml`)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason # Khớp chính xác user jason
      route:
      - destination:
          host: reviews
          subset: v2 # Chuyển tới v2 (sao đen)
  - route:
    - destination:
        host: reviews
        subset: v1 # Mọi user khác về v1 (không sao)
```

### 4.4. Fault Injection — Chèn độ trễ (`networking/virtual-service-ratings-test-delay.yaml`)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ratings
spec:
  hosts:
  - ratings
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    fault:
      delay:
        percentage:
          value: 100.0
        fixedDelay: 7s # Trì hoãn cố định 7 giây
    route:
    - destination:
        host: ratings
        subset: v1
```

