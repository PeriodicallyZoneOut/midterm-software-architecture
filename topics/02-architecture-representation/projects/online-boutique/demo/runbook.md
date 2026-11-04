# Runbook Triển khai & Kiểm chứng Kiến trúc — Online Boutique (`theanh-architecture`)

Runbook này hướng dẫn chi tiết từng bước khởi chạy, kiểm chứng 4+1 Views, kiểm tra cấu trúc dữ liệu Redis/Protobuf, diễn tập kịch bản lỗi (Fault Injection) và thu thập bằng chứng (`evidence/`) cho môi trường độc lập của **Thế Anh (`theanh-architecture`)** theo đúng quy định tại **Mục 5, Mục 9 & Mục 10 (`docs/TEAM-ASSIGNMENT.md`)**.

---

## 1. Thông tin Môi trường & Thư mục Làm việc

- **Working Directory:**
  ```powershell
  cd e:\KTPM\midterm-software-architecture\topics\02-architecture-representation\projects\online-boutique\source
  ```
- **Namespace Kubernetes độc lập (theo quy tắc Mục 9 `TEAM-ASSIGNMENT.md`):** `theanh-architecture`
- **Dependencies cần có trên máy:**
  1. **Docker Desktop** (đã bật **Enable Kubernetes** trong *Settings $\rightarrow$ Kubernetes*, hoặc dùng `minikube` / `kind`).
  2. **`kubectl`** CLI (đã đi kèm sẵn khi cài Docker Desktop).
- **Bảng Cổng (Port Mapping):**
  - Cổng truy cập trình duyệt trên máy host (qua `kubectl port-forward`): **`http://localhost:8088`** (dùng `8088` để tránh xung đột với cổng `8080` của Mini Shop hoặc các stack khác).
  - Các cổng nội bộ trong cụm Kubernetes (`ClusterIP`):
    - `frontend`: Service `80` $\rightarrow$ Pod `8080`
    - `productcatalogservice`: `3550`
    - `cartservice`: `7070`
    - `redis-cart`: `6379`
    - `currencyservice`: `7000`
    - `checkoutservice`: `5050`
    - `shippingservice`: `50051`
    - `paymentservice`: `50051`
    - `emailservice`: Service `5000` $\rightarrow$ Pod `8080`
    - `recommendationservice`: `8080`
    - `adservice`: `9555`

---

## 2. Khởi chạy & Kiểm tra Sẵn sàng (Deploy & Readiness Check)

### Bước 2.1: Tạo Namespace riêng và Triển khai Manifest chuẩn
```powershell
cd e:\KTPM\midterm-software-architecture\topics\02-architecture-representation\projects\online-boutique\source

# 1. Kiểm tra kết nối cụm Kubernetes
kubectl cluster-info
kubectl get nodes

# 2. Tạo namespace độc lập cho Thế Anh
kubectl create namespace theanh-architecture --dry-run=client -o yaml | kubectl apply -f -

# 3. Triển khai toàn bộ 12 Deployments + 12 Services vào namespace theanh-architecture
kubectl apply -n theanh-architecture -f release/kubernetes-manifests.yaml
```

### Bước 2.2: Theo dõi Trạng thái Sẵn sàng (Readiness Probes)
```powershell
# Chờ tất cả các Pod chuyển sang trạng thái Running (1/1 READY)
kubectl get pods -n theanh-architecture -w

# Kiểm tra danh sách Deployments, Services và Endpoints
kubectl get deployments,services,endpoints -n theanh-architecture -o wide
```
- **Kết quả kỳ vọng (Expected Result):**
  - 12 Pods (`adservice`, `cartservice`, `checkoutservice`, `currencyservice`, `emailservice`, `frontend`, `loadgenerator`, `paymentservice`, `productcatalogservice`, `recommendationservice`, `redis-cart`, `shippingservice`) đều đạt `READY 1/1` và `STATUS Running`.

### Bước 2.3: Mở cổng truy cập ứng dụng trên máy Host (`port-forward`)
Mở một cửa sổ PowerShell riêng để giữ kết nối cổng `8088`:
```powershell
kubectl port-forward -n theanh-architecture svc/frontend 8088:80
```
- Kiểm tra nhanh HTTP Healthz:
  ```powershell
  curl.exe -i http://localhost:8088/_healthz
  ```
  *(Kết quả kỳ vọng: `HTTP/1.1 200 OK`, nội dung `ok`).*

---

## 3. Kịch bản Demo 4+1 Views, Data Schema & Component Mapping (Live Demo)

### Kịch bản 1: Duyệt Sản phẩm & Quy đổi Tiền tệ (`Browse & Currency Conversion`)
1. Mở trình duyệt tại `http://localhost:8088` hoặc chạy lệnh:
   ```powershell
   curl.exe -i http://localhost:8088/product/OLJCESPC7Z
   ```
2. **Đối chiếu Code & Sơ đồ:**
   - Trình duyệt nhận Cookie `shop_session-id` (`src/frontend/middleware.go:103`).
   - `productHandler` (`src/frontend/handlers.go:144`) gọi `GetProduct(id="OLJCESPC7Z")` tới `productcatalogservice:3550` (`src/productcatalogservice/product_catalog.go:47`), trả về kính mát **Sunglasses** giá `$19.99`.

