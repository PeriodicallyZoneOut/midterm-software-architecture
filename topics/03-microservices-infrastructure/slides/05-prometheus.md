---
marp: true
theme: default
paginate: true
header: 'Chủ đề 3.5: Giám sát Số liệu Hệ thống với Prometheus | Tường'
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

# SLIDE 1: ĐẶT VẤN ĐỀ & TRỤ CỘT METRICS TRONG QUAN SÁT HỆ THỐNG
- **Học phần**: Kiến trúc Phần mềm — Báo cáo Chuyên sâu: **Prometheus Metrics Engine**
- **Người thực hiện**: Tường (Thời lượng: 10 phút)
- **Hệ thống minh chứng**: [Prometheus Manifests](../../projects/istio/source/samples/addons/prometheus.yaml)

### 3 Trụ Cột của Observability (Quan Sát Toàn Diện):
1. **Logs**: Ghi lại sự kiện rời rạc mang tính chi tiết cao (high context, tốn dung lượng lưu trữ).
2. **Traces**: Theo dõi hành trình luồng request qua các microservice phân tán (end-to-end hop).
3. **Metrics**: Dữ liệu chuỗi thời gian số học được tổng hợp định kỳ (thấp chi phí, cảnh báo tức thì).

### Tại Sao Prometheus Trở Thành Tiêu Chuẩn De Facto Trong Cloud-Native?
- Lưu trữ dạng **Time-Series Database (TSDB)** tối ưu hóa cho ghi chép số liệu hàng triệu mẫu/giây.
- Độc lập, không phụ thuộc vào hạ tầng bên ngoài (self-contained, local storage).
- Khả năng **Service Discovery** động tự tìm thấy Pods trong Kubernetes.
- Ngôn ngữ truy vấn quyền năng **PromQL (Prometheus Query Language)**.

---

# SLIDE 2: KIẾN TRÚC TỔNG THỂ CỦA PROMETHEUS SERVER

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PROMETHEUS ARCHITECTURE                         │
│                                                                        │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │                     PROMETHEUS SERVER                        │     │
│   │                                                              │     │
│   │  ┌────────────────┐     ┌────────────────┐    ┌───────────┐  │     │
│   │  │ Scrape Manager │────>│ TSDB           │<───│ PromQL    │  │     │
│   │  │ (Retrieval)    │     │ (Local Storage)│    │ Engine    │  │     │
│   │  └───────▲────────┘     └────────────────┘    └─────▲─────┘  │     │
│   └──────────c──────────────────────────────────────────│────────┘     │
│              │ HTTP Pull (Mỗi 15s)                      │ API Query    │
│              │                                          │              │
│   ┌──────────▼──────────┐                 ┌─────────────▼──────────┐   │
│   │ Kubernetes Targets  │                 │ Visualization / Alert  │   │
│   │ - Pods (Envoy 15090)│                 │ - Grafana Dashboard    │   │
│   │ - Nodes / cAdvisor  │                 │ - Alertmanager         │   │
│   │ - K8s API Server    │                 │ - Prometheus Web UI    │   │
│   └─────────────────────┘                 └────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

# SLIDE 3: CƠ CHẾ PULL MODEL & THU THẬP METRICS TỪ ENVOY SIDECAR
*Làm sao Prometheus thu thập được toàn bộ số liệu mạng mà không cần can thiệp code ứng dụng?*

### 1. Triết Lý Pull Model vs Push Model:
- **Push Model**: Các app chủ động bắn metric ra server ➔ Dễ gây DDoS hệ thống giám sát khi có sự cố.
- **Pull Model (Prometheus)**: Server chủ động kéo (scrape) định kỳ ➔ Kiểm soát được tốc độ và tải giám sát; tự động phát hiện target sập khi kéo thất bại.

### 2. Thu Thập Dữ Liệu từ Envoy Proxy (`:15090/stats/prometheus`):
- Trong Bookinfo, ứng dụng chạy độc lập (Python, Ruby, Java, Node.js).
- Sidecar Envoy proxy của Istio đứng ở cổng biên tiếp nhận mọi request và đo lường L7 telemetry.
- Envoy mở sẵn endpoint nội bộ tại cổng `:15090/stats/prometheus`.
- Cấu hình Prometheus trong `samples/addons/prometheus.yaml`:
  ```yaml
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
      target_label: __address__
      regex: 15090
  ```

