# Kiểm chứng & Đánh giá Đánh đổi — Online Boutique

## 1. Phương pháp & Kịch bản kiểm chứng thực tế

| Kịch bản kiểm nghiệm | Thao tác thực hiện | Kỳ vọng (Expected Result) | Kết quả kiểm chứng thực tế |
|---|---|---|---|
| **Kịch bản 1: Luồng nghiệp vụ End-to-end** | Duyệt trang chủ -> Xem chi tiết mặt hàng -> Add to Cart -> Nhấn 'Place Order' | Giao dịch hoàn tất, trả về Order ID, giỏ hàng được làm rỗng | Passed: HTTP 200, hiển thị xác nhận đơn hàng, `cartservice` xóa sạch key session trong Redis |
| **Kịch bản 2: Pod Self-healing & Resiliency** | Thực thi lệnh xóa pod `kubectl delete pod -l app=cartservice` khi đang lướt web | Kubernetes ReplicaSet phát hiện và tạo ngay pod mới; người dùng refresh trang không bị crash | Passed: Pod mới ở trạng thái Running sau 2s; session giỏ hàng trong Redis vẫn nguyên vẹn |
| **Kịch bản 3: Downstream Service Failure** | Scale `paymentservice` về 0 replicas (`kubectl scale deployment paymentservice --replicas=0`) | Người dùng ấn Checkout bị báo lỗi thanh toán, nhưng giỏ hàng KHÔNG bị xóa | Passed: `checkoutservice` nhận mã lỗi gRPC `Unavailable`, hủy transaction và bảo toàn giỏ hàng |

---

## 2. Phân tích Đánh đổi Kiến trúc (Architectural Trade-offs)

```text
               Scalability & Tech Agility (Ưu điểm)
                          ▲
                          │
          [Kiến trúc Microservices Online Boutique]
                          │
                          ▼
            Cascading Latency & Ops Complexity (Chi phí)
```

1. **Về Khả năng mở rộng (Scalability)**:
   - *Đạt được*: Cho phép mở rộng có chọn lọc. Ví dụ `frontend` là điểm nhận toàn bộ traffic từ web browser có thể tăng lên nhiều pod mà không cần tăng các backend tính toán như `currencyservice`.
   - *Đánh đổi*: Cần thiết lập tài nguyên requests/limits cẩn thận để tránh contention trên Kubernetes node.

2. **Về Tính chịu lỗi (Fault Tolerance)**:
   - *Đạt được*: Sự cố ở các tính năng phụ như Banner quảng cáo (`adservice`) hoặc Gợi ý sản phẩm (`recommendationservice`) không làm tê liệt quá trình thanh toán chính.
   - *Đánh đổi*: Nếu `checkoutservice` hoặc `cartservice` gặp sự cố, trải nghiệm mua sắm bị ngưng trệ hoàn toàn (Single Point of Business Bottleneck).

3. **Về Độ trễ mạng (Network Overhead)**:
   - *Đạt được*: Code base tách biệt, interface Protobuf gọn gàng, contract độc lập.
   - *Đánh đổi*: So với Monolith (gọi hàm trực tiếp in-memory ~nanoseconds), chuỗi 7 gRPC calls cộng thêm độ trễ TCP/IP và serialization mất từ 15ms đến 60ms cho mỗi lượt checkout.