### Kịch bản 2: Thêm vào Giỏ hàng & Kiểm chứng Schema Nhị phân trong `redis-cart`
1. Thêm 2 chiếc kính mát (`OLJCESPC7Z`) vào giỏ hàng:
   ```powershell
   # Gửi POST /cart với một session cố định để kiểm chứng trực tiếp trong Redis
   curl.exe -i -X POST http://localhost:8088/cart `
     -H "Cookie: shop_session-id=theanh-demo-session-001" `
     -d "product_id=OLJCESPC7Z&quantity=2"
   ```
2. **Kiểm chứng trực tiếp Data Schema trong `redis-cart`:**
   ```powershell
   # Liệt kê các key đang lưu trong Redis
   kubectl exec -n theanh-architecture deploy/redis-cart -- redis-cli KEYS "*"

   # Xem kiểu dữ liệu và giá trị nhị phân Protobuf của key vừa tạo
   kubectl exec -n theanh-architecture deploy/redis-cart -- redis-cli GET "theanh-demo-session-001"
   ```
   - **Kết quả kỳ vọng:** Xuất hiện key `"theanh-demo-session-001"` chứa chuỗi byte Protobuf (`Hipstershop.Cart` gồm `user_id="theanh-demo-session-001"` và `CartItem {product_id="OLJCESPC7Z", quantity=2}` do `RedisCartStore.cs:60` ghi vào).

### Kịch bản 3: Đặt hàng (`PlaceOrder`) & Truy vết Log qua 6 Dịch vụ
1. Gửi yêu cầu đặt hàng cho session `theanh-demo-session-001`:
   ```powershell
   curl.exe -s -X POST http://localhost:8088/cart/checkout `
     -H "Cookie: shop_session-id=theanh-demo-session-001" `
     -d "email=theanh@example.com&street_address=268+Ly+Thuong+Kiet&zip_code=70000&city=HCM&state=HCM&country=Vietnam&credit_card_number=4388576018410707&credit_card_expiration_month=09&credit_card_expiration_year=2030&credit_card_cvv=123" | Select-String -Pattern "Order Confirmation|Tracking|Total Paid" -Context 2,2
   ```
2. **Kiểm tra Log xác nhận tại `checkoutservice`, `paymentservice`, `emailservice` và kiểm tra Redis:**
   ```powershell
   kubectl logs -n theanh-architecture deploy/checkoutservice --tail=20
   kubectl logs -n theanh-architecture deploy/paymentservice --tail=10
   kubectl logs -n theanh-architecture deploy/emailservice --tail=10

   # Kiểm tra lại giỏ hàng trong Redis đã được làm rỗng (EmptyCart)
   kubectl exec -n theanh-architecture deploy/redis-cart -- redis-cli GET "theanh-demo-session-001"
   ```
   - **Kết quả kỳ vọng:**
     - `checkoutservice` in log `[PlaceOrder] user_id="theanh-demo-session-001"`, `payment went through (transaction_id: ...)` và `order confirmation email sent to "theanh@example.com"`.
     - `paymentservice` in log `Transaction processed: visa ending 0707`.
     - `emailservice` (`DummyEmailService`) in log `A request to send order confirmation email to theanh@example.com has been received.`

---

## 4. Kịch bản Diễn tập Lỗi & Khôi phục (Fault Injection & Recovery)

### 4.1. Lỗi Dịch vụ Phụ trợ (`adservice` tắt $\rightarrow$ Hệ thống vẫn hoạt động bình thường)
```powershell
# 1. Tắt adservice
kubectl scale deployment/adservice -n theanh-architecture --replicas=0

# 2. Kiểm tra lại trang sản phẩm -> Vẫn trả về HTTP 200 OK nhờ timeout 100ms + bắt lỗi ở rpc.go:169-180
curl.exe -I http://localhost:8088/product/OLJCESPC7Z

# 3. Khôi phục lại adservice
kubectl scale deployment/adservice -n theanh-architecture --replicas=1
```

### 4.2. Lỗi Dịch vụ Cốt lõi (`redis-cart` tắt $\rightarrow$ Báo lỗi `HTTP 500`, khôi phục khi bật lại)
```powershell
# 1. Tắt redis-cart
kubectl scale deployment/redis-cart -n theanh-architecture --replicas=0

# 2. Thử xem giỏ hàng -> Trả về HTTP 500 Internal Server Error do RedisCartStore.cs ném RpcException(FailedPrecondition)
curl.exe -i http://localhost:8088/cart -H "Cookie: shop_session-id=theanh-demo-session-001"

# 3. Khôi phục lại redis-cart và chờ Ready
kubectl scale deployment/redis-cart -n theanh-architecture --replicas=1
kubectl wait --for=condition=available deployment/redis-cart -n theanh-architecture --timeout=60s

# 4. Kiểm tra lại -> Trả về HTTP 200 OK bình thường
curl.exe -I http://localhost:8088/cart
```

---

## 5. Dừng Hệ thống & Dọn dẹp

- **Tạm dừng `loadgenerator` để tiết kiệm CPU khi không test tải:**
  ```powershell
  kubectl scale deployment/loadgenerator -n theanh-architecture --replicas=0
  ```
- **Xóa toàn bộ stack sau khi hoàn tất buổi bảo vệ:**
  ```powershell
  kubectl delete namespace theanh-architecture
  ```
