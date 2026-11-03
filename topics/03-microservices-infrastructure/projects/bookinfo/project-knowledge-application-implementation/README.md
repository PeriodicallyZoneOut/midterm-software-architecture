# Áp dụng kiến thức vào project — Bookinfo

Tài liệu này hệ thống hóa toàn bộ kiến thức chuyên sâu về Microservices, Docker, Kubernetes, Istio Service Mesh, Prometheus và Grafana được áp dụng trực tiếp vào dự án Bookinfo.

## Cấu trúc tài liệu

1. [01-concepts.md](01-concepts.md): Khái niệm cốt lõi, vấn đề giải quyết, kiến trúc Polyglot, Service Mesh, và Observability.
2. [02-component-mapping.md](02-component-mapping.md): Bảng ánh xạ toàn diện từ Microservice -> Source code -> Port -> Kubernetes resource -> Envoy Proxy.
3. [03-implementation.md](03-implementation.md): Phân tích code chi tiết, Dockerfile đa tầng, Kubernetes manifests, và Istio Traffic Management CRDs.
4. [04-verification-and-tradeoffs.md](04-verification-and-tradeoffs.md): Kịch bản kiểm chứng thực nghiệm (Canary, Fault Injection, Self-healing) và phân tích các đánh đổi kiến trúc (Architectural Trade-offs).

