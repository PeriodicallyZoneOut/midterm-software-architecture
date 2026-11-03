---
marp: true
theme: default
paginate: true
header: 'Chủ đề 3.4: Quản trị Lưới Dịch vụ với Istio Service Mesh | Tường'
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

# SLIDE 1: ĐẶT VẤN ĐỀ & SỰ CẦN THIẾT CỦA SERVICE MESH
- **Học phần**: Kiến trúc Phần mềm — Báo cáo Chuyên sâu: **Istio Service Mesh**
- **Người thực hiện**: Tường (Thời lượng: 10 phút)
- **Hệ thống minh chứng**: [Bookinfo Istio Networking](../../projects/bookinfo/source/networking)

### Nỗi Đau Lớn Khi Số Lượng Microservices Tăng Lên:
- Làm sao triển khai mã hóa **Mutual TLS (mTLS)** cho toàn bộ giao tiếp mạng nội bộ?
- Làm sao thực hiện **Canary Routing** (A/B Testing) dựa trên HTTP Header mà không sửa code?
- Làm sao cấu hình **Timeout, Retry, Circuit Breaker** đồng nhất cho 4 ngôn ngữ (Python, Ruby, Java, Node.js)?
- Nếu code các logic mạng vào từng thư viện ứng dụng ➔ **Gánh nặng nhân bản code khổng lồ**.
- **Giải pháp Service Mesh**: Tách biệt hoàn toàn Logic Nghiệp vụ khỏi Logic Mạng Hạ tầng.

---

# SLIDE 2: KIẾN TRÚC 2 TẦNG CỦA ISTIO: CONTROL PLANE VS DATA PLANE

```text
┌────────────────────────────────────────────────────────┐
│              CONTROL PLANE: istiod                     │
│  - Pilot: Dịch cấu hình YAML thành xDS API cho Envoy   │
│  - Citadel: Certificate Authority cấp chứng chỉ mTLS   │
│  - Galley: Kiểm tra cú pháp và tính hợp lệ của CRD     │
└──────────────────────────┬─────────────────────────────┘
                           │ xDS gRPC API (Đẩy Config xuống Proxy)
┌──────────────────────────▼─────────────────────────────┐
│              DATA PLANE: Envoy Sidecars                │
│                                                        │
│  [ Pod: productpage ]             [ Pod: reviews ]     │
│  ┌─────────────────┐             ┌─────────────────┐   │
│  │ App (Python)    │             │ App (Java)      │   │
│  └───────▲─────────┘             └───────▲─────────┘   │
│          │ localhost                     │ localhost   │
│  ┌───────▼─────────┐   mTLS      ┌───────▼─────────┐   │
│  │ Envoy Proxy     │═════════════│ Envoy Proxy     │   │
│  │ (:15001/:15006) │ (SPIFFE ID) │ (:15001/:15006) │   │
│  └─────────────────┘             └─────────────────┘   │
└────────────────────────────────────────────────────────┘
```

---

# SLIDE 3: CƠ CHẾ INTERCEPT TRAFFIC QUA IPTABLES & SIDECAR INJECTION
*Làm sao Envoy proxy chặn bắt được toàn bộ traffic mà ứng dụng không hay biết?*

### 1. Cơ Chế Sidecar Injection Tự Động:
- Gán nhãn cho namespace: `kubectl label namespace default istio-injection=enabled`.
- Khi Pod được tạo, K8s Mutating Admission Webhook tự động chèn thêm container `istio-init` và `istio-proxy` (Envoy).

### 2. Ma Thuật của `istio-init` (iptables Rules):
- `istio-init` chạy với quyền `NET_ADMIN` trước khi app khởi động:
  - Chuyển hướng toàn bộ traffic **Inbound** (gửi đến Pod) vào cổng `:15006` của Envoy.
  - Chuyển hướng toàn bộ traffic **Outbound** (gửi đi khỏi Pod) vào cổng `:15001` của Envoy.
- Kết quả: Ứng dụng chỉ cần gửi HTTP thông thường, Envoy tự động mã hóa và định tuyến ở tầng dưới.

---

# SLIDE 4: BỘ BA CUSTOM RESOURCE DEFINITIONS (CRDS) CỐT LÕI
*3 Khái niệm trừu tượng nền tảng để điều khiển luồng trong Istio*

