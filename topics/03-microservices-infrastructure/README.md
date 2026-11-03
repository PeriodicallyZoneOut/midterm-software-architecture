# Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana

> **Cẩm nang toàn diện**: Đọc ngay [HUONG-DAN-TOAN-TAP.md](HUONG-DAN-TOAN-TAP.md) (Tổng hợp 100% slide, kịch bản thuyết trình, mapping code, lệnh run demo và câu hỏi vấn đáp cho Tường).  
> **Lệnh chạy nhanh 1 trang**: Xem [CHEAT-SHEET-CMD.md](CHEAT-SHEET-CMD.md).  
> **Script triển khai tự động**: Chạy `.\setup-and-run.ps1` trong PowerShell.

## Kiến thức và slide

- Microservice boundaries, contracts, ownership; so sánh Monolith vs Modular Monolith vs Microservices.
- Kiến trúc Polyglot Microservices: Python (Flask), Ruby (WEBrick), Java (Open Liberty), Node.js (Express).
- Docker image/container, multi-stage build; Kubernetes Pod, Deployment, Service, labels, scaling và self-healing.
- Istio Service Mesh: Control plane (`istiod`) vs Data plane (Envoy Sidecar proxy), Ingress Gateway, VirtualService, DestinationRule, Canary routing, Fault injection và Transparent mTLS.
- Cloud-Native Observability: Metrics vs Logs vs Traces; 4 Golden Signals; Prometheus scrape/PromQL → Grafana dashboards.
- Phân tích đánh đổi kiến trúc (Architectural Trade-offs): Latency, Resource footprint, Operational complexity.

[Bộ 7 Slide Độc Quyền Từng Chủ Đề (10 trang / 10 phút)](slides/README.md) · [Slide trình chiếu tổng hợp](slides/slides.md) · [Slide English](slides/slides-en.md) · [Speaker notes](slides/speaker-notes.md)

## Projects

- [Bookinfo](projects/bookinfo/README.md) (**Dự án chính của Tường**): Ứng dụng microservices đa ngôn ngữ chuẩn Istio (productpage, details, reviews v1/v2/v3, ratings); minh chứng trực quan cho Canary routing, Fault injection, Kubernetes self-healing và Envoy telemetry.
- [Istio](projects/istio/README.md): Hạ tầng Service Mesh, Ingress Gateway, Traffic management CRDs, và các addons giám sát Prometheus & Grafana.
- [Online Boutique](projects/online-boutique/README.md): Dự án tham chiếu bổ sung về kiến trúc gRPC microservices và Redis cache.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code thực tế.
- Demo có runbook, expected/actual result và evidence đã lọc sạch dữ liệu nhạy cảm.
- Giải thích được luồng routing L7, tự phục hồi của Pod, câu lệnh PromQL và bảng đánh đổi kiến trúc.
