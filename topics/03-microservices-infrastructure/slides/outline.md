# Dàn Ý Slide: 10 Slide Trong 10 Phút

> **Chủ đề 3**: Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana, Bookinfo  
> **Người thực hiện**: Tường  
> **Cấu trúc**: **10 SLIDES CHUẨN XÁC**  
> **Thời lượng thuyết trình**: 10 phút (Slide: 6.0 phút + Live Demo: 3.5 phút + Vấn đáp: 0.5 phút)  
> **Hệ thống minh chứng**: [Bookinfo](../projects/bookinfo/README.md) & [Istio + Addons](../projects/istio/README.md)

---

## Danh Mục 10 Slide & Mapping Công Nghệ

| Slide | Tiêu đề Slide | Công nghệ Trọng tâm | Code & Manifest Mapping trong Project |
|---|---|---|---|
| **Slide 1** | Đặt Vấn Đề & Chuyển Dịch Cloud-Native | Tổng quan kiến trúc & 4 bài toán | Cấu trúc Bookinfo trên cụm Kubernetes |
| **Slide 2** | Kiến Trúc Microservices & Polyglot | **Microservices** | So sánh Monolith vs Microservices; 4 ngôn ngữ trong Bookinfo |
| **Slide 3** | Domain Decomposition & Code Mapping | **Microservices & Bookinfo** | Single Responsibility; `productpage.py` & `LibertyRestEndpoint.java` |
| **Slide 4** | Inter-Service Networking & Header Propagation | **Microservices & Tracing** | Code deep-dive hàm `getForwardHeaders` trong `productpage.py` |
| **Slide 5** | Containerization & Multi-Stage Build | **Docker** | Namespaces/Cgroups; Code deep-dive `src/reviews/Dockerfile` |
| **Slide 6** | Workload Modeling & Label Selectors | **Kubernetes** | Pod `2/2 Running` (App + Envoy); `platform/kube/bookinfo.yaml` |
| **Slide 7** | Self-Healing & Zero-Downtime Deployment | **Kubernetes** | Reconciliation Loop; Phục hồi Pod `details` trong 1.8s |
| **Slide 8** | Service Mesh & Canary Routing | **Istio** | Control Plane `istiod` vs Data Plane Envoy; `VirtualService` user `jason` |
| **Slide 9** | Zero Trust Security & Transparent mTLS | **Istio** | Định danh SPIFFE ID; SDS xoay vòng chứng chỉ; `PeerAuthentication` STRICT |
| **Slide 10** | Observability & Architectural Trade-offs | **Prometheus & Grafana** | Pull `:15090`; PromQL đo RPS & P95; Grafana Dashboard; Bảng Trade-offs |
