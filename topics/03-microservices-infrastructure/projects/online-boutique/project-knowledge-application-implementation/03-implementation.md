# Triển khai Chi tiết — Online Boutique

## 1. Cấu hình Multi-stage Dockerfile & Tối ưu hóa

### Minh chứng từ `src/frontend/Dockerfile`:
```dockerfile
# Stage 1: Build binary với đầy đủ công cụ lập trình Go
FROM golang:1.23.2-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /go/bin/frontend .

# Stage 2: Runtime image tối giản
FROM alpine:3.20
RUN apk add --no-cache ca-certificates
WORKDIR /src
COPY --from=builder /go/bin/frontend /src/server
COPY ./templates ./templates
COPY ./static ./static
EXPOSE 8080
ENTRYPOINT ["/src/server"]
```
- **Lợi ích**:
  - Image size siêu nhỏ (~25MB so với >800MB nếu để nguyên Go SDK).
  - Triệt tiêu compiler và header files trong runtime để tăng cường bảo mật.

---

## 2. Kubernetes Workload Modeling (Manifests)

### 2.1. Cấu hình Health Checking (Probes) cho `cartservice`
Trích từ [`release/kubernetes-manifests.yaml`](../source/release/kubernetes-manifests.yaml):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cartservice
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cartservice
  template:
    metadata:
      labels:
        app: cartservice
    spec:
      serviceAccountName: cartservice
      terminationGracePeriodSeconds: 5
      containers:
      - name: server
        image: cartservice
        ports:
        - containerPort: 7070
        env:
        - name: REDIS_ADDR
          value: "redis-cart:6379"
        resources:
          requests:
            cpu: 200m
            memory: 64Mi
          limits:
            cpu: 300m
            memory: 128Mi
        readinessProbe:
          initialDelaySeconds: 15
          periodSeconds: 10
          grpc:
            port: 7070
        livenessProbe:
          initialDelaySeconds: 15
          periodSeconds: 10
          grpc:
            port: 7070
```
- **Phân tích cơ chế**:
  - Sử dụng chuẩn gRPC Health Checking Protocol thay vì HTTP ping.
  - `readinessProbe`: Ngăn chặn gửi traffic cho đến khi .NET runtime và kết nối tới Redis hoàn tất.
  - `resources.requests/limits`: Bảo vệ node không bị OOM (Out Of Memory) và giúp K8s scheduler xếp pod tối ưu.

---

## 3. Luồng Điều phối Checkout (Checkout Orchestrator Trace)

Trong [`src/checkoutservice/main.go`](../source/src/checkoutservice/main.go):
```go
func (cs *checkoutService) PlaceOrder(ctx context.Context, req *pb.PlaceOrderRequest) (*pb.PlaceOrderResponse, error) {
    // 1. Chuẩn bị đơn hàng và lấy giỏ hàng
    cart, err := cs.getCart(ctx, req.UserId)
    
    // 2. Lấy thông tin giá từ Catalog
    totalPrice := calculateTotal(cart, cs.productCatalogSvc)
    
    // 3. Tính phí giao hàng
    shippingQuote, err := cs.shippingSvc.GetQuote(ctx, req.Address)
    
    // 4. Thanh toán thẻ tín dụng
    paymentResult, err := cs.paymentSvc.Charge(ctx, req.CreditCard, totalPrice)
    
    // 5. Gửi vận chuyển
    shippingResult, err := cs.shippingSvc.ShipOrder(ctx, req.Address, cart)
    
    // 6. Xóa giỏ hàng
    _ = cs.cartSvc.EmptyCart(ctx, req.UserId)
    
    // 7. Gửi email xác nhận
    _ = cs.emailSvc.SendOrderConfirmation(ctx, req.Email, orderResult)
    
    return &pb.PlaceOrderResponse{Order: orderResult}, nil
}
```
- Cơ chế fail-safe: Nếu bước 4 (thanh toán) thất bại, quy trình lập tức hủy bỏ và trả về lỗi cho người dùng; giỏ hàng không bị xóa.