---

# SLIDE 4: MÔ HÌNH DỮ LIỆU CHUỖI THỜI GIAN (DATA MODEL)
*Dữ liệu được tổ chức dưới dạng Metric Name, Key-Value Labels, và Timestamps*

### Cấu Trúc Định Danh Metric:
$$\text{<metric name>}\{\text{<label name>} = \text{"<label value>"}, ...\} \quad \text{value} \quad [\text{timestamp}]$$

### Ví Dụ Thực Tế Từ Lưới Dịch Vụ Bookinfo:
```text
istio_requests_total{
  reporter="destination",
  source_workload="productpage-v1",
  destination_workload="reviews-v2",
  destination_service="reviews.default.svc.cluster.local",
  response_code="200"
} 14285 1741046400000
```

### Ý Nghĩa Của Hệ Thống Labels (Đa Chiều - Multi-dimensional):
- Cho phép cắt lát (slice & dice) dữ liệu theo bất kỳ chiều nào mà không cần đổi tên metric.
- Lọc theo phiên bản: `destination_version="v2"`
- Lọc theo mã trạng thái: `response_code=~"5.*"`
- Gom nhóm theo workload: `by (destination_workload)`

---

# SLIDE 5: BỐN LOẠI METRICS CỐT LÕI (METRIC TYPES)

| Loại Metric | Định Nghĩa | Đặc Tính | Ứng Dụng Thực Tế Trong Dự Án |
|---|---|---|---|
| **1. Counter** | Giá trị số chỉ tăng (hoặc reset về 0 khi restart) | Không bao giờ giảm; dùng hàm `rate()` để tính tốc độ tăng | `istio_requests_total`: Đếm tổng số request HTTP đã phục vụ |
| **2. Gauge** | Giá trị số tức thời có thể tăng hoặc giảm | Biểu thị trạng thái hiện tại của tài nguyên | `container_memory_usage_bytes`: Lượng RAM đang dùng của Pod |
| **3. Histogram** | Phân bổ mẫu thành các ngăn (buckets) tích lũy | Đi kèm các bucket `_bucket{le="..."}`, `_sum`, `_count` | `istio_request_duration_milliseconds_bucket`: Phân vị thời gian phản hồi |
| **4. Summary** | Tương tự Histogram nhưng tính sẵn quantile ở phía client | Tiết kiệm CPU server nhưng không thể tổng hợp gộp nhiều instance | Ít dùng trong môi trường microservices phân tán như Istio |

---

# SLIDE 6: NỀN TẢNG CÚ PHÁP TRUY VẤN PROMQL
*PromQL (Prometheus Query Language) là ngôn ngữ biểu thức số học dựa trên vector thời gian*

### 1. Kiểu Dữ Liệu Đầu Ra:
- **Instant Vector**: Tập hợp các chuỗi thời gian chứa 1 giá trị duy nhất tại thời điểm hiện tại:
  `istio_requests_total{destination_workload="reviews-v1"}`
- **Range Vector**: Tập hợp các chuỗi thời gian chứa một mảng giá trị trong một khoảng thời gian lùi về trước:
  `istio_requests_total{destination_workload="reviews-v1"}[5m]`
- **Scalar**: Một giá trị số thực đơn lẻ.

### 2. Các Toán Tử & Hàm Cốt Lõi:
- `rate(v[range])`: Tính tốc độ tăng trung bình mỗi giây của Counter (tự bù đắp khi counter reset).
- `sum() by (...)`: Gom nhóm và tính tổng theo các nhãn chỉ định.
- `histogram_quantile(φ, b)`: Tính giá trị phân vị $\phi$ (ví dụ: 0.95 cho P95) từ các bucket histogram.

---

# SLIDE 7: PROMQL THỰC CHIẾN 1 — ĐO LƯỜNG LƯU LƯỢNG (RPS)
*Đo số yêu cầu trên mỗi giây gửi đến từng Microservice trong Bookinfo*

### Biểu Thức PromQL Tính RPS Theo Workload:
```promql
sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)
```

```text
Grafana / Prometheus Query Visualizer:
productpage-v1  ████████████████████████████████ 32.4 req/s
reviews-v1      ████████████ 12.1 req/s
reviews-v2      ████████████ 11.8 req/s
details-v1      ████████████████████████████ 28.5 req/s
```

