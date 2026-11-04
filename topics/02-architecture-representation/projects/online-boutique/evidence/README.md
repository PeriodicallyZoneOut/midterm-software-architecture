# Evidence — Online Boutique (Architecture Representation)

Thư mục này dùng để lưu trữ bằng chứng chạy thực tế (runtime logs, trạng thái Kubernetes Pods/Services, kết quả kiểm tra Redis Protobuf key-value, và log kịch bản lỗi/khôi phục) trên môi trường của **Thế Anh (`theanh-architecture`)**.

## Danh mục File Bằng chứng Cần Thu thập (Chạy một lệnh duy nhất bên dưới khi bật Docker/Kubernetes)

| Tên file Evidence | Nội dung chứng minh | Lệnh tạo tương ứng |
| :--- | :--- | :--- |
| `01-k8s-workloads-and-services.txt` | Chứng minh 12 Deployments, Pods và 12 Services đã chạy `READY 1/1` trong namespace `theanh-architecture` (Physical/Deployment View). | `kubectl get deploy,po,svc,ep -n theanh-architecture -o wide` |
| `02-browse-and-cart-redis.txt` | Chứng minh luồng Browse sản phẩm, Add-to-Cart và cấu trúc lưu trữ key-value nhị phân Protobuf trong `redis-cart` (Process View & Data Model). | `curl /product/OLJCESPC7Z`, `POST /cart`, và `redis-cli KEYS "*" / GET` |
| `03-checkout-orchestration-logs.txt` | Chứng minh luồng `PlaceOrder()` đi qua `checkoutservice`, `paymentservice`, `shippingservice`, `emailservice` (Process View & Logical View). | `POST /cart/checkout` kèm `kubectl logs` của 3 services |
| `04-fault-injection-and-recovery.txt` | Chứng minh sự khác biệt giữa lỗi dịch vụ phụ trợ (`adservice` tắt $\rightarrow$ `HTTP 200`) và lỗi dịch vụ cốt lõi (`redis-cart` tắt $\rightarrow$ `HTTP 500` rồi khôi phục `HTTP 200`). | `kubectl scale` + `curl` kiểm chứng trước/trong/sau lỗi |

## Script Thu thập Tự động Toàn bộ Evidence

Khi đã bật Kubernetes trong Docker Desktop và chạy `kubectl apply -n theanh-architecture -f release/kubernetes-manifests.yaml` cùng `kubectl port-forward -n theanh-architecture svc/frontend 8088:80`, chạy đoạn lệnh sau để tự động xuất đủ 4 file vào thư mục này:

```powershell
$evDir = "e:\KTPM\midterm-software-architecture\topics\02-architecture-representation\projects\online-boutique\evidence"

# 1. Trạng thái Workloads & Services
kubectl get deploy,po,svc,ep -n theanh-architecture -o wide > "$evDir\01-k8s-workloads-and-services.txt"

# 2. Luồng Browse, Add-to-Cart & Redis Schema
curl.exe -i http://localhost:8088/product/OLJCESPC7Z > "$evDir\02-browse-and-cart-redis.txt"
curl.exe -i -X POST http://localhost:8088/cart -H "Cookie: shop_session-id=theanh-session-01" -d "product_id=OLJCESPC7Z&quantity=2" >> "$evDir\02-browse-and-cart-redis.txt"
kubectl exec -n theanh-architecture deploy/redis-cart -- redis-cli KEYS "*" >> "$evDir\02-browse-and-cart-redis.txt"
kubectl exec -n theanh-architecture deploy/redis-cart -- redis-cli GET "theanh-session-01" >> "$evDir\02-browse-and-cart-redis.txt"

# 3. Luồng Checkout Orchestration
curl.exe -i -X POST http://localhost:8088/cart/checkout -H "Cookie: shop_session-id=theanh-session-01" -d "email=theanh@example.com&street_address=268+Ly+Thuong+Kiet&zip_code=70000&city=HCM&state=HCM&country=Vietnam&credit_card_number=4388576018410707&credit_card_expiration_month=09&credit_card_expiration_year=2030&credit_card_cvv=123" > "$evDir\03-checkout-orchestration-logs.txt"
kubectl logs -n theanh-architecture deploy/checkoutservice --tail=25 >> "$evDir\03-checkout-orchestration-logs.txt"
kubectl logs -n theanh-architecture deploy/paymentservice --tail=15 >> "$evDir\03-checkout-orchestration-logs.txt"
kubectl logs -n theanh-architecture deploy/emailservice --tail=15 >> "$evDir\03-checkout-orchestration-logs.txt"

# 4. Fault Injection & Recovery
kubectl scale deploy/adservice -n theanh-architecture --replicas=0
curl.exe -I http://localhost:8088/product/OLJCESPC7Z > "$evDir\04-fault-injection-and-recovery.txt"
kubectl scale deploy/adservice -n theanh-architecture --replicas=1
kubectl scale deploy/redis-cart -n theanh-architecture --replicas=0
Start-Sleep -Seconds 3
curl.exe -i http://localhost:8088/cart -H "Cookie: shop_session-id=theanh-session-01" >> "$evDir\04-fault-injection-and-recovery.txt"
kubectl scale deploy/redis-cart -n theanh-architecture --replicas=1
kubectl wait --for=condition=available deploy/redis-cart -n theanh-architecture --timeout=60s
curl.exe -I http://localhost:8088/cart >> "$evDir\04-fault-injection-and-recovery.txt"
```
