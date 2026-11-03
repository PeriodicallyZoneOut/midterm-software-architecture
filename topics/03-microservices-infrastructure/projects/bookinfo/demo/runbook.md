# Runbook Demo: Bookinfo + Istio + Observability (Prometheus & Grafana)

> **Mục tiêu**: Kịch bản chạy thực tế cho bài thi giữa kỳ của Tường (Thời lượng: 5–7 phút).  
> **Yêu cầu trước khi chạy**: Đã bật Kubernetes trên Docker Desktop hoặc Minikube/k3d.

---

## Phần 1: Khởi động Môi trường & Triển khai Hệ thống

### 1. Cài đặt Istio & Kích hoạt Sidecar Injection
```bash
# 1. Cài đặt Istio (profile demo bao gồm Ingress Gateway và cấu hình chi tiết)
istioctl install --set profile=demo -y

# 2. Gán nhãn tự động inject Envoy sidecar cho default namespace
kubectl label namespace default istio-injection=enabled --overwrite

# 3. Triển khai Prometheus và Grafana từ thư mục addons của Istio
kubectl apply -f ../../istio/source/samples/addons/prometheus.yaml
kubectl apply -f ../../istio/source/samples/addons/grafana.yaml
```

### 2. Triển khai Bookinfo Application
```bash
# Di chuyển vào thư mục source của Bookinfo
cd ../source

# Triển khai toàn bộ Services và Deployments của Bookinfo
kubectl apply -f platform/kube/bookinfo.yaml

# Triển khai Ingress Gateway và VirtualService mở cổng vào productpage
kubectl apply -f networking/bookinfo-gateway.yaml

# Khởi tạo DestinationRule cho tất cả services (định nghĩa subsets v1, v2, v3)
kubectl apply -f networking/destination-rule-all.yaml

# Kiểm tra trạng thái Pods (Chờ toàn bộ Pods đạt 2/2 Running - 1 app container + 1 Envoy sidecar)
kubectl get pods -w
```

---

## Phần 2: Kịch bản Trình diễn Vấn đáp Giữa kỳ (Live Demo)

### 🔴 DEMO 1: Mở Web Bookinfo & Xác nhận Kiến trúc Polyglot (1 phút)
1. Mở port-forward cổng Frontend `productpage`:
   ```bash
   kubectl port-forward svc/productpage 9080:9080
   ```
2. Mở trình duyệt web: `http://localhost:9080/productpage`
3. **Thuyết minh**:
   - Giao diện Bookinfo hiển thị thông tin cuốn sách "The Comedy of Errors".
   - Cột bên trái: Dữ liệu sách do **`details`** (viết bằng **Ruby**) phục vụ.
   - Cột bên phải: Đánh giá do **`reviews`** (viết bằng **Java**) phục vụ.
   - Nhấn `F5` tải lại trang vài lần: Có lúc không thấy sao (v1), có lúc thấy sao đen (v2 - gọi sang **`ratings`** viết bằng **Node.js**), có lúc thấy sao đỏ (v3). Điều này chứng minh Kubernetes Service mặc định cân bằng tải Round-Robin giữa 3 Deployments `reviews-v1`, `reviews-v2`, `reviews-v3`.

---

### 🔴 DEMO 2: Điều phối Lưu lượng (Traffic Management) & Canary Routing (2 phút)

#### Bước 2.1: Khóa 100% traffic về Reviews v1 (Baseline ổn định)
```bash
kubectl apply -f networking/virtual-service-all-v1.yaml
```
- F5 trang web nhiều lần: 100% các lần load chỉ thấy v1 (không có sao đánh giá).

#### Bước 2.2: Canary Routing theo HTTP Header người dùng (A/B Testing)
- Áp dụng routing thông minh: Chỉ user `jason` mới thấy phiên bản thử nghiệm `reviews:v2` (sao đen), các user khác vẫn ở `reviews:v1`:
  ```bash
  kubectl apply -f networking/virtual-service-reviews-test-v2.yaml
  ```
