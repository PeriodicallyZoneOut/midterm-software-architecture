# Online Boutique — Architecture Representation

Trọng tâm: Tái dựng kiến trúc từ mã nguồn đa ngôn ngữ (Go, C#/.NET, Node.js, Python, Java) và cấu hình Kubernetes runtime; biểu diễn đầy đủ **4+1 View Model**, **C4 Model (Level 1–4)**, **Data Schema/Model (Redis Cart, Product Catalog JSON, Protobuf Contracts)**, **Security/Concurrency View** và **Component Mapping** có đối chiếu trực tiếp tới code.

## Nội dung

- [Áp dụng kiến thức vào project](project-knowledge-application-implementation/README.md)
  - [01-concepts.md](project-knowledge-application-implementation/01-concepts.md): Stakeholder Matrix, 4+1 View Model, C4 Level 1–4, Data Schema/Model (Redis, JSON, Protobuf).
  - [02-component-mapping.md](project-knowledge-application-implementation/02-component-mapping.md): Bảng ánh xạ tổng thể 11 microservices + Redis và 6 Component Cards chi tiết (10 trường theo `INVENTORY.md`).
  - [03-implementation.md](project-knowledge-application-implementation/03-implementation.md): Truy vết luồng gRPC (Browse, Cart, Checkout `PlaceOrder()`), Security View, Concurrency View và Error Handling.
  - [04-verification-and-tradeoffs.md](project-knowledge-application-implementation/04-verification-and-tradeoffs.md): Ma trận kiểm chứng, 5 quyết định kiến trúc (ADR/Trade-offs) và 10 câu hỏi vấn đáp có trích dẫn `file:line`.
- [Source đã copy](source/) · [Nguồn và phiên bản](SOURCE-NOTES.md)
- [Runbook](demo/runbook.md)
- [Evidence](evidence/README.md)
- [Bộ Slide riêng cho Online Boutique](slides/outline.md) · [Speaker Notes](slides/speaker-notes.md) · [Exports](slides/exports/)
