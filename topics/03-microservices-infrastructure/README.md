# Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana

## Kiến thức và slide

- Microservice boundaries, contracts, ownership; so sánh monolith/modular monolith.
- Docker image/container/network/volume và Kubernetes Pod/Deployment/Service/probes/scaling.
- Istio control/data plane, mode triển khai, ingress, traffic policy và mTLS.
- Metrics/logs/traces; Prometheus scrape/PromQL → Grafana datasource/panels.
- End-to-end checkout, scale/failure/recovery và số liệu thực nghiệm.

[Slide outline](slides/outline.md) · [Speaker notes](slides/speaker-notes.md)

## Projects

- [Online Boutique](projects/online-boutique/README.md): gRPC services, Redis, checkout orchestrator; workload và Kubernetes mapping.
- [Istio](projects/istio/README.md): Control/data plane, gateway/routing/mTLS; addons Prometheus/Grafana và metric pipeline.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code.
- Demo có runbook, expected/actual result và evidence; giới hạn được ghi rõ.
