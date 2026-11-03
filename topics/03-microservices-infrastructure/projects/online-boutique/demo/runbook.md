# Runbook Demo: Online Boutique + Istio + Observability

> **Mục tiêu**: Kịch bản chạy thực tế cho bài thi giữa kỳ của Tường (Thời lượng: 4–5 phút).  
> **Yêu cầu trước khi chạy**: Đã có cluster Kubernetes (Minikube / k3d / Docker Desktop K8s) đang chạy.

---

## Chuẩn bị môi trường & Lệnh khởi động

### 1. Triển khai Istio & Service Mesh Ingress
```bash
# 1. Cài đặt Istio profile demo hoặc default
istioctl install --set profile=demo -y

# 2. Gán nhãn tự động inject Envoy sidecar cho default namespace
kubectl label namespace default istio-injection=enabled --overwrite

# 3. Triển khai các addon giám sát (Prometheus, Grafana)
kubectl apply -f ../../istio/source/samples/addons/prometheus.yaml
kubectl apply -f ../../istio/source/samples/addons/grafana.yaml
```

### 2. Triển khai Online Boutique
```bash
# Di chuyển vào source Online Boutique
cd ../source

# Triển khai toàn bộ workload
kubectl apply -f release/kubernetes-manifests.yaml

# Kiểm tra trạng thái Pods (Chờ các Pod đạt 2/2 Running - 1 app container + 1 envoy proxy)
kubectl get pods -w
```

---

## Kịch bản Demo Live (4 Phút Vấn Đáp)

### Kịch bản 1: Mở ứng dụng & Thực hiện giao dịch mua hàng (1 phút)
1. Mở Port-forward cổng Frontend ra máy tính:
   ```bash
   kubectl port-forward svc/frontend 8080:80
   ```
2. Mở trình duyệt web tại `http://localhost:8080`.
3. Nhấp chọn 1 sản phẩm -> Chọn số lượng 2 -> Bấm **Add To Cart**.
4. Bấm **Place Order** -> Trang hiển thị **Your order is complete!** kèm Order ID và mã vận đơn.
5. *Giải thích cho Thầy/Cô*: Luồng vừa rồi đã đi qua `frontend` -> `checkoutservice` -> gọi 6 microservice downstream qua gRPC và kết thúc bằng việc xóa giỏ hàng trong Redis.

### Kịch bản 2: Kiểm chứng Pod Self-healing & Zero-downtime (1 phút)
1. Mở một cửa sổ Terminal theo dõi Pods:
   ```bash
   kubectl get pods -l app=cartservice -w
   ```
2. Trên cửa sổ Terminal thứ hai, cố tình kill Pod `cartservice`:
   ```bash
   kubectl delete pod -l app=cartservice
   ```
3. *Hiện tượng quan sát được*:
   - Pod cũ chuyển sang `Terminating`.
   - Ngay lập tức ReplicaSet sinh ra một Pod mới `Pending` -> `ContainerCreating` -> `Running (2/2)`.
   - Trong lúc đó, quay lại trình duyệt refresh trang Giỏ hàng: Web vẫn hoạt động bình thường, không hề bị lỗi kết nối.

### Kịch bản 3: Giám sát Hệ thống với Prometheus & Grafana (2 phút)
1. Mở Port-forward cho Prometheus và Grafana:
   ```bash
   kubectl port-forward svc/prometheus -n istio-system 9090:9090
   kubectl port-forward svc/grafana -n istio-system 3000:3000
   ```
2. Mở giao diện Grafana tại `http://localhost:3000`:
   - Vào menu Dashboards -> Chọn **Istio Service Dashboard**.
   - Chọn service: `frontend.default.svc.cluster.local`.
3. Kích hoạt sinh tải để tạo biến thiên dữ liệu:
   ```bash
   # Scale loadgenerator lên để bơm traffic vào hệ thống
   kubectl scale deployment/loadgenerator --replicas=2
   ```
4. *Chỉ cho Thầy/Cô thấy trên màn hình Grafana*:
   - Panel **Incoming Requests**: Đồ thị RPS dựng đứng từ 0 lên ~30-50 req/s.
   - Panel **Client Request Duration (p95, p99)**: Cho thấy độ trễ xử lý của Envoy sidecar phản ánh chân thực các giao dịch gRPC nội bộ.