```text
[ Internet Client ]
       │ HTTP Port 80
       ▼
1. GATEWAY (bookinfo-gateway.yaml) ── Mở cổng biên Ingress tiếp nhận traffic
       │
       ▼
2. VIRTUALSERVICE (bookinfo / reviews) ── Định nghĩa luật định tuyến L7 (URI, Header, Weight)
       │
       ▼
3. DESTINATIONRULE (destination-rule-all.yaml) ── Định nghĩa Subsets (v1, v2, v3) & TLS Policy
       │
       ▼
[ Kubernetes Pods Target ]
```

---

# SLIDE 5: ISTIO INGRESS GATEWAY — ĐÓN TRAFFIC TẠI BIÊN CLUSTER
*Phân tích file `networking/bookinfo-gateway.yaml`*

### Cấu Hình Gateway:
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: bookinfo-gateway
spec:
  selector:
    istio: ingressgateway # Sử dụng Istio Ingress Gateway mặc định của cụm
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
```
- **So sánh với K8s Native Ingress**: Istio Gateway linh hoạt hơn gấp nhiều lần, tách biệt việc mở cổng mạng (`Gateway`) khỏi luật định tuyến (`VirtualService`), hỗ trợ quản lý đa giao thức L4–L7 và mTLS tại biên.

---

# SLIDE 6: CANARY ROUTING THEO HTTP HEADER NGƯỜI DÙNG
*Phân tích file `networking/virtual-service-reviews-test-v2.yaml`*

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason # Khớp chính xác user jason
      route:
      - destination:
          host: reviews
          subset: v2 # Định tuyến sang Pod v2 (Hiển thị Sao đen)
  - route:
    - destination:
        host: reviews
        subset: v1 # Khách vãng lai mặc định sang v1 (Không sao)
```
- **Ý nghĩa**: Code Java của `reviews` không cần sửa 1 dòng; việc phân loại người dùng được thực thi 100% tại tầng L7 Envoy proxy!

---

# SLIDE 7: PHÂN CHIA TẢI THEO TRỌNG SỐ (WEIGHTED TRAFFIC SHIFTING)
*Kỹ thuật triển khai phiên bản mới an toàn trên quy mô lớn*

### Chuyển Dịch Tải Dần Dần (Phát hành v3 Sao Đỏ):
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 50 # 50% traffic vào bản v1 ổn định
    - destination:
        host: reviews
        subset: v3
      weight: 50 # 50% traffic vào bản v3 thử nghiệm
```
- Cho phép đội ngũ SRE quan sát tỉ lệ lỗi và độ trễ của bản mới trước khi chuyển 100% traffic.

---

# SLIDE 8: CHAOS ENGINEERING & RESILIENCE — FAULT INJECTION
*Kiểm thử độ bền bỉ của hệ thống trước sự cố bất ngờ*

### Cấu Hình Tiêm Lỗi Trì Hoãn (`virtual-service-ratings-test-delay.yaml`):
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ratings
spec:
  hosts:
  - ratings
  http:
  - match:
    - headers:
        end-user: { exact: jason }
    fault:
      delay:
        percentage: { value: 100.0 }
        fixedDelay: 7s # Cố tình chèn độ trễ 7 giây vào ratings
    route:
    - destination: { host: ratings, subset: v1 }
```
- **Kết quả**: Khi `ratings` bị chậm 7s, client timeout kích hoạt, `reviews` hiển thị fallback text chứ web không bị sập ➔ **Chống Cascading Failure**.

---

# SLIDE 9: BẢO MẬT ZERO TRUST VỚI TRANSPARENT mTLS
*Mã hóa dữ liệu hai chiều tự động và định danh mật mã SPIFFE ID*

### 1. Nguyên Tắc Zero Trust:
- Mạng nội bộ cluster không an toàn; bất kỳ Pod nào cũng có thể bị thâm nhập.
- Mọi kết nối liên Pod bắt buộc phải được: **Xác thực**, **Ủy quyền** và **Mã hóa**.

### 2. Cơ Chế Hoạt Động của Istio mTLS:
1. **SPIFFE ID**: Mỗi service account được cấp danh tính duy nhất:  
   `spiffe://cluster.local/ns/default/sa/bookinfo-productpage`
