# DANH SÁCH LỆNH CHẠY DEMO — TOPIC 03 (TƯỜNG)
# Microservices, Kubernetes, Istio, Prometheus, Grafana
# Primary Project: Bookinfo (Polyglot Microservices Sample)

---

## BƯỚC 0: ĐIỀU KIỆN TIÊN QUYẾT (CHỈ LÀM 1 LẦN TRÊN WINDOWS)
1. Mở ứng dụng **Docker Desktop**.
2. Nhấn vào biểu tượng **Settings (bánh răng)** ở góc trên bên phải.
3. Chọn tab **Kubernetes** ở menu bên trái.
4. Tích chọn ô: `[v] Enable Kubernetes`.
5. Nhấn **Apply & restart** và chờ khoảng 2-3 phút cho đến khi góc dưới bên trái Docker Desktop hiện icon màu xanh lá cây: `Kubernetes running`.

---

## BƯỚC 1: CÀI ĐẶT ISTIO CLI (NẾU MÁY CHƯA CÓ)
Mở một cửa sổ PowerShell (Admin hoặc thường), chạy:
```powershell
winget install istio.istioctl
```
*(Sau đó tắt terminal và mở lại terminal mới để nhận lệnh `istioctl`).*

---

## BƯỚC 2: CHẠY SETUP TỰ ĐỘNG TOÀN BỘ HỆ THỐNG
Script PowerShell tự động cấu hình Istio sidecar injection, deploy toàn bộ Bookinfo (4 microservices, 6 deployments) và Prometheus + Grafana:

Chạy lệnh sau tại thư mục gốc của project:
```powershell
# Di chuyển vào thư mục Topic 03
cd d:\VScode\midterm-software-architecture\topics\03-microservices-infrastructure

# 1. Khởi tạo Istio trên cụm K8s (Profile demo)
istioctl install --set profile=demo -y

# 2. Chạy script setup tự động
.\setup-and-run.ps1
```

Kiểm tra trạng thái các Pods (Chờ các Pod đạt `2/2 Running` - nghĩa là 1 App + 1 Envoy Sidecar):
```powershell
kubectl get pods -w
```

---

## BƯỚC 3: CÁC LỆNH CHẠY LIVE DEMO (VẤN ĐÁP GIỮA KỲ — 5-7 PHÚT)

### 🔴 DEMO 1: Mở Web Bookinfo & Khám Phá Kiến Trúc Polyglot (1 phút)
Mở **Terminal 1**:
```powershell
kubectl port-forward svc/productpage 9080:9080
```
- Truy cập trình duyệt: `http://localhost:9080/productpage`
- Nhấn `F5` tải lại trang 3-4 lần:
  - Cột trái: Thông tin sách do **`details`** (viết bằng **Ruby**) phục vụ.
  - Cột phải: Đánh giá do **`reviews`** (viết bằng **Java**) phục vụ.
  - Lúc thì không sao (`reviews-v1`), lúc sao đen (`reviews-v2` gọi sang **`ratings`** viết bằng **Node.js**), lúc sao đỏ (`reviews-v3`).
- *Giải thích cho Thầy/Cô*: Đây là tính chất **Polyglot Microservices** (4 ngôn ngữ khác nhau: Python, Ruby, Java, Node.js). Mặc định Kubernetes Service phân phối tải ngẫu nhiên Round-Robin giữa 3 Deployments của reviews.

---

### 🔴 DEMO 2: Điều Phối Traffic Thông Minh (Canary Routing) với Istio (2 phút)

#### 2.1. Khóa 100% traffic về Reviews v1 (Không sao):
Mở **Terminal 2**:
```powershell
kubectl apply -f projects/bookinfo/source/networking/virtual-service-all-v1.yaml
```
- Quay lại trình duyệt F5 nhiều lần: 100% request chỉ thấy v1 (không có sao).

#### 2.2. Canary Routing theo HTTP Header (User `jason` thấy sao đen v2):
```powershell
kubectl apply -f projects/bookinfo/source/networking/virtual-service-reviews-test-v2.yaml
```
- **Thực nghiệm ngay trên web**:
  1. Chưa đăng nhập -> F5: Vẫn là **v1** (không sao).
  2. Bấm **Sign in** góc trên bên phải, nhập username: `jason` (password để trống) -> Bấm **Sign in**.
  3. F5 trang web: Xuất hiện ngay lập tức **sao đen** của `reviews:v2`!
  4. Bấm **Sign out** -> Lập tức quay về **v1** (không sao).
