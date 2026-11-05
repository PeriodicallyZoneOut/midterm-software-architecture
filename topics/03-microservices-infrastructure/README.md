# Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana

> **Hướng dẫn Setup toàn bộ Project**: Đọc ngay [HUONG-DAN-SETUP.md](HUONG-DAN-SETUP.md) (Hướng dẫn cài đặt từ A đến Z, 1-Click setup và reset).  
> **Script triển khai tự động**: Chạy `.\setup-and-run.ps1` trong PowerShell.  
> **Lệnh chạy nhanh 1 trang**: Xem [CHEAT-SHEET-CMD.md](CHEAT-SHEET-CMD.md).  
> **Kịch bản Live Demo 10 Phút**: Xem [KICH-BAN-DEMO-TOAN-BO-CONG-NGHE.md](KICH-BAN-DEMO-TOAN-BO-CONG-NGHE.md) (Kịch bản thực chiến liên hoàn 6 công nghệ).  
> **Cẩm nang toàn diện**: Đọc [HUONG-DAN-TOAN-TAP.md](HUONG-DAN-TOAN-TAP.md) (Tổng hợp 100% slide, kịch bản thuyết trình, mapping code, lệnh run demo và câu hỏi vấn đáp cho Tường).  

## Kiến thức và slide

- Microservice boundaries, contracts, ownership; so sánh Monolith vs Modular Monolith vs Microservices.
- Kiến trúc Polyglot Microservices: Python (Flask), Ruby (WEBrick), Java (Open Liberty), Node.js (Express).
- Docker image/container, multi-stage build; Kubernetes Pod, Deployment, Service, labels, scaling và self-healing.
- Istio Service Mesh: Control plane (`istiod`) vs Data plane (Envoy Sidecar proxy), Ingress Gateway, VirtualService, DestinationRule, Canary routing, Fault injection và Transparent mTLS.
- Cloud-Native Observability: Metrics vs Logs vs Traces; 4 Golden Signals; Prometheus scrape/PromQL → Grafana dashboards.
- Phân tích đánh đổi kiến trúc (Architectural Trade-offs): Latency, Resource footprint, Operational complexity.

[Slide Thuyết Trình 10 Phút Chuẩn (13 slide PDF)](slides/exports/Cloud-Native%20Microservices%20Architecture%20Presentation.pdf) · [Kịch bản thuyết trình slide 10 phút](slides/KICH-BAN-THUYET-TRINH-10-PHUT.md) · [Kịch bản Live Demo 10 phút](KICH-BAN-DEMO-TOAN-BO-CONG-NGHE.md) · [Bộ 7 Slide Độc Lập](slides/README.md)

## Projects

- [Bookinfo](projects/bookinfo/README.md) (**Dự án chính của Tường**): Ứng dụng microservices đa ngôn ngữ chuẩn Istio (productpage, details, reviews v1/v2/v3, ratings); minh chứng trực quan cho Canary routing, Fault injection, Kubernetes self-healing và Envoy telemetry.
- [Istio](projects/istio/README.md): Hạ tầng Service Mesh, Ingress Gateway, Traffic management CRDs, và các addons giám sát Prometheus & Grafana.
- [Online Boutique](projects/online-boutique/README.md): Dự án tham chiếu bổ sung về kiến trúc gRPC microservices và Redis cache.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code thực tế.
- Demo có runbook, expected/actual result và evidence đã lọc sạch dữ liệu nhạy cảm.
- Giải thích được luồng routing L7, tự phục hồi của Pod, câu lệnh PromQL và bảng đánh đổi kiến trúc.
