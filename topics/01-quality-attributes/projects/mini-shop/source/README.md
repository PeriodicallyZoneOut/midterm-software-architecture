# Mini Shop · Lab 01

Demo microservices local: React/TypeScript → Nginx → API Gateway → Products và Orders → hai MariaDB độc lập.

- [Sơ đồ dataflow: HTML offline](docs/dataflows.html) · [Mermaid và giải thích](docs/DATAFLOWS.md)
- [Mô hình kiến trúc C4 (Context, Container, Component, Code)](docs/C4-MODELS.md)
- [Spec chi tiết](SPEC.md)
- [Checklist phát triển](TASKS.md)
- [Kế hoạch kiểm thử](TEST-PLAN.md)
- [Kết quả kiểm chứng](docs/VERIFICATION.md)

## Chạy bằng Docker

Yêu cầu Docker Engine đang chạy và Docker Compose v2 trở lên. Không cần Node/MariaDB trên host để chạy toàn bộ stack. Docker cần Internet ở lần đầu để tải image và npm dependencies.

```bash
cd lab-01
cp .env.example .env  # chỉ lần đầu; giữ .env đang có
# Thay giá trị demo nếu dùng môi trường khác.
docker compose up --build -d --wait
```

Mở **http://localhost:8080**. Trên máy hiện tại, dùng `sudo docker compose ...` trong terminal nếu tài khoản chưa có quyền Docker. Agent có thể dùng `pkexec docker compose ...` để xác thực qua hộp thoại.

Database được khởi tạo và thêm 5 sản phẩm mẫu tự động. Database host đã cài không bị sử dụng hoặc thay đổi. Chỉ cổng web 8080 được mở trên loopback. `.env` không đưa vào Git. Giá trị ví dụ là mật khẩu demo local, chưa có xác thực cho trang quản trị.

```bash
docker compose ps
docker compose logs -f products orders gateway
docker compose down        # giữ dữ liệu trong volume
docker compose up -d --wait # khôi phục
```

Không thêm `-v` vào `down` trừ khi chủ động muốn xóa toàn bộ database của lab.

## Kiểm thử

Node 24+ và Chromium phục vụ kiểm thử trên host; dependency được cố định bằng package-lock.json.

```bash
npm ci
npm run verify      # build 4 workspace và 5 unit test
npm run test:api    # integration qua Nginx/Gateway + MariaDB thật
npm run test:e2e    # Chromium: desktop/mobile, checkout, admin, retry
npm run test:transaction # inject lỗi item thứ hai, kiểm tra rollback
npm run test:stack  # Docker: lỗi, recovery, persistence, deploy riêng
```

`test:api`, `test:e2e`, `test:transaction`, `test:stack` chạy tuần tự trên stack đang healthy, không chạy cùng lúc vì kiểm thử stack tạm dừng service. Các test tạo dữ liệu giả có tiền tố Test; không xóa dữ liệu người dùng. Test trình duyệt lưu ảnh trong `docs/screenshots` và báo cáo trong `playwright-report`.

Nếu Chromium không ở `/usr/bin/chromium`, đặt `CHROMIUM_PATH=/đường/dẫn/chromium`. Nếu đổi cổng `.env`, đặt `BASE_URL=http://127.0.0.1:CỔNG` cho test.

Trên Omarchy khi cần quyền Docker:

```bash
DOCKER_PRIVILEGE=pkexec npm run test:transaction
DOCKER_PRIVILEGE=pkexec npm run test:stack
```

Script chỉ thao tác Compose project `lab01-mini-shop`, có `finally` đưa stack về trạng thái chạy. Không chạy trong lúc đang trình bày demo vì có bước down/up ngắn.

## Kịch bản trình bày 5–7 phút

1. Mở catalog, thêm sản phẩm, tạo đơn; mở chi tiết đơn.
2. Vào Quản lý, đổi giá sản phẩm. Mở đơn cũ để thấy snapshot giữ nguyên.
3. Chạy `docker compose stop products`. Xem đơn cũ vẫn được; tạo đơn mới báo lỗi hữu hạn.
4. Chạy `docker compose start products`. Chờ healthcheck, thử tạo đơn lại.
5. Chạy `docker compose up -d --build --no-deps --wait products`: chỉ Products được deploy, Orders không restart.
6. Xem `docker compose logs orders products gateway`: cùng requestId được truyền qua các service.

## Source và ownership

```text
frontend/             React SPA, CSS, Nginx, frontend Dockerfile
services/gateway/     định tuyến public, requestId, timeout
services/products/    sản phẩm, internal resolve, schema và seed
services/orders/      đơn hàng, snapshot, idempotency, transaction
scripts/              kiểm chứng lifecycle Docker
tests/                unit, API, browser
compose.yaml          sáu container, ba network, hai volume
Dockerfile            backend multi-stage, SERVICE build arg
```

Mỗi backend có package và tsconfig riêng. Các helper HTTP/DB nhỏ được đặt trong từng service để không phụ thuộc runtime vào package nội bộ dùng chung. Schema v1 trong bootstrap chỉ tạo nếu chưa có; cập nhật schema trong bài mở rộng cần migration có version mới.

## Hạn chế có chủ đích

- Demo local, không auth, không thanh toán/tồn kho, chưa triển khai production.
- HTTP đồng bộ; chưa cần Saga/broker vì mỗi đơn chỉ ghi vào một database.
- Hai database container cùng máy không phải high availability.
- Product list không phân trang; order list có phân trang; danh sách admin có thể dài sau nhiều lần test.
- Giá được chốt tại bước Products trả lời resolve; chưa có cơ chế báo giá giữ giá trong thời gian nhất định.
- Idempotency key không có TTL; cần chính sách retention nếu vận hành dài hạn.
- Tag image khóa major/minor; chưa khóa digest. CSS dùng Google Fonts với fallback sans-serif khi offline.
- API integration và browser test không thay thế load test hoặc security review.

## Troubleshooting

- `permission denied docker.sock`: dùng `sudo docker ...`; không cần đổi quyền socket.
- Cổng 8080 bận: sửa WEB_PORT trong `.env`, chạy lại Compose.
- API 503: xem `docker compose ps` và logs; đợi database/service healthy.
- Đổi mật khẩu `.env` sau khi đã có volume không tự đổi password DB hiện hữu; cần đổi user password trong DB tương ứng.
- Docker pull chậm: lần đầu cần tải image, các lần sau dùng cache. Không cần cài Kubernetes.
