# Triển khai Chi tiết — Istio & Observability Addons

## 1. Cấu hình Sidecar Injection & Namespace

Để kích hoạt Data Plane cho bất kỳ namespace nào (ví dụ: `default`), Kubernetes dùng cơ chế **Mutating Admission Webhook**:
```bash
# Gán nhãn để istiod tự động inject Envoy proxy container vào mọi Pod mới tạo
kubectl label namespace default istio-injection=enabled --overwrite
```
- Khi manifest Pod được gửi đến Kubernetes API Server, Webhook của Istio sẽ tự động chèn thêm container `istio-proxy` và container khởi tạo `istio-init` (để thiết lập rule `iptables` chuyển hướng traffic sang port 15001/15006 của Envoy).

---

## 2. Triển khai Cấu hình Định tuyến & Canary (VirtualService)

Mẫu cấu hình chia tải 90% vào bản v1 ổn định và 10% vào bản thử nghiệm v2:
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: frontend-routing
  namespace: default
spec:
  hosts:
  - "frontend"
  http:
  - route:
    - destination:
        host: frontend
        subset: v1
      weight: 90
    - destination:
        host: frontend
        subset: v2
      weight: 10
    timeout: 3s
    retries:
      attempts: 3
      perTryTimeout: 1s
```
- Cấu hình này giải quyết đồng thời:
  1. Thử nghiệm phiên bản mới rủi ro tối thiểu (Canary).
  2. Tăng độ bền (Resilience) qua cơ chế tự động thử lại (Retry) 3 lần, mỗi lần tối đa 1 giây.

---

## 3. Cấu hình Bảo mật Zero Trust (mTLS STRICT)

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```
- Khi áp dụng manifest này, mọi request gửi đến bất kỳ Pod nào trong namespace `default` mà không có chứng chỉ mTLS hợp lệ từ Envoy sidecar sẽ bị từ chối ngay lập tức với mã lỗi HTTP 503 hoặc connection reset.

---

## 4. Cấu hình Thu thập & Trực quan hóa (Prometheus / Grafana)

Cấu hình mẫu Prometheus scrape target cho Envoy:
```yaml
# Trích từ samples/addons/prometheus.yaml
- job_name: 'envoy-stats'
  metrics_path: '/stats/prometheus'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_container_port_name]
    action: keep
    regex: '.*-envoy-prom'
```
- Prometheus tự động quét tất cả các Pod có cổng Envoy Prometheus (`15090`) và ghi nhận vào cơ sở dữ liệu chuỗi thời gian (TSDB).
