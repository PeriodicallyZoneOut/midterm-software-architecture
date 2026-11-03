# Evidence — Bookinfo

Thư mục lưu trữ các bằng chứng thực nghiệm khi chạy hệ thống Bookinfo trên môi trường cá nhân của Tường (Kubernetes, Istio, Prometheus, Grafana).

## Danh mục bằng chứng cần thu thập

1. **Khởi động và Trạng thái Pods**:
   - `kubectl get pods -o wide` xác nhận 4 microservices (6 Deployments) và Envoy sidecars đạt trạng thái `2/2 Running`.
   - `kubectl get svc` hiển thị danh sách ClusterIP services (`productpage`, `details`, `reviews`, `ratings`).
2. **Kiểm chứng Canary Routing**:
   - Ảnh chụp màn hình trình duyệt với user ẩn danh: chỉ hiển thị reviews v1 (không sao).
   - Ảnh chụp màn hình đăng nhập user `jason`: hiển thị reviews v2 (sao đen).
   - Log từ Envoy proxy ghi nhận header routing `end-user: jason`.
3. **Kiểm chứng Fault Injection**:
   - Ảnh chụp màn hình lỗi timeout/delay 7s khi user `jason` tải trang.
   - Trạng thái HTTP status code 500 hoặc degradation message trên UI.
4. **Kiểm chứng Self-Healing & Scaling**:
   - Log xóa Pod và quá trình ReplicaSet tự động khởi tạo lại Pod mới.
5. **Observability**:
   - Ảnh chụp dashboard Grafana (Istio Service Dashboard, Istio Workload Dashboard).
   - Kết quả truy vấn PromQL trên giao diện Prometheus tại cổng 9090.

