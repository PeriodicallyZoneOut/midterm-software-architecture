# Mapping Thành phần — Istio & Observability Pipeline

## Bảng ánh xạ Kiến trúc Khái niệm -> Resource Kubernetes / Istio CRD -> File Cấu hình

| Thành phần Khái niệm | Loại Resource (Kind) | Trách nhiệm & Phạm vi tác động | File Cấu hình / Manifest minh chứng |
|---|---|---|---|
| **Control Plane** | `Deployment: istiod` | Quản lý cấu hình xDS, phân phối route, cấp chứng chỉ CA | [`source/manifests/`](../source/manifests/) |
| **Data Plane Sidecar** | `Container: istio-proxy` | Chạy bên trong Pod, đón/chặn traffic L4/L7, thu thập metrics | Tự động inject qua namespace label `istio-injection=enabled` |
| **Ingress Gateway** | `Gateway` & `Deployment: istio-ingressgateway` | Cổng vào tiếp nhận lưu lượng HTTP/HTTPS từ ngoài Internet vào mesh | [`source/samples/bookinfo/networking/bookinfo-gateway.yaml`](../source/samples/bookinfo/networking/bookinfo-gateway.yaml) |
| **L7 Routing Rule** | `VirtualService` | Định tuyến dựa trên host, URI, chia phần trăm tải (Canary), timeout, retry | [`source/samples/bookinfo/networking/virtual-service-all-v1.yaml`](../source/samples/bookinfo/networking/virtual-service-all-v1.yaml) |
| **Traffic Policy & Subset** | `DestinationRule` | Định nghĩa version subsets (v1, v2), load balancing algorithm, circuit breaker | [`source/samples/bookinfo/networking/destination-rule-all.yaml`](../source/samples/bookinfo/networking/destination-rule-all.yaml) |
| **Zero Trust mTLS** | `PeerAuthentication` | Cấu hình chế độ mã hóa bắt buộc (STRICT) hoặc nới lỏng (PERMISSIVE) | Manifest CRD `security.istio.io/v1beta1` |
| **L7 Authorization** | `AuthorizationPolicy` | Phân quyền truy cập theo method, path, danh tính nguồn (Source SPIFFE ID) | Manifest CRD `security.istio.io/v1beta1` |
| **Metrics Collector** | `Deployment: prometheus` | Định kỳ cào số liệu (Scrape) từ cổng `:15090` của từng Envoy proxy | [`source/samples/addons/prometheus.yaml`](../source/samples/addons/prometheus.yaml) |
| **Metrics Visualizer** | `Deployment: grafana` | Kết nối Prometheus datasource, hiển thị dashboard đo lường SLA/Golden Signals | [`source/samples/addons/grafana.yaml`](../source/samples/addons/grafana.yaml) |

---

## Luồng Dữ liệu Đo lường (Telemetry Metric Pipeline)

```text
[ Microservice App ] ──(Localhost)──> [ Envoy Proxy Sidecar ]
                                             │
                                     (Port 15090 /stats/prometheus)
                                             │
                                             ▼ (Mỗi 15s Scrape HTTP)
                                    [ Prometheus TSDB ]
                                             │
                                             ▼ (PromQL HTTP Query API)
                                    [ Grafana Dashboard ]
```
