# Source — Bookinfo

Workspace path: `topics/03-microservices-infrastructure/projects/bookinfo/source`.

Nguồn gốc upstream: [https://github.com/istio/istio/tree/master/samples/bookinfo](https://github.com/istio/istio/tree/master/samples/bookinfo) thuộc repository Istio (Apache License 2.0).

Điểm đọc code và cấu hình chính:
- `src/productpage/productpage.py`: Flask frontend, tracing headers propagation (`getForwardHeaders`), Prometheus `/metrics`.
- `src/details/details.rb`: Ruby WEBrick service cung cấp thông tin sách, endpoint `/health`.
- `src/reviews/reviews-application/src/main/java/application/rest/LibertyRestEndpoint.java`: Java JAX-RS endpoint, cờ `ENABLE_RATINGS` và `STAR_COLOR` điều khiển hành vi v1/v2/v3.
- `src/ratings/ratings.js`: Node.js Express service, quản lý điểm sao và cơ chế lỗi timeout giả lập (`v-unavailable`, `v-unhealthy`).
- `platform/kube/bookinfo.yaml`: Manifests triển khai toàn bộ 4 Services, 6 Deployments (productpage-v1, details-v1, reviews-v1, reviews-v2, reviews-v3, ratings-v1) và ServiceAccounts.
- `networking/bookinfo-gateway.yaml`: Cấu hình Istio Gateway (port 80) và VirtualService định tuyến traffic vào `productpage`.
- `networking/destination-rule-all.yaml`: Định nghĩa DestinationRule cho cả 4 services với các subset tương ứng theo nhãn version (`v1`, `v2`, `v3`).
- `networking/virtual-service-reviews-test-v2.yaml`: Cấu hình Canary routing dựa trên HTTP header `end-user: jason` vào `reviews:v2`.
- `networking/virtual-service-reviews-80-20.yaml` / `50-v3.yaml`: Cấu hình phân chia lưu lượng theo trọng số (Weighted traffic shifting).
- `networking/virtual-service-ratings-test-delay.yaml`: Cấu hình fault injection chèn độ trễ 7 giây vào service `ratings`.

Bản source đã được sao chép nguyên trạng từ Istio sample, sẵn sàng build hoặc apply trực tiếp bằng `kubectl` với các pre-built container images chính thức từ `docker.io/istio/examples-bookinfo-*`.