2. **Cấp phát & Xoay vòng Chứng chỉ**: `istiod` đóng vai trò CA cấp phát chứng chỉ X.509 ngắn hạn qua cơ chế SDS (Secret Discovery Service).
3. **Mã hóa Trong Suốt (Transparent)**: Hai Envoy sidecar tự động bắt tay mTLS. Code Python, Ruby hay Java truyền plain HTTP nội bộ mà dữ liệu trên đường truyền vẫn được mã hóa 100%.
4. **`PeerAuthentication` STRICT**: Từ chối mọi kết nối plaintext không có sidecar.

---

# SLIDE 10: TỔNG KẾT & ARCHITECTURAL TRADE-OFFS CỦA ISTIO

### Bảng Đánh Đổi Kiến Trúc (Trade-offs):

| Lợi Thế Đạt Được | Chi Phí & Đánh Đổi Thực Tế | Giải Pháp Khắc Phục |
|---|---|---|
| **Zero Code Changes**: Không cần viết code mTLS, routing cho từng ngôn ngữ. | **Hop Latency Overhead**: Mỗi chặng mạng tăng thêm **+1.5 đến 3ms** qua 2 proxy. | Cân nhắc chuyển sang **Istio Ambient Mesh** (chia sẻ ztunnel ở tầng Node). |
| **Kiểm Soát Luồng L7 Tinh Tế**: Canary theo Header, chia tải % chính xác. | **Tài Nguyên Sidecar**: Mỗi Pod tốn thêm **30–50MB RAM** và CPU cho Envoy. | Tối ưu tài nguyên qua `Sidecar` CRD để giới hạn config xDS tải về. |
| **Bảo Mật Zero Trust Toàn Diện**: Tự động mã hóa mTLS 100% liên Pod. | **Độ Phức Tạp Vận Hành**: Khó debug sự cố mạng và xung đột iptables. | Sử dụng `istioctl analyze` và Distributed Tracing để chẩn đoán. |

---

## 🎙️ KỊCH BẢN THUYẾT TRÌNH 10 PHÚT — CHỦ ĐỀ ISTIO

- **[0:00 – 1:00] Slide 1 & 2**: *"Kính thưa Thầy/Cô, em là Tường, trình bày về Istio Service Mesh. Khi số lượng microservices tăng lên, việc viết code mTLS hay Canary cho 4 ngôn ngữ khác nhau là bất khả thi. Istio giải quyết bằng cách tách đôi: Control Plane `istiod` quản lý cấu hình và CA; Data Plane các Envoy sidecar chặn bắt traffic để thực thi mạng."*
- **[1:00 – 2:30] Slide 3 & 4**: *"Envoy được tự động tiêm vào Pod qua Webhook. Container `istio-init` dùng iptables điều hướng toàn bộ traffic Inbound cổng 15006 và Outbound cổng 15001 vào Envoy. Istio cung cấp bộ ba CRD: Gateway đón traffic biên, VirtualService định nghĩa luật L7, và DestinationRule định nghĩa các subsets."*
- **[2:30 – 4:00] Slide 5 & 6**: *(Mở file `virtual-service-reviews-test-v2.yaml`)*: *"Qua VirtualService, em thực hiện Canary Routing: khách vãng lai 100% vào `reviews:v1` (không sao); nhưng khi user đăng nhập là `jason`, Envoy phát hiện header `end-user: jason` và route sang `reviews:v2` (sao đen) mà code Java không cần sửa một dòng nào!"*
- **[4:00 – 5:30] Slide 7 & 8**: *(Mở file `virtual-service-ratings-test-delay.yaml`)*: *"Istio hỗ trợ chia tải theo trọng số 50/50 để thử nghiệm an toàn, và Fault Injection chèn delay 7 giây để kiểm thử khả năng chịu lỗi (Chaos Engineering), chứng minh cơ chế timeout chống sập dây chuyền."*
- **[5:30 – 6:30] Slide 9 & 10**: *"Về bảo mật, Istio thực thi Zero Trust qua Transparent mTLS với định danh SPIFFE ID và chế độ STRICT. Đánh đổi lớn nhất của Service Mesh là mỗi chặng mạng tăng thêm 1.5–3ms độ trễ và tốn 30–50MB RAM mỗi Pod, nhưng đem lại khả năng kiểm soát mạng và bảo mật vô song."*
- **[6:30 – 9:30] Live Demo**: Apply VirtualService Canary user `jason`, đăng nhập thấy sao đen, apply VirtualService chèn delay 7s kiểm chứng resilience.
- **[9:30 – 10:00] Kết bài & Vấn đáp**: Tuyên bố kết thúc bài thuyết trình Istio.