- **Thực nghiệm**:
  1. Trình duyệt chưa đăng nhập -> F5: Luôn thấy **v1** (không sao).
  2. Bấm nút **Sign in** ở góc trên bên phải trang web, nhập username: `jason` (mật khẩu tùy ý, để trống cũng được) -> Bấm **Sign in**.
  3. Quan sát giao diện: Xuất hiện ngay lập tức **sao đen** của `reviews:v2`!
  4. Đăng xuất (Sign out) -> Trở lại **v1** (không sao).
- **Thuyết minh**: Envoy proxy bắt HTTP header `end-user: jason` do `productpage` chuyển tiếp và định tuyến sang Pod subset `v2` mà code Java không cần sửa một dòng nào!

#### Bước 2.3: Phân chia tải theo tỉ lệ trọng số (Weighted Traffic Shifting - 80/20 hoặc 50/50)
```bash
kubectl apply -f networking/virtual-service-reviews-50-v3.yaml
```
- F5 liên tục: Đúng 50% request ra không sao (v1) và 50% ra sao đỏ (v3). Đây là kỹ thuật triển khai Canary phát hành phiên bản mới an toàn trong thực tế.

---

### 🔴 DEMO 3: Giả lập Sự cố (Fault Injection) & Kiểm thử Độ bền bỉ (1.5 phút)

#### Chèn độ trễ 7 giây (HTTP Delay) vào service `ratings`:
```bash
kubectl apply -f networking/virtual-service-ratings-test-delay.yaml
```
1. Đăng nhập với tài khoản `jason`.
2. F5 trang web: Trang web mất đúng khoảng 3–7 giây để tải xong, và phần reviews hiển thị thông báo lỗi: *"Sorry, product reviews are currently unavailable for this book"*.
3. **Thuyết minh**: Vì `reviews` có cấu hình timeout nội bộ, khi downstream `ratings` bị trễ 7s thì timeout kích hoạt giúp ngăn chặn tình trạng thắt cổ chai dây chuyền (Cascading Failure), bảo vệ toàn bộ hệ thống.

---

### 🔴 DEMO 4: Tự Phục Hồi (Self-Healing) & Zero-Downtime trong Kubernetes (1 phút)
1. Theo dõi trạng thái Pod của `details`:
   ```bash
   kubectl get pods -l app=details -w
   ```
2. Trên terminal khác, xóa cưỡng bức Pod `details`:
   ```bash
   kubectl delete pod -l app=details
   ```
3. **Hiện tượng quan sát**:
   - Pod cũ bị xóa, ReplicaSet của Kubernetes lập tức khởi tạo Pod mới thay thế trong 2–3 giây.
   - Trình duyệt F5 trang web vẫn phản hồi bình thường, không xảy ra downtime.

---

### 🔴 DEMO 5: Giám sát Hệ thống với Prometheus & Grafana (1.5 phút)
1. Mở port-forward cho Grafana và Prometheus:
   ```bash
   kubectl port-forward svc/grafana -n istio-system 3000:3000
   kubectl port-forward svc/prometheus -n istio-system 9090:9090
   ```
2. Mở trình duyệt tại `http://localhost:3000`:
   - Truy cập **Dashboards** -> chọn **Istio Service Dashboard** -> chọn Service `productpage.default.svc.cluster.local`.
3. Bơm tải liên tục bằng vòng lặp curl:
   ```powershell
   for ($i=1; $i -le 100; $i++) { curl.exe -s http://localhost:9080/productpage > $null }
   ```
4. **Chỉ số trên màn hình**:
   - **RPS (Request Volume)** tăng vọt phản ánh lưu lượng truy cập.
   - **P95 / P99 Latency**: Đo lường chính xác độ trễ qua Envoy sidecar.
   - Mở Prometheus tại `http://localhost:9090` và chạy PromQL:
     ```promql
     sum(rate(istio_requests_total{destination_workload="productpage-v1"}[1m])) by (response_code)
     ```

---

## Dọn dẹp Tài nguyên sau Demo
```bash
# Xóa VirtualServices và DestinationRules đã áp dụng
kubectl delete -f networking/virtual-service-all-v1.yaml
kubectl delete -f networking/destination-rule-all.yaml
kubectl delete -f networking/bookinfo-gateway.yaml

# Xóa toàn bộ Bookinfo
kubectl delete -f platform/kube/bookinfo.yaml
```

