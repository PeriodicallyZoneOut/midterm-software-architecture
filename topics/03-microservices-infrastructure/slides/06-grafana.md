---
marp: true
theme: default
paginate: true
header: 'Chủ đề 3.6: Trực quan hóa Dữ liệu Giám sát với Grafana | Tường'
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

# SLIDE 1: ĐẶT VẤN ĐỀ & VAI TRÒ CỦA GRAFANA TRONG QUẢN TRỊ SRE
- **Học phần**: Kiến trúc Phần mềm — Báo cáo Chuyên sâu: **Grafana Observability Dashboard**
- **Người thực hiện**: Tường (Thời lượng: 10 phút)
- **Hệ thống minh chứng**: [Grafana Manifests](../../projects/istio/source/samples/addons/grafana.yaml)

### Khoảng Trống Giữa Dữ Liệu Thô và Trực Giác Con Người:
- Prometheus cung cấp hàng triệu mẫu số liệu chuỗi thời gian thô qua PromQL.
- Nhưng trong ca trực sự cố (Incident Response), kỹ sư SRE không thể vừa gõ PromQL vừa đoán hệ thống bị nghẽn ở đâu.
- **Yêu cầu cốt lõi**:
  - Cần một "Giao diện kính đơn" (**Single Pane of Glass**) hợp nhất toàn bộ thông tin.
  - Nhận biết ngay vi phạm SLO qua màu sắc trực quan (Xanh: Bình thường, Vàng: Cảnh báo, Đỏ: Nguy cấp).
  - Tương quan trực quan giữa lưu lượng mạng (RPS), độ trễ (Latency) và tài nguyên CPU/RAM.

---

