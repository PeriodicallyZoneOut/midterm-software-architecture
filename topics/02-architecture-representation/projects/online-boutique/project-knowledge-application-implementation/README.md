# Áp dụng Kiến thức Architecture Representation — Online Boutique

Thư mục này chứa trọn bộ tài liệu biểu diễn kiến trúc (**Architecture Representation**) cho hệ thống mã nguồn mở **Google Online Boutique (`microservices-demo`)**, đáp ứng đầy đủ các tiêu chí của **Thế Anh (Mục 5 — `docs/TEAM-ASSIGNMENT.md`)** và **Mục 4 & Mục 8 (`docs/INVENTORY.md`)**:

1. **[01-concepts.md](01-concepts.md)** — **Stakeholders, 4+1 View Model, C4 Model (Level 1–4) & Data Schema/Model:**
   - Phân biệt View vs. Notation/UML vs. C4 Zoom Levels.
   - Bảng Stakeholder & Concern Matrix.
   - **4+1 View Model** đầy đủ (Logical View, Development View, Process View, Physical/Deployment View, `+1` Scenarios).
   - **C4 Model** 4 cấp độ (System Context, Container, Component, Code).
   - **Data Schema / Data Model thực tế:** Cấu trúc Key-Value Protobuf trong `redis-cart` (`RedisCartStore.cs`), JSON Schema của `products.json` và `currency_conversion.json`, cùng hệ thống hợp đồng `protos/demo.proto`. Giải thích rõ vì sao baseline không dùng RDBMS/SQL.

2. **[02-component-mapping.md](02-component-mapping.md)** — **Bảng Ánh xạ Tổng thể & Component Cards (10 trường):**
   - Bảng ánh xạ từ Hộp sơ đồ $\rightarrow$ Hợp đồng Protobuf (`protos/demo.proto`) $\rightarrow$ Source Symbol (`file:line`) $\rightarrow$ Runtime Kubernetes (`Deployment`, `Service`, Port, Env, Probes, Resources) $\rightarrow$ Bằng chứng kiểm chứng.
   - 6 thẻ Component Cards chi tiết theo đúng quy cách 10 mục của `docs/INVENTORY.md` (Frontend, CheckoutService, CartService + Redis, ProductCatalogService, CurrencyService, và nhóm Mock Services: Payment/Shipping/Email).

3. **[03-implementation.md](03-implementation.md)** — **Truy vết Luồng Thực thi, Security View & Concurrency View:**
   - Truy vết từng bước trong code cho 4 kịch bản: Browse (`homeHandler`), Add-to-Cart (`addToCartHandler`), Checkout Orchestration (`PlaceOrder`), và kịch bản lỗi (`redis-cart` hoặc `productcatalogservice` ngừng hoạt động / trả mã lỗi gRPC).
   - **Security View:** 3 Trust Boundaries, Pod/Container SecurityContext (`runAsNonRoot`, `readOnlyRootFilesystem`, `drop: [ALL]`), giao tiếp gRPC plaintext (`insecure.NewCredentials()`) và đề xuất mTLS/NetworkPolicy.
   - **Concurrency View:** Xử lý đồng thời trên Goroutines / .NET ThreadPool / Python ThreadPoolExecutor và vấn đề Lost Update trong `RedisCartStore.AddItemAsync` (Read-Modify-Write không có lock).

4. **[04-verification-and-tradeoffs.md](04-verification-and-tradeoffs.md)** — **Kiểm chứng, Quyết định Kiến trúc (ADRs) & 10 Câu hỏi Vấn đáp:**
   - Bảng đối chiếu Sơ đồ Upstream vs. Thực tế Code/Manifest.
   - 5 Quyết định kiến trúc & Đánh đổi (Trade-offs): Polyglot gRPC, Synchronous Orchestrator vs. Choreography, Stateless Checkout (không lưu Order DB), Redis Binary Protobuf vs. RDBMS, In-memory Catalog JSON.
   - Bộ 10 câu hỏi và trả lời vấn đáp chuyên sâu kèm trích dẫn `file:line`.
