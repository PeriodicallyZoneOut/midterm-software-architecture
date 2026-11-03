# Source — Online Boutique (Architecture Representation)

- **Workspace path gốc:** `week-03/microservices-demo` (đã đồng bộ từ `topics/03-microservices-infrastructure/projects/online-boutique/source/` theo hướng dẫn tại `docs/TEAM-ASSIGNMENT.md` Mục 2 & Mục 5).
- **Upstream Repository:** https://github.com/GoogleCloudPlatform/microservices-demo
- **Branch / Commit Hash:** `main` — `38e7348eb289eb5b87c0c6e8cb19ced0449dc389` (Release tag tương ứng trong manifest: `v0.10.7`).
- **License:** Apache License 2.0 (`LICENSE`).
- **Điểm đọc code chính cho Architecture Representation:**
  - Hợp đồng giao tiếp gRPC chung: `protos/demo.proto` (`package hipstershop`)
  - API Gateway / Web UI: `src/frontend/main.go`, `src/frontend/handlers.go`, `src/frontend/rpc.go`
  - Checkout Orchestrator: `src/checkoutservice/main.go`
  - Cart Service & Redis Store: `src/cartservice/src/services/CartService.cs`, `src/cartservice/src/cartstore/RedisCartStore.cs`
  - Product Catalog & JSON Store: `src/productcatalogservice/server.go`, `src/productcatalogservice/product_catalog.go`, `src/productcatalogservice/products.json`
  - Currency Service: `src/currencyservice/server.js`, `src/currencyservice/data/currency_conversion.json`
  - Payment / Shipping / Email / Recommendation / Ad: `src/paymentservice/charge.js`, `src/shippingservice/main.go`, `src/emailservice/email_server.py`, `src/recommendationservice/recommendation_server.py`, `src/adservice/src/main/java/hipstershop/AdService.java`
  - Cấu hình Deployment: `release/kubernetes-manifests.yaml`, `kustomize/`

## Checklist Nguồn & Phiên bản
- [x] Ghi commit/tag (`38e7348eb289eb5b87c0c6e8cb19ced0449dc389`, image tag `v0.10.7`) và license (`Apache-2.0`).
- [x] Ghi thay đổi local: Giữ nguyên mã nguồn upstream không chỉnh sửa logic để đảm bảo tính trung thực khi đối chiếu kiến trúc.
- [x] Copy nguyên thư mục project vào `source/` phục vụ riêng cho Chủ đề 2 (`theanh-architecture`).
- [x] Không chứa secret hay thông tin nhạy cảm trong cấu hình mặc định.