- *Giải thích cho Thầy/Cô*: `productpage` chuyển tiếp header `end-user: jason`. Envoy Sidecar chặn ở tầng L7, khớp luật trong Istio `VirtualService` và route vào Pod subset `v2` của reviews mà không cần sửa 1 dòng code nào!

#### 2.3. Phân chia tải theo trọng số (Traffic Shifting: 50% v1 và 50% v3 sao đỏ):
```powershell
kubectl apply -f projects/bookinfo/source/networking/virtual-service-reviews-50-v3.yaml
```
- F5 liên tục: Đúng 50% request ra không sao (v1) và 50% ra sao đỏ (v3). Minh chứng phát hành canary an toàn trước khi thay thế hoàn toàn phiên bản cũ.

---

### 🔴 DEMO 3: Giả Lập Sự Cố (Fault Injection & Graceful Degradation) (1.5 phút)
Chèn độ trễ 7 giây (HTTP Delay) vào service `ratings` đối với user `jason`:
```powershell
kubectl apply -f projects/bookinfo/source/networking/virtual-service-ratings-test-delay.yaml
```
- Trên trình duyệt, đăng nhập với user `jason` -> F5 trang web:
  - Trang web mất vài giây để tải.
  - Cột `details` vẫn hiển thị bình thường.
  - Cột `reviews` hiển thị thông báo lỗi nhẹ nhàng: *"Ratings service is currently unavailable"*.
- *Giải thích cho Thầy/Cô*: Thử nghiệm tính bền bỉ (Chaos Engineering). Khi `ratings` bị chậm, timeout kích hoạt giúp `productpage` không bị sập theo (ngăn ngừa Cascading Failure).

---

### 🔴 DEMO 4: Kubernetes Pod Self-Healing & Zero Downtime (1 phút)
Mở **Terminal 3**:
```powershell
# 1. Cố tình xóa (kill) Pod details
kubectl delete pod -l app=details

# 2. Xem Kubernetes lập tức tạo Pod mới thay thế trong 2 giây
kubectl get pods -l app=details -w
```
- Quay lại trình duyệt F5 trang web: Web vẫn phục vụ mượt mà, không hề có lỗi gián đoạn vì Kubernetes Service tự động định tuyến traffic sang Pod sẵn sàng.

---

### 🔴 DEMO 5: Giám Sát Mesh Trên Grafana & Truy Vấn Prometheus (1.5 phút)
Mở **Terminal 4**:
```powershell
# Port forward Grafana
kubectl port-forward svc/grafana -n istio-system 3000:3000
```
Mở **Terminal 5**:
```powershell
# Port forward Prometheus
kubectl port-forward svc/prometheus -n istio-system 9090:9090
```
- Mở trình duyệt: `http://localhost:3000` (Grafana)
  - Vào **Dashboards** -> chọn **Istio Service Dashboard** -> chọn Service `productpage.default.svc.cluster.local`.
- Bơm 100 request liên tục tạo biến thiên:
  ```powershell
  1..100 | ForEach-Object { curl.exe -s http://localhost:9080/productpage > $null }
  ```
- *Hiện tượng quan sát*:
  - Panel **Request Volume (RPS)** dựng đứng phản ánh lưu lượng tức thời.
  - Panel **P95 / P99 Latency** đo đạc chính xác thời gian phản hồi qua Envoy proxy.
- Mở `http://localhost:9090/graph` (Prometheus) và gõ câu lệnh PromQL:
  ```promql
  sum(rate(istio_requests_total{destination_workload="productpage-v1"}[1m])) by (response_code)
  ```
  Nhấn **Execute** -> Chọn tab **Graph** xem biểu đồ request thành công mã 200.

---

## BƯỚC 4: DỌN DẸP SAU BUỔI VẤN ĐÁP
```powershell
kubectl delete -f projects/bookinfo/source/networking/virtual-service-all-v1.yaml
kubectl delete -f projects/bookinfo/source/networking/destination-rule-all.yaml
kubectl delete -f projects/bookinfo/source/networking/bookinfo-gateway.yaml
kubectl delete -f projects/bookinfo/source/platform/kube/bookinfo.yaml
```
