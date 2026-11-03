---
marp: true
theme: default
paginate: true
header: 'Chủ đề 3.3: Điều phối Cụm với Kubernetes | Tường'
footer: 'Kiến trúc Phần mềm — Báo cáo Giữa kỳ'
style: |
  section { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 35px; }
  h1 { color: #58a6ff; font-size: 26px; }
  h2, h3 { color: #79c0ff; font-size: 20px; }
  table { font-size: 13px; color: #c9d1d9; width: 100%; }
  th { background-color: #161b22; color: #58a6ff; }
  code { background-color: #161b22; color: #ff7b72; font-size: 12px; }
  pre { background-color: #161b22; font-size: 11px; padding: 10px; }
---

# SLIDE 1: ĐẶT VẤN ĐỀ & BÀI TOÁN ĐIỀU PHỐI CONTAINER (ORCHESTRATION)
- **Học phần**: Kiến trúc Phần mềm — Báo cáo Chuyên sâu: **Kubernetes (K8s) Orchestration**
- **Người thực hiện**: Tường (Thời lượng: 10 phút)
- **Hệ thống minh chứng**: [Bookinfo Manifests](../../projects/bookinfo/source/platform/kube/bookinfo.yaml)

### Khi Docker Đơn Lẻ Là Chưa Đủ:
- Làm sao quản lý hàng trăm container chạy trên hàng chục máy chủ vật lý?
- Khi 1 container bị chết lúc 2 giờ sáng, ai sẽ tự động khởi động lại nó?
- Làm sao cập nhật phiên bản mới (Deployment) mà người dùng không bị gián đoạn (Zero Downtime)?
- Làm sao tự động cân bằng tải nội bộ và phân giải tên miền động khi các container liên tục thay đổi địa chỉ IP?
- **Giải pháp Kubernetes**: Hệ điều hành phân tán cho Cloud, tự động hóa toàn bộ vòng đời ứng dụng.

---

# SLIDE 2: KIẾN TRÚC TỔNG THỂ KUBERNETES: CONTROL PLANE VS WORKER NODES

```text
┌────────────────────────────────────────────────────────┐
│               CONTROL PLANE (Master Node)              │
│  - kube-apiserver: Cổng giao tiếp REST duy nhất        │
│  - etcd: Cơ sở dữ liệu phân tán Key-Value (Chân lý)    │
│  - kube-scheduler: Lập lịch Pod lên Node tối ưu        │
│  - kube-controller-manager: Duy trì trạng thái mong muốn│
└──────────────────────────┬─────────────────────────────┘
                           │ Quản trị qua gRPC/HTTPS
┌──────────────────────────▼─────────────────────────────┐
│                 WORKER NODES (Worker Pool)             │
│  - kubelet: Agent quản lý vòng đời Pod trên từng Node  │
│  - kube-proxy: Quản lý luật mạng iptables / IPVS       │
│  - Container Runtime (containerd): Kéo image và chạy   │
└────────────────────────────────────────────────────────┘
```

---

# SLIDE 3: ĐƠN VỊ CỐT LÕI: POD — TẠI SAO POD LẠI CHỨA NHIỀU CONTAINER?
*Khái niệm nguyên tử (Atomic Unit) nhỏ nhất trong Kubernetes*

### 1. Bản Chất của Pod:
- Pod là một nhóm gồm 1 hoặc nhiều container chia sẻ chung:
  - **Network Namespace**: Dùng chung địa chỉ IP và giao tiếp với nhau qua `localhost`.
  - **Storage Volumes**: Dùng chung thư mục ổ cứng mount vào Pod.
  - **IPC Namespace**: Chia sẻ bộ nhớ chia sẻ.

### 2. Mô Hình Multi-Container (Pod `2/2 Running` trong Bookinfo):
- **Container 1**: Mã nguồn ứng dụng nghiệp vụ (`productpage`, `details`, `reviews`, `ratings`).
- **Container 2**: **Sidecar Container (`istio-proxy` / Envoy)**.
- *Lợi ích*: Tách biệt logic nghiệp vụ khỏi logic hạ tầng mà vẫn đảm bảo độ trễ giao tiếp cực thấp (gọi qua `localhost`).

---

# SLIDE 4: MÔ HÌNH HÓA WORKLOAD: DEPLOYMENT & REPLICASET
*Quản lý vòng đời và số lượng bản sao mong muốn*

### Mối Quan Hệ Giữa Deployment, ReplicaSet và Pod:
```text
[ Deployment: reviews-v1 ] (Quản lý chiến lược Rollout & Rollback)
       │
       ▼
[ ReplicaSet: reviews-v1-xxx ] (Đảm bảo đúng số lượng replicas = 1)
       │
       ▼
[ Pod: reviews-v1-xxx-yyy ] (Đơn vị thực thi chạy trên Node)
```

### Cấu Hình Thực Tế trong `bookinfo.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reviews-v2
  labels: { app: reviews, version: v2 }
spec:
  replicas: 1
  selector:
    matchLabels: { app: reviews, version: v2 }
  template:
    metadata:
      labels: { app: reviews, version: v2 }
```

---

# SLIDE 5: SERVICE DISCOVERY & CÂN BẰNG TẢI QUA KUBERNETES SERVICE
*Cung cấp địa chỉ IP ảo ổn định cho các Pod phù du (Ephemeral Pods)*

### Vấn Đề: Pod IP Liên Tục Thay Đổi Khi Restart:
- Nếu gọi trực tiếp IP của Pod, hệ thống sẽ sụp đổ khi Pod chết và sinh ra với IP mới.

### Cơ Chế Hoạt Động của ClusterIP Service:
```text
Client Request ──> [ Service: reviews (:9080) ] (ClusterIP Ảo Cố Định)
                            │
               ┌────────────┴────────────┐ (Cân bằng tải L4 Round-Robin)
               ▼                         ▼
      [ reviews-v1 Pod ]        [ reviews-v2 Pod ]
      (IP: 10.244.1.5)          (IP: 10.244.2.8)
```
- **kube-proxy**: Ghi các luật NAT vào `iptables` trên từng Node để phân phối gói tin tới đúng danh sách **Endpoints**.
- **CoreDNS**: Cho phép gọi qua tên miền nội bộ: `http://reviews:9080` hoặc `http://details:9080`.

---

# SLIDE 6: CƠ CHẾ TỰ PHỤC HỒI (SELF-HEALING) QUA RECONCILIATION LOOP
*Nguyên lý cốt lõi giúp Kubernetes tự vận hành không cần con người can thiệp*

### 1. Vòng Lặp Đối Soát Trạng Thái (Reconciliation Loop):
$$\text{Current State (Thực tế)} \xrightarrow{\quad\text{Controller}\quad} \text{Desired State (Khai báo)}$$

### 2. Kiểm Chứng Thực Nghiệm trong Bookinfo:
1. Chạy lệnh: `kubectl delete pod -l app=details`.
2. **Diễn biến từng mili-giây**:
   - `0.0s`: Pod cũ nhận tín hiệu hủy, chuyển sang trạng thái `Terminating`.
   - `0.2s`: ReplicaSet Controller phát hiện số lượng Pod thực tế (0) < mong muốn (1).
   - `0.5s`: Scheduler tìm Node phù hợp và ra lệnh cho `kubelet` kéo container.
   - `1.8s`: Pod mới đạt trạng thái `Running (2/2)`.
   - Kubernetes Service tự động cập nhật Endpoints, khách vào web **Zero Downtime**!

---

# SLIDE 7: CHIẾN LƯỢC ZERO-DOWNTIME ROLLING UPDATE & ROLLBACK
*Cập nhật phiên bản phần mềm an toàn trên môi trường Production*

### Cơ Chế Rolling Update:
- Tham số điều khiển:
  - `maxSurge: 25%`: Số lượng Pod tối đa được tạo vượt mức replicas mong muốn.
  - `maxUnavailable: 25%`: Số lượng Pod tối đa được phép dừng hoạt động trong quá trình rollout.

### Quy Trình Cập Nhật 3 Bước:
```text
Bước 1: [ Pod v1 ] [ Pod v1 ]
Bước 2: [ Pod v1 ] [ Pod v1 ] + [ Pod v2 (Mới - Đang kiểm tra probe) ]
Bước 3: [ Pod v1 ] + [ Pod v2 (Đã sẵn sàng nhận traffic) ] ──> Hủy dần [ Pod v1 ]
Bước 4: [ Pod v2 ] [ Pod v2 ] (Hoàn tất 100% Zero Downtime)
```
- Nếu bản mới bị crash, lập tức hoàn nguyên chỉ bằng 1 lệnh:  
  `kubectl rollout undo deployment/reviews-v1`

---

# SLIDE 8: HEALTH CHECKING (PROBES) — BẢO VỆ LƯU LƯỢNG ỨNG DỤNG
*Cách Kubernetes biết khi nào ứng dụng thực sự sẵn sàng nhận traffic*

### 3 Loại Probe Quan Trọng:
1. **`readinessProbe` (Kiểm tra Sẵn Sàng)**:
   - Trả lời: *"Ứng dụng đã nạp xong dữ liệu/cache để nhận request từ user chưa?"*
   - Nếu fail: Kubernetes **gỡ IP của Pod** khỏi Service Endpoints, không gửi traffic tới Pod này.
2. **`livenessProbe` (Kiểm tra Sống Sót)**:
   - Trả lời: *"Ứng dụng có bị rơi vào deadlock hay vòng lặp vô tận không?"*
   - Nếu fail: `kubelet` cưỡng bức **khởi động lại container (Restart)**.
3. **`startupProbe`**: Dành cho các ứng dụng nặng (như Java Liberty) khởi động chậm, tránh bị liveness probe kill nhầm khi đang boot.

---

# SLIDE 9: QUẢN LÝ TÀI NGUYÊN (RESOURCES REQUESTS & LIMITS)
*Quy hoạch dung lượng cụm và chống hiện tượng cạn kiệt tài nguyên*

### Khác Biệt Giữa Requests và Limits:
- **`resources.requests` (Mức sàn Cam kết)**:
  - Được `kube-scheduler` dùng để tính toán và lập lịch Pod lên Node có đủ RAM/CPU trống.
- **`resources.limits` (Mức trần Tối đa)**:
  - Nếu vượt CPU Limit: Ứng dụng bị bóp băng thông CPU (Throttling) chứ không chết.
  - Nếu vượt Memory Limit: Container lập tức bị tiêu diệt bởi **OOMKilled (Out Of Memory)**.

```yaml
resources:
  requests:
    cpu: "100m"      # Cam kết tối thiểu 0.1 CPU core
    memory: "128Mi"  # Cam kết tối thiểu 128MB RAM
  limits:
    cpu: "500m"      # Tối đa 0.5 CPU core
    memory: "512Mi"  # Chạm trần 512MB sẽ bị OOMKill
```

---

# SLIDE 10: TỔNG KẾT & ARCHITECTURAL TRADE-OFFS CỦA KUBERNETES

### Bảng Đánh Đổi Kiến Trúc (Trade-offs):

| Lợi Thế Vượt Trội | Đánh Đổi & Chi Phí Thực Tế | Giải Pháp Khắc Phục |
|---|---|---|
| **Self-Healing Tuyệt Đối**: Cụm tự phục hồi 24/7 không cần trực đêm. | **Độ Phức Tạp Cấu Hình**: Hàng chục file YAML dễ sai sót cú pháp. | Dùng Helm Chart hoặc Kustomize để chuẩn hóa mẫu khai báo. |
| **Zero-Downtime Rollout**: Cập nhật phiên bản liên tục giữa ban ngày. | **Quản Trị Hạ Tầng Nặng**: etcd, networking, certificate đòi hỏi kỹ năng cao. | Sử dụng dịch vụ Managed Kubernetes (GKE, EKS, AKS). |
| **Cân Bằng Tải Tự Động**: Tự động scale ngang qua HPA. | **Tài Nguyên Control Plane**: Tiêu tốn CPU/RAM cho master components. | Quy hoạch node size hợp lý, tối ưu hóa kích thước cụm. |

---

## 🎙️ KỊCH BẢN THUYẾT TRÌNH 10 PHÚT — CHỦ ĐỀ KUBERNETES

- **[0:00 – 1:00] Slide 1 & 2**: *"Kính thưa Thầy/Cô, em là Tường, trình bày về Nền tảng Điều phối Kubernetes. Khi hệ thống mở rộng, Kubernetes giải quyết bài toán quản lý hàng trăm container qua mô hình Master-Worker: Control Plane giữ trạng thái chân lý trong etcd, Worker Nodes thực thi Pod qua kubelet và kube-proxy."*
- **[1:00 – 2:30] Slide 3 & 4**: *(Mở file `platform/kube/bookinfo.yaml`)*: *"Đơn vị nhỏ nhất của K8s là Pod. Trong Bookinfo, mỗi Pod chứa 2 container (`2/2 Running`): gồm 1 container app nghiệp vụ và 1 container Envoy sidecar. Deployment quản lý ReplicaSet để bảo đảm đúng số lượng bản sao mong muốn."*
- **[2:30 – 4:00] Slide 5 & 6**: *"Địa chỉ IP của Pod liên tục thay đổi. Kubernetes Service ClusterIP giải quyết bằng cách cung cấp IP ảo cố định và DNS nội bộ `:9080`, tự động chia tải Round-Robin. Trái tim của K8s là vòng lặp Reconciliation loop: liên tục so sánh trạng thái thực tế với mong muốn để tự động bù đắp lỗi."*
- **[4:00 – 5:30] Slide 7 & 8**: *"Để cập nhật không gián đoạn, K8s thực hiện Rolling Update song song. Kết hợp với readinessProbe (chỉ route traffic khi app nạp xong) và livenessProbe (restart khi deadlock), cụm bảo vệ tuyệt đối tính liên tục của dịch vụ."*
- **[5:30 – 6:30] Slide 9 & 10**: *"Chúng ta áp dụng requests và limits để tránh lỗi OOMKilled. Đánh đổi lớn nhất của Kubernetes là độ phức tạp cấu hình, nhưng mang lại khả năng tự phục hồi và co giãn không có đối thủ."*
- **[6:30 – 9:30] Live Demo**: Chạy lệnh `kubectl delete pod -l app=details`, quan sát trên Terminal pod mới sinh ra trong 1.8s và F5 trình duyệt chứng minh zero downtime.
- **[9:30 – 10:00] Kết bài & Vấn đáp**: Tuyên bố kết thúc bài thuyết trình Kubernetes.

