# Mapping Thành phần — Online Boutique

## Bảng ánh xạ tổng thể từ Nghiệp vụ -> Source Code -> Kubernetes Resource

| Dịch vụ (Microservice) | Ngôn ngữ / Runtime | Trách nhiệm nghiệp vụ | State / Storage | Source Code chính | Kubernetes Deployment & Service |
|---|---|---|---|---|---|
| **frontend** | Go 1.23 | Đón HTTP traffic từ Browser, render HTML templates, proxy request đến các backend gRPC | Stateless | [`src/frontend/main.go`](../source/src/frontend/main.go), [`src/frontend/handlers.go`](../source/src/frontend/handlers.go) | `deployment/frontend`, `service/frontend` (Port 80 -> 8080) |
| **cartservice** | C# (.NET 8) | Quản lý giỏ hàng của từng session người dùng (thêm, sửa, xóa, lấy giỏ hàng) | Stateful qua Redis | [`src/cartservice/src/cartstore/`](../source/src/cartservice/src/cartstore/), [`src/cartservice/src/Program.cs`](../source/src/cartservice/src/Program.cs) | `deployment/cartservice`, `service/cartservice` (Port 7070) |
| **redis-cart** | Redis Alpine | In-memory key-value store lưu session giỏ hàng | Stateful (Volume/RAM) | Image chuẩn: `redis:alpine` | `deployment/redis-cart`, `service/redis-cart` (Port 6379) |
| **productcatalogservice** | Go 1.23 | Cung cấp danh mục sản phẩm, tìm kiếm, lấy chi tiết đơn giá | Stateless (Đọc file `products.json` lúc khởi động) | [`src/productcatalogservice/main.go`](../source/src/productcatalogservice/main.go), [`src/productcatalogservice/products.json`](../source/src/productcatalogservice/products.json) | `deployment/productcatalogservice`, `service/productcatalogservice` (Port 3550) |
| **currencyservice** | Node.js 20 | Chuyển đổi tỉ giá tiền tệ giữa các quốc gia | Stateless | [`src/currencyservice/server.js`](../source/src/currencyservice/server.js), [`src/currencyservice/data/currency_conversion.json`](../source/src/currencyservice/data/currency_conversion.json) | `deployment/currencyservice`, `service/currencyservice` (Port 7000) |
| **paymentservice** | Node.js 20 | Xác thực thẻ tín dụng và trừ tiền (Mock service) | Stateless | [`src/paymentservice/server.js`](../source/src/paymentservice/server.js), [`src/paymentservice/charge.js`](../source/src/paymentservice/charge.js) | `deployment/paymentservice`, `service/paymentservice` (Port 50051) |
| **shippingservice** | Go 1.23 | Tính phí giao hàng và sinh mã vận đơn tracking (Mock service) | Stateless | [`src/shippingservice/main.go`](../source/src/shippingservice/main.go), [`src/shippingservice/shippingservice.go`](../source/src/shippingservice/shippingservice.go) | `deployment/shippingservice`, `service/shippingservice` (Port 50051) |
| **emailservice** | Python 3.11 | Soạn và gửi email xác nhận đơn hàng sau khi checkout (Mock service) | Stateless | [`src/emailservice/email_server.py`](../source/src/emailservice/email_server.py) | `deployment/emailservice`, `service/emailservice` (Port 5000) |
| **checkoutservice** | Go 1.23 | **Orchestrator**: Điều phối toàn bộ luồng thanh toán, liên kết giỏ hàng, danh mục, thanh toán, vận chuyển và gửi email | Stateless (Workflow state in-memory) | [`src/checkoutservice/main.go`](../source/src/checkoutservice/main.go), [`src/checkoutservice/processor.go`](../source/src/checkoutservice/processor.go) | `deployment/checkoutservice`, `service/checkoutservice` (Port 5050) |
| **recommendationservice** | Python 3.11 | Gợi ý sản phẩm liên quan dựa trên các item trong giỏ hàng | Stateless | [`src/recommendationservice/recommendation_server.py`](../source/src/recommendationservice/recommendation_server.py) | `deployment/recommendationservice`, `service/recommendationservice` (Port 8080) |
| **adservice** | Java 21 | Cung cấp banner quảng cáo theo ngữ cảnh | Stateless | [`src/adservice/src/main/java/hipstershop/AdService.java`](../source/src/adservice/src/main/java/hipstershop/AdService.java) | `deployment/adservice`, `service/adservice` (Port 9555) |
| **loadgenerator** | Python / Locust | Sinh tải giả lập người dùng duyệt web, mua hàng | Tool / Worker | [`src/loadgenerator/locustfile.py`](../source/src/loadgenerator/locustfile.py) | `deployment/loadgenerator` (Gửi traffic trực tiếp tới `frontend:80`) |

---

## Chi tiết gRPC Interface Contracts (`protos/demo.proto`)

- `CartService`:
  - `AddItem(AddItemRequest) returns (Empty)`
  - `GetCart(GetCartRequest) returns (Cart)`
  - `EmptyCart(EmptyCartRequest) returns (Empty)`
- `ProductCatalogService`:
  - `ListProducts(Empty) returns (ListProductsResponse)`
  - `GetProduct(GetProductRequest) returns (Product)`
  - `SearchProducts(SearchProductsRequest) returns (SearchProductsResponse)`
- `CheckoutService`:
  - `PlaceOrder(PlaceOrderRequest) returns (PlaceOrderResponse)`
- `PaymentService`:
  - `Charge(ChargeRequest) returns (ChargeResponse)`
- `ShippingService`:
  - `GetQuote(GetQuoteRequest) returns (GetQuoteResponse)`
  - `ShipOrder(ShipOrderRequest) returns (ShipOrderResponse)`
- `CurrencyService`:
  - `GetSupportedCurrencies(Empty) returns (GetSupportedCurrenciesResponse)`
  - `Convert(CurrencyConversionRequest) returns (Money)`
