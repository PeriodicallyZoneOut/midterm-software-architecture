# HƯỚNG DẪN SETUP & TRIỂN KHAI TOÀN BỘ PROJECT (TOPIC 03)
## BOOKINFO, KUBERNETES, ISTIO SERVICE MESH, PROMETHEUS & GRAFANA

- **Sinh viên thực hiện**: **Huỳnh Mạnh Tường** (MSSV: **23120105**)
- **Thư mục làm việc**: `d:\VScode\midterm-software-architecture\topics\03-microservices-infrastructure`

---

## 📋 TỔNG QUAN CÁC FILE LIÊN QUAN ĐẾN SETUP

| Tên File | Vai trò |
|---|---|
| 📄 [**`setup-and-run.ps1`**](setup-and-run.ps1) | **Script PowerShell tự động hóa 1-Click** (tự gán nhãn namespace, apply manifests Bookinfo, Gateway, DestinationRules, Prometheus, Grafana). |
| 📄 [**`CHEAT-SHEET-CMD.md`**](CHEAT-SHEET-CMD.md) | File tóm tắt lệnh setup và lệnh chạy demo 1 trang. |
| 📄 [**`HUONG-DAN-TOAN-TAP.md`**](HUONG-DAN-TOAN-TAP.md) | Cẩm nang chi tiết lý thuyết, code mapping và runbook hoàn chỉnh. |

---

## 🚀 HƯỚNG DẪN 4 BƯỚC SETUP TỪ ĐẦU ĐẾN CUỐI

### BƯỚC 0: BẬT KUBERNETES TRÊN DOCKER DESKTOP (Chỉ làm 1 lần)
1. Mở **Docker Desktop**.
2. Bấm vào biểu tượng **Cài đặt ⚙️ (Settings)** ở góc trên bên phải.
3. Chọn thẻ **Kubernetes** ở thanh menu bên trái.
4. Tích chọn ô: `[v] Enable Kubernetes`.
5. Bấm **Apply & restart** và đợi 2-3 phút cho đến khi góc dưới bên trái hiện icon xanh lá: **`Kubernetes running`**.

---

### BƯỚC 1: KIỂM TRA CÔNG CỤ ĐIỀU KHIỂN
Mở **PowerShell**, kiểm tra `kubectl` và `istioctl`:
```powershell
kubectl version --client
istioctl version
```
*(Yêu cầu `istioctl` từ bản **1.24.1** trở lên để tránh bug đường dẫn trên Windows).*

---

### BƯỚC 2: TRIỂN KHAI TOÀN BỘ HỆ THỐNG
Mở PowerShell tại thư mục dự án và chạy 2 lệnh sau:

```powershell
# 1. Di chuyển vào thư mục Chủ đề 3
cd d:\VScode\midterm-software-architecture\topics\03-microservices-infrastructure

# 2. Cài đặt Istio Control Plane (profile demo) lên cụm K8s
istioctl install --set profile=demo -y

# 3. Chạy script setup tự động
.\setup-and-run.ps1
```

> **Script `setup-and-run.ps1` sẽ tự động thực hiện:**
> - Gán nhãn `istio-injection=enabled` cho namespace `default` (tự động tiêm Envoy proxy).
> - Triển khai 4 microservices Bookinfo (`productpage`, `details`, `reviews` v1/v2/v3, `ratings`).
> - Triển khai Ingress Gateway và các DestinationRules.
> - Triển khai hệ thống giám sát **Prometheus TSDB** và **Grafana Cockpit**.

---

### BƯỚC 3: KIỂM TRA TRẠNG THÁI HOÀN TẤT (2/2 READY)

Chạy lệnh kiểm tra:
```powershell
kubectl get pods
```
Chờ toàn bộ 6 Pods của Bookinfo đạt trạng thái **`READY: 2/2`** và **`STATUS: Running`**:
```text
NAME                              READY   STATUS    RESTARTS   AGE
details-v1-xxxxxxxxxx-xxxxx       2/2     Running   0          60s
productpage-v1-xxxxxxxxxx-xxxxx   2/2     Running   0          60s
ratings-v1-xxxxxxxxxx-xxxxx       2/2     Running   0          60s
reviews-v1-xxxxxxxxxx-xxxxx       2/2     Running   0          60s
reviews-v2-xxxxxxxxxx-xxxxx       2/2     Running   0          60s
reviews-v3-xxxxxxxxxx-xxxxx       2/2     Running   0          60s
```

Kiểm tra thêm pods giám sát trong `istio-system`:
```powershell
kubectl get pods -n istio-system
```
*(Đảm bảo `istiod`, `prometheus`, `grafana` đều đang `Running`).*

---

### BƯỚC 4: MỞ 3 CỔNG TRUY CẬP ĐỂ SẴN SÀNG DEMO

Mở **3 tab PowerShell riêng biệt** để chuyển tiếp cổng (port-forward) lên trình duyệt:

```powershell
# Tab 1: Web Bookinfo
kubectl port-forward svc/productpage 9080:9080
# -> Truy cập: http://localhost:9080/productpage

# Tab 2: Grafana Dashboard
kubectl port-forward svc/grafana -n istio-system 3000:3000
# -> Truy cập: http://localhost:3000

# Tab 3: Prometheus Metrics
kubectl port-forward svc/prometheus -n istio-system 9090:9090
# -> Truy cập: http://localhost:9090
```

---

## 🧹 CÁCH XÓA / RESET TOÀN BỘ HỆ THỐNG KHI CẦN LÀM LẠI TỪ ĐẦU

Nếu muốn gỡ sạch toàn bộ Bookinfo và Istio để làm lại từ đầu:

```powershell
cd d:\VScode\midterm-software-architecture\topics\03-microservices-infrastructure

# 1. Xóa Bookinfo & cấu hình mạng
kubectl delete -f projects\bookinfo\source\networking\bookinfo-gateway.yaml
kubectl delete -f projects\bookinfo\source\networking\destination-rule-all.yaml
kubectl delete -f projects\bookinfo\source\platform\kube\bookinfo.yaml

# 2. Xóa Prometheus và Grafana
kubectl delete -f projects\istio\source\samples\addons\prometheus.yaml
kubectl delete -f projects\istio\source\samples\addons\grafana.yaml

# 3. Gỡ cài đặt Istio Control Plane
istioctl uninstall --purge -y
kubectl delete namespace istio-system
```