# SLIDE 2: KIẾN TRÚC GRAFANA & TÍCH HỢP PROMETHEUS DATASOURCE

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        GRAFANA INTEGRATION FLOW                        │
│                                                                        │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │                      GRAFANA SERVER                          │     │
│   │                                                              │     │
│   │   [ Dashboard Engine ] <─── [ Provisioning / ConfigMaps ]    │     │
│   │            │                                                 │     │
│   │            ▼                                                 │     │
│   │   [ DataSource Plugin: Prometheus ]                          │     │
│   └────────────┬─────────────────────────────────────────────────┘     │
│                │ HTTP Proxy Request (http://prometheus:9090)           │
│                ▼                                                       │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │             PROMETHEUS SERVICE (istio-system)                │     │
│   │             (TSDB / Instant & Range Vector API)              │     │
│   └──────────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────────┘
```

### Cấu Hình Provisioning Tự Động Trong `samples/addons/grafana.yaml`:
```yaml
datasources.yaml: |
  apiVersion: 1
  datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
    jsonData:
      timeInterval: 15s
```

---

# SLIDE 3: BỘ PANEL ĐA DẠNG & NGUYÊN TẮC THIẾT KẾ TRỰC QUAN

```text
┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│       STAT PANEL        │       GAUGE PANEL       │    TIME-SERIES PANEL    │
│      Current RPS        │     CPU Saturation      │   P95 Latency Over Time │
│       ┌───────┐         │       ┌─────────┐       │   120ms ─┐   /\         │
│       │ 42.5  │ req/s   │       │   78%   │       │    80ms ─┼──/  \──/\    │
│       └───────┘         │       └─────────┘       │    40ms ─┴─/    \───\─  │
├─────────────────────────┴─────────────────────────┴─────────────────────────┤
│                                BAR CHART                                    │
│                       HTTP Status Code Breakdown                            │
│           200 OK: ████████████████████████████████ 98.2%                    │
│           503 Service Unavailable: █ 1.8%                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Nguyên Tắc Thiết Kế Dashboard SRE Tốt:
- **Từ Tổng thể đến Chi tiết (Top-down)**: Đặt các chỉ số tổng hợp cấp cao (RPS, Success Rate) ở hàng trên cùng.
- **Quy tắc Mã màu Ngưỡng (Thresholds)**:
  - Xanh lá (< 100ms) ➔ Vàng (100–300ms) ➔ Đỏ rực (> 300ms).

---

# SLIDE 4: ISTIO MESH DASHBOARD — BỨC TRANH TOÀN CẢNH MẠNG LƯỚI
*Dashboard cấp cao nhất cung cấp góc nhìn vĩ mô về toàn bộ Service Mesh*

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        ISTIO MESH DASHBOARD                            │
│                                                                        │
│   Global Request Volume      Global Success Rate      4xx / 5xx Errors │
│   ┌───────────────────┐      ┌─────────────────┐      ┌──────────────┐ │
│   │     48.2 req/s    │      │     99.85 %     │      │     0.15 %   │ │
│   └───────────────────┘      └─────────────────┘      └──────────────┘ │
│                                                                        │
│   [ Workload Traffic Distribution ]                                    │
│   productpage-v1 ──> reviews-v1 (50%) ──> ratings-v1 (50%)             │
│                  ──> reviews-v2 (50%) ──> ratings-v1 (50%)             │
│                  ──> details-v1 (100%)                                 │
└────────────────────────────────────────────────────────────────────────┘
```

### Giá Trị Vận Hành Của Mesh Dashboard:
- Nhận biết ngay khi có sự cố diện rộng ảnh hưởng đến toàn bộ hệ thống.
- Theo dõi tổng lưu lượng ingress đổ vào cluster qua Ingress Gateway.

---

# SLIDE 5: ISTIO SERVICE DASHBOARD — SOI CHI TIẾT TỪNG WORKLOAD
*Dashboard chuyên sâu phân tích hành vi của một Microservice cụ thể*

```text
Dashboard Variable Selected: $service = "reviews.default.svc.cluster.local"
```

### 1. Inbound Requests Volume (Lưu Lượng Đến):
- Phân tách theo Workload: Ai đang gọi đến reviews? (`source_workload="productpage-v1"`).
- Phân bổ theo HTTP Response Code: Bao nhiêu request 200, bao nhiêu lỗi 503?

### 2. Request Duration Percentiles (Thời Gian Xử Lý):
- Biểu diễn đồng thời 3 đường đồ thị: **P50 (Median)**, **P90**, và **P99**.
- Giúp phát hiện nhanh hiện tượng "Độ trễ đuôi" khi bản `reviews:v2` gọi sang `ratings`.

### 3. Outbound Requests (Lưu Lượng Gọi Đi):
- Thấy rõ `reviews:v2` và `reviews:v3` tạo thêm kết nối outbound sang `ratings:v1` để lấy số sao đánh giá.

---

# SLIDE 6: TƯƠNG QUAN GIỮA TÀI NGUYÊN HẠ TẦNG VÀ LƯU LƯỢNG MẠNG
*Khả năng ghép nối dữ liệu từ nhiều nguồn trong cùng một giao diện*

```text
┌────────────────────────────────────────────────────────────────────────┐
│   TẦNG DỊCH VỤ (Prometheus Istio Telemetry)                            │
│   Traffic Spike: 10 req/s  ──>  50 req/s (Bùng nổ tải)                 │
│   Latencies P95: 35ms      ──>  280ms                                  │
├────────────────────────────────────────────────────────────────────────┤
│   TẦNG TÀI NGUYÊN CONTAINER (cAdvisor Metrics)                         │
│   Pod CPU:       15%       ──>  92% (Gần ngưỡng nghẽn CPU)             │
│   Pod Memory:    64MB      ──>  118MB                                  │
└────────────────────────────────────────────────────────────────────────┘
```

### Lợi Ích Của Phân Tích Tương Quan (Correlation Analysis):
- Trả lời câu hỏi: *Độ trễ tăng do logic code bị nghẽn CPU, hay do băng thông mạng bị nghẽn?*
- Giúp định cỡ lại `resources.requests` và `limits` trong Kubernetes Deployment một cách chính xác dựa trên bằng chứng dữ liệu.

---

# SLIDE 7: DASHBOARD TEMPLATING & CƠ CHẾ BIẾN ĐỘNG DYNAMIC VARIABLES
*Giải quyết bài toán bùng nổ số lượng dashboard khi có hàng trăm microservices*

### Nếu Không Dùng Templating:
- Dự án có 10 service ➔ Phải tạo và bảo trì thủ công 10 cái dashboard riêng lẻ.
- Rất dễ sai lệch cấu hình và khó nâng cấp đồng loạt.

### Giải Pháp Biến Động (Dynamic Variables) Trong Grafana:
```sql
Namespace Variable:
label_values(istio_requests_total, destination_workload_namespace)

Service Variable:
label_values(istio_requests_total{destination_workload_namespace="$namespace"}, destination_service_name)

Workload Variable:
label_values(istio_requests_total{destination_service_name="$service"}, destination_workload)
```

- Khi người dùng chọn `$service = reviews`, tất cả Panel trên Dashboard tự động cập nhật câu truy vấn PromQL tương ứng.

---

# SLIDE 8: PHÂN TÍCH TELEMETRY THỰC CHIẾN KHI TRAFFIC BURST
*Quan sát biểu đồ Grafana trong quá trình kiểm thử tải (Traffic Generator)*

### Kịch Bản Mô Phỏng:
Chạy script sinh tải 100 requests liên tục vào `productpage`:
```powershell
for ($i=1; $i -le 100; $i++) {
    Invoke-WebRequest -Uri "http://localhost/productpage" -UseBasicParsing | Out-Null
}
```

```text
Kết Quả Quan Sát Được Trên Grafana Service Dashboard:
1. RPS Panel:           Đột ngột vọt từ 0.2 lên 28.5 req/s.
2. Latency P95 Panel:   Ổn định ở mức 45ms, không xuất hiện gai nhọn (spike).
3. Success Rate Panel:  Duy trì vững vàng ở mức 100%.
4. Review Workload:     Traffic chia đều 50/50 giữa reviews-v1 và reviews-v2.
```
- **Ý nghĩa kiến trúc**: Chứng minh tính ổn định của cụm K8s và khả năng chịu tải của Envoy sidecar.

---

# SLIDE 9: THIẾT LẬP CẢNH BÁO SRE (ALERTING) & QUẢN LÝ SLO
*Chuyển từ cơ chế giám sát bị động (Passive) sang chủ động phòng ngừa (Proactive)*

### 1. Grafana Alert Rule Mẫu:
- **Tiêu chuẩn SLO**: "Tỉ lệ lỗi của `productpage` không được vượt quá 1% trong 5 phút".
- **Condition**:
  $$\frac{\text{sum(rate(istio\_requests\_total}\{\text{response\_code}=\sim"5.*"\}))}{\text{sum(rate(istio\_requests\_total\}))}} > 0.01$$
- **Evaluation**: Kiểm tra mỗi 1 phút, kích hoạt trạng thái `Alerting` nếu vi phạm kéo dài 5 phút liên tục (`for: 5m`).

### 2. Kênh Thông Báo Cảnh Báo (Notification Channels):
- Tích hợp tự động gửi Webhook đến Slack, Microsoft Teams, hoặc PagerDuty.
- Đính kèm đường dẫn trực tiếp (deep link) trỏ thẳng vào Dashboard tại thời điểm xảy ra sự cố.

---

# SLIDE 10: TỔNG KẾT & ARCHITECTURAL TRADE-OFFS CỦA GRAFANA

### Bảng Đánh Đổi Kiến Trúc Bảng Điều Khiển:

| Lợi Thế Cốt Lõi | Chi Phí & Thách Thức Vận Hành | Giải Pháp Tối Ưu Hóa |
|---|---|---|
| **Trực Quan Hóa Đỉnh Cao**: Biến số liệu thô thành biểu đồ sống động, dễ đọc cho mọi stakeholder. | **Tải Truy Vấn Prometheus**: Khi nhiều người cùng mở dashboard, Grafana gửi liên tục hàng trăm truy vấn nặng. | Thiết lập khoảng làm mới tự động hợp lý (ví dụ: `Auto-refresh: 1m` thay vì `5s`). |
| **Hệ Thống Mẫu Hóa Linh Hoạt**: Dùng biến động giúp 1 dashboard đại diện cho mọi service. | **Nguy Cơ Lạm Dụng Panel**: Nhồi nhét quá nhiều panel phức tạp gây quá tải trình duyệt web client. | Áp dụng nguyên tắc KISS; chia nhỏ thành Mesh Dashboard, Service Dashboard riêng biệt. |
| **Quản Lý Bằng Code (Dashboard-as-Code)**: Lưu dashboard dưới dạng file JSON và ConfigMap K8s. | **Đồng Bộ Phiên Bản**: Chỉnh sửa trực tiếp trên UI có thể bị mất khi Pod Grafana restart. | Luôn export JSON và lưu vào Git repository qua CI/CD pipeline hoặc ConfigMap. |

---

## 🎙️ KỊCH BẢN THUYẾT TRÌNH 10 PHÚT — CHỦ ĐỀ GRAFANA

- **[0:00 – 1:00] Slide 1: Đặt Vấn Đề**: *"Kính thưa Thầy/Cô, em là Tường. Nếu như Prometheus là cỗ máy thu thập và tính toán số liệu ngầm dưới hạ tầng, thì Grafana chính là bộ mặt trực quan của hệ sinh thái Observability. Khi xảy ra sự cố, kỹ sư SRE không thể vừa debug vừa gõ lệnh PromQL, mà cần một Single Pane of Glass để phát hiện ngay điểm nghẽn."*
- **[1:00 – 2:00] Slide 2: Kiến Trúc & Datasource**: *(Chỉ vào file `grafana.yaml`)*: *"Grafana kết nối với Prometheus qua HTTP proxy tại URL `http://prometheus:9090`. File cấu hình mẫu trong dự án của em tự động provision sẵn DataSource này thông qua Kubernetes ConfigMap mà không cần người dùng phải thiết lập bằng tay."*
- **[2:00 – 3:30] Slide 3 & 4: Bộ Panel & Mesh Dashboard**: *"Grafana cung cấp đa dạng panel từ Stat tức thời, Gauge đo bão hòa tài nguyên, đến Time-series độ trễ. Ở cấp độ cao nhất, Istio Mesh Dashboard cung cấp 3 tín hiệu sinh mệnh: Tổng lưu lượng mạng (RPS), Tỉ lệ thành công 99.85%, và Tỉ lệ lỗi 4xx/5xx phân bổ theo từng microservice."*
- **[3:30 – 5:00] Slide 5 & 6: Service Dashboard & Tương Quan Tài Nguyên**: *"Khi cần đào sâu vào từng service như `reviews`, Service Dashboard phân tích chi tiết: Lưu lượng Inbound từ `productpage`, Outbound sang `ratings`, và đặc biệt là 3 đường phân vị độ trễ P50, P90, P99. Điểm mạnh nhất của Grafana là khả năng tương quan giữa độ trễ mạng của Envoy và mức sử dụng CPU/RAM của container để tìm nguyên nhân gốc rễ."*
- **[5:00 – 6:00] Slide 7 & 8: Templating & Burst Test**: *"Nhờ cơ chế Dashboard Templating với các biến động `$namespace`, `$service`, một dashboard duy nhất có thể phục vụ hàng trăm microservices. Trong bài kiểm thử tải 100 requests vào `productpage`, Grafana lập tức ghi nhận RPS tăng vọt lên 28 req/s nhưng độ trễ P95 vẫn giữ đều ở 45ms."*
- **[6:00 – 7:00] Slide 9 & 10: Alerting & Trade-offs**: *"Về mặt phòng ngừa, Grafana Alerting hỗ trợ cấu hình ngưỡng SLO để chủ động bắn thông báo qua Slack. Về mặt đánh đổi, việc mở quá nhiều dashboard với chu kỳ refresh ngắn 5 giây có thể gây quá tải cho Prometheus server, vì vậy giải pháp tối ưu là duy trì refresh 15s hoặc 1m."*
- **[7:00 – 9:30] Live Demo Thực Tế**: *(Mở terminal chạy lệnh)*:
  ```powershell
  kubectl port-forward svc/grafana 3000:3000 -n istio-system
  ```
  Mở trình duyệt tại `http://localhost:3000`, truy cập mục Dashboards ➔ chọn `Istio Service Dashboard`, chọn dropdown Service là `productpage`, kích hoạt reload và sinh tải để thấy các đường đồ thị nhảy thời gian thực.
- **[9:30 – 10:00] Kết Luận**: Tóm lược toàn bộ giải pháp giám sát trực quan và tổng kết giá trị của Grafana đối với hệ thống SRE.

