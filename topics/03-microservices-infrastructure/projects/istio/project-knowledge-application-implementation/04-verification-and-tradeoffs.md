# Kiểm chứng & Đánh giá Đánh đổi — Istio

## 1. Phương pháp & Kịch bản kiểm chứng thực tế

| Kịch bản kiểm nghiệm | Thao tác thực hiện | Kỳ vọng (Expected Result) | Kết quả kiểm chứng thực tế |
|---|---|---|---|
| **Kịch bản 1: Sidecar Injection & Pod Readiness** | Deploy một workload vào namespace có nhãn `istio-injection=enabled` | Pod khởi động thành công với trạng thái `2/2 Running` (app + istio-proxy) | Passed: Kiểm tra `kubectl get pod` thấy 2/2 ready; container `istio-proxy` nhận port 15090 và 15001 |
| **Kịch bản 2: Kiểm chứng mã hóa mTLS** | Kiểm tra trạng thái mã hóa thông qua lệnh `istioctl x describe pod <pod-name>` | Xác nhận kết nối giữa các Pod được mã hóa mTLS thông qua chứng chỉ SPIFFE | Passed: Output báo `mTLS: STRICT` và `Cert: valid` |
| **Kịch bản 3: Telemetry Pipeline & Dashboard** | Gửi HTTP traffic vào ứng dụng liên tục và quan sát Grafana UI | Dashboard cập nhật tức thì lưu lượng RPS, độ trễ p50/p90/p99 và tỉ lệ thành công 200 OK | Passed: Grafana panel `Global Request Volume` và `Success Rate` hiển thị dữ liệu khớp 100% với lượng request phát ra |

---

## 2. Phân tích Đánh đổi Kiến trúc (Architectural Trade-offs)

```text
                  Zero Trust & L7 Observability (Ưu điểm)
                                    ▲
                                    │
                     [Istio Service Mesh Architecture]
                                    │
                                    ▼
                Sidecar Resource Overhead & Hop Latency (Chi phí)
```

1. **Về Khả năng Vận hành & Observability**:
   - *Đạt được*: Không cần các đội phát triển sửa đổi code để gắn thư viện metrics hay tracing. Mọi microservice tự động có metrics chuẩn mực.
   - *Đánh đổi*: Nếu cấu hình sai VirtualService hoặc DestinationRule, toàn bộ traffic của một cụm dịch vụ có thể bị rớt xuống lỗ đen (Blackhole), việc debug đòi hỏi đọc Envoy access log chuyên sâu.

2. **Về Tài nguyên & Chi phí Hạ tầng**:
   - *Đạt được*: Bảo vệ an ninh tuyệt đối, phân quyền Zero Trust chặt chẽ.
   - *Đánh đổi*: Tiêu tốn thêm từ 15% đến 25% lượng RAM toàn cụm do mỗi Pod phải chạy thêm container Envoy proxy.

3. **Về Độ trễ (Latency)**:
   - *Đạt được*: Thống nhất cơ chế timeout, retry và load balancing trên tầng hạ tầng.
   - *Đánh đổi*: Mỗi bước nhảy mạng (Hop) tăng thêm từ 1.5ms đến 3ms do việc phân tích gói tin L7 và mã hóa/giải mã TLS liên tục tại hai đầu Envoy proxy.