### Cơ Chế Phân Tích Kỹ Thuật:
1. `reporter="destination"`: Lấy metric được đo tại phía nhận (tránh đếm đúp từ cả client và server).
2. `[1m]`: Cửa sổ trượt 1 phút để tính tốc độ tăng tức thời ổn định, loại bỏ nhiễu.
3. `rate(...)`: Đổi từ tổng tích lũy (Cumulative Counter) sang tốc độ xử lý mỗi giây (RPS).
4. `sum(...) by (destination_workload)`: Gộp tất cả các replica của Pod lại thành số liệu tổng cho service.

---

# SLIDE 8: PROMQL THỰC CHIẾN 2 — TÍNH PHÂN VỊ ĐỘ TRỄ (P95/P99)
*Đo lường trải nghiệm người dùng thực tế bằng phân vị (Percentiles) thay vì trung bình cộng*

### Tại Sao Không Dùng Giá Trị Trung Bình (Average Latency)?
- Giá trị trung bình che giấu các trường hợp bất thường (Tail Latency).
- 95% khách hàng có thể load trang trong 50ms, nhưng 5% khách VIP có thể bị treo đến 5 giây!

### Biểu Thức PromQL Tính P95 Latency của `productpage`:
```promql
histogram_quantile(
  0.95,
  sum(rate(istio_request_duration_milliseconds_bucket{destination_workload="productpage-v1"}[1m])) by (le)
)
```

### Cách Hoạt Động của Phân Vị Bucket:
- Envoy ghi nhận thời gian xử lý vào các thùng đếm tích lũy `le` (less than or equal):  
  `le="10"`, `le="25"`, `le="50"`, `le="100"`, `le="250"`, `le="1000"`, `le="+Inf"`.
- Hàm `histogram_quantile(0.95, ...)` nội suy tuyến tính bên trong bucket để tìm ra ngưỡng thời gian mà 95% request kết thúc bên dưới ngưỡng đó.

---

# SLIDE 9: PROMQL THỰC CHIẾN 3 — TỈ LỆ LỖI VÀ THEO DÕI SLO
*Giám sát 4 Tín hiệu Vàng SRE (Golden Signals): Latency, Traffic, Errors, Saturation*

### 1. Đếm Tần Suất Lỗi HTTP 5xx:
```promql
sum(rate(istio_requests_total{reporter="destination", response_code=~"5.*"}[1m])) by (destination_workload)
```

### 2. Tính Tỉ Lệ Lỗi (Error Rate %) So Với Tổng Traffic:
```promql
(
  sum(rate(istio_requests_total{reporter="destination", response_code=~"5.*"}[5m]))
  /
  sum(rate(istio_requests_total{reporter="destination"}[5m]))
) * 100
```

### Ứng Dụng Trong Thực Tế:
- Thiết lập cảnh báo SLO (Service Level Objective): Bắn alert Slack/PagerDuty khi `Error Rate > 1%` liên tục trong 3 phút.
- Phát hiện lỗi ngầm do Service Mesh cấu hình sai Timeout hoặc Circuit Breaker kích hoạt.

---

# SLIDE 10: TỔNG KẾT & ARCHITECTURAL TRADE-OFFS CỦA PROMETHEUS

### Bảng Đánh Đổi Kiến Trúc Giám Sát (Trade-offs):

| Điểm Mạnh Vượt Trội | Giới Hạn Kiến Trúc & Thách Thức | Giải Pháp Thiết Kế Khắc Phục |
|---|---|---|
| **Khai Thác Đa Chiều (Labels)**: PromQL cực kỳ mạnh mẽ để cắt lát số liệu. | **Bùng Nổ Lực Lượng (Cardinality Explosion)**: Tạo quá nhiều label độc nhất làm cạn kiệt RAM. | Tuyệt đối không đưa User ID, Request ID hoặc Session ID vào Label. |
| **Pull Model An Toàn**: Không lo server giám sát bị ứng dụng làm nghẽn. | **Độ Trễ Giám Sát (Scrape Delay)**: Số liệu trễ tối thiểu bằng khoảng cách chu kỳ kéo (15s). | Chấp nhận đánh đổi giữa độ phân giải thời gian thực và chi phí CPU/mạng. |
| **Không Phụ Thuộc Cụm (Self-contained)**: Dễ cài đặt qua YAML, lưu trữ local disk. | **Khó Lưu Trữ Dài Hạn (Long-term Retention)**: TSDB nội bộ không thiết kế cho scale hàng năm. | Tích hợp **Thanos** hoặc **Cortex** để đẩy số liệu dài hạn lên Object Storage (S3/MinIO). |

