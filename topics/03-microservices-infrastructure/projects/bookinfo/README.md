# Bookinfo — Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana

Trọng tâm: Kiến trúc Microservices Polyglot (Python, Ruby, Java, Node.js), Kubernetes Workloads (Deployments, Services), Istio Service Mesh (Envoy sidecars, Ingress Gateway, VirtualService, DestinationRule, Canary routing, Fault injection, mTLS), và Observability (Prometheus scraping Envoy metrics, Grafana dashboards).

## Nội dung

- [Áp dụng kiến thức vào project](project-knowledge-application-implementation/README.md).
  - [01-concepts.md](project-knowledge-application-implementation/01-concepts.md): Lý thuyết Microservices, Polyglot, Service Mesh, Metrics.
  - [02-component-mapping.md](project-knowledge-application-implementation/02-component-mapping.md): Bảng mapping 4 microservices (`productpage`, `details`, `reviews` v1/v2/v3, `ratings`) -> Source code -> Port -> Kubernetes resource.
  - [03-implementation.md](project-knowledge-application-implementation/03-implementation.md): Phân tích code chi tiết, Dockerfile, Kubernetes manifests, Istio CRDs.
  - [04-verification-and-tradeoffs.md](project-knowledge-application-implementation/04-verification-and-tradeoffs.md): Kịch bản kiểm chứng (Canary, Fault injection, Self-healing) và đánh đổi kiến trúc.
- [Source đã copy](source/) · [Nguồn và phiên bản](SOURCE-NOTES.md).
- [Runbook chạy demo](demo/runbook.md).
- [Evidence](evidence/README.md).

## Giới thiệu hệ thống Bookinfo

Bookinfo là ứng dụng mẫu kinh điển của Istio và Cloud Native Computing Foundation (CNCF), mô phỏng một trang web đánh giá và mua sách trực tuyến. Ứng dụng gồm 4 microservices riêng biệt:

1. **`productpage`** (Python / Flask): Nhận request từ người dùng, gọi `details` và `reviews` để tổng hợp thành trang web hoàn chỉnh.
2. **`details`** (Ruby / WEBrick & Sinatra): Cung cấp thông tin chi tiết về sách (thể loại, số trang, nhà xuất bản, ISBN).
3. **`reviews`** (Java / Open Liberty): Cung cấp các bài đánh giá sách. Gồm 3 phiên bản đồng thời:
   - **v1**: Không gọi service ratings (hiển thị bài đánh giá thuần text, không có sao).
   - **v2**: Gọi `ratings` service và hiển thị sao đánh giá màu đen (1–5 black stars).
   - **v3**: Gọi `ratings` service và hiển thị sao đánh giá màu đỏ (1–5 red stars).
4. **`ratings`** (Node.js / Express): Cung cấp điểm đánh giá sao cho cuốn sách (có thể kết nối MySQL hoặc MongoDB).