---

## 🎙️ KỊCH BẢN THUYẾT TRÌNH 10 PHÚT — CHỦ ĐỀ PROMETHEUS

- **[0:00 – 1:00] Slide 1: Đặt Vấn Đề**: *"Kính thưa Thầy/Cô, em là Tường. Trong kiến trúc microservices phân tán, ta không thể SSH vào từng server xem log khi có sự cố. Chúng ta cần trụ cột Metrics của Observability để nắm bắt sức khỏe hệ thống theo thời gian thực. Prometheus là cỗ máy số liệu chuẩn Cloud-Native được tích hợp trực tiếp trong dự án Bookinfo của em."*
- **[1:00 – 2:00] Slide 2: Kiến Trúc Server**: *"Kiến trúc Prometheus Server gồm 3 thành phần chính: Scrape Manager đi thu thập dữ liệu qua giao thức HTTP; TSDB tối ưu hóa cho ghi chép số liệu chuỗi thời gian; và PromQL Engine xử lý các phép toán tính tốc độ và phân vị."*
- **[2:00 – 3:30] Slide 3 & 4: Cơ Chế Kéo & Data Model**: *(Chỉ vào file `prometheus.yaml`)*: *"Prometheus dùng cơ chế Pull thay vì Push để kiểm soát tải. Điểm đặc biệt trong kiến trúc của em là Prometheus không scrape code Python hay Java trực tiếp, mà scrape Envoy Sidecar tại cổng `:15090/stats/prometheus`. Mô hình dữ liệu gồm Tên Metric và tập nhãn đa chiều key-value, cho phép ta lọc chi tiết theo service, version và status code."*
- **[3:30 – 4:30] Slide 5 & 6: 4 Loại Metrics & PromQL**: *"Prometheus định nghĩa 4 loại metric cốt lõi: Counter chỉ tăng, Gauge tăng giảm tự do, Histogram đếm theo thùng dữ liệu, và Summary. Ngôn ngữ PromQL làm việc trên hai cấu trúc chính là Instant Vector và Range Vector với các toán tử gom nhóm `by` và hàm đạo hàm `rate()`."*
- **[4:30 – 6:00] Slide 7 & 8: PromQL Thực Chiến**: *(Trình bày 2 câu lệnh trên slide)*: *"Đây là 2 câu lệnh PromQL em thường xuyên sử dụng: Thứ nhất, tính RPS bằng hàm `rate()` chia cho cửa sổ 1 phút để thấy lưu lượng tức thời của từng service. Thứ hai, tính độ trễ P95 bằng `histogram_quantile(0.95, ...)`. Chúng em không dùng trung bình cộng vì giá trị trung bình sẽ che giấu hiện tượng Tail Latency ảnh hưởng đến khách hàng."*
- **[6:00 – 7:00] Slide 9 & 10: Tỉ Lệ Lỗi & Trade-offs**: *"Về mặt kiểm soát chất lượng, câu lệnh tính tỉ lệ lỗi 5xx trên tổng traffic giúp đội ngũ SRE phát hiện vi phạm SLO. Về mặt đánh đổi, Prometheus đánh đổi khả năng lưu trữ dài hạn lấy tốc độ truy vấn cục bộ cực nhanh, và nguy cơ lớn nhất là Cardinality Explosion nếu ta lỡ đưa User ID vào Label."*
- **[7:00 – 9:30] Live Demo Thực Tế**: *(Mở terminal chạy lệnh)*:
  ```powershell
  kubectl port-forward svc/prometheus 9090:9090 -n istio-system
  ```
  Truy cập `http://localhost:9090`, gõ biểu thức `sum(rate(istio_requests_total[1m])) by (destination_workload)` và bấm Tab Graph để thấy biểu đồ lưu lượng biến động theo từng request test.
- **[9:30 – 10:00] Kết Luận**: Tóm tắt vai trò của Prometheus và chuyển giao sang phần trực quan hóa với Grafana.

