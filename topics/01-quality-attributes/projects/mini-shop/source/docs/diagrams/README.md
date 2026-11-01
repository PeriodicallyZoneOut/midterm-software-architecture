# Sơ đồ dataflow Mini Shop

Mở [trang HTML offline](../dataflows.html) để xem mục lục, phóng to, tải từng SVG hoặc in. [DATAFLOWS.md](../DATAFLOWS.md) là nguồn chính, có sơ đồ Mermaid, bảng ownership và liên kết code.

| File | Nội dung |
|---|---|
| flow-00.svg | Tổng quan Gateway, services, DB, network và volume |
| flow-01.svg | Catalog và tìm kiếm |
| flow-02.svg | Giỏ hàng và localStorage |
| flow-03.svg | Tạo sản phẩm |
| flow-04.svg | Sửa sản phẩm và ngừng bán |
| flow-05.svg | Checkout thành công, resolve giá, transaction |
| flow-06.svg | Danh sách đơn và phân trang |
| flow-07.svg | Chi tiết đơn, snapshot |
| flow-08.svg | Mất response và idempotency replay |
| flow-09.svg | Request đồng thời cùng key |
| flow-10.svg | Lỗi Products, sản phẩm thiếu hoặc ngừng bán |
| flow-11.svg | Rollback khi lỗi ghi item |
| flow-12.svg | Healthcheck/readiness |

Mỗi SVG có file `.mmd` tương ứng. SVG là vector, có thể đưa vào slide hoặc xuất PNG bằng trình soạn thảo ảnh vector. HTML chứa sẵn toàn bộ SVG, không tải thư viện từ CDN lúc mở.

## Tái xuất sau khi sửa source

Chạy từ thư mục `lab-01`, đã `npm ci` và có Chromium. Công cụ Mermaid đặt trong `/tmp` để không thay dependency ứng dụng:

```bash
npm install --prefix /tmp/lab01-diagram-renderer mermaid
printf "import mermaid from 'mermaid'; window.mermaid = mermaid;\n" > /tmp/lab01-diagram-renderer/entry.js
./node_modules/.bin/esbuild /tmp/lab01-diagram-renderer/entry.js --bundle --format=iife --outfile=/tmp/lab01-diagram-renderer/bundle.js
node scripts/render-dataflows.mjs
```

Có thể đặt `MERMAID_BUNDLE` và `CHROMIUM_PATH` để đổi đường dẫn. Script parse/render từng sơ đồ, xác nhận đủ 13 SVG trong HTML, kiểm tra điều khiển zoom và lưu ảnh preview. Nếu chạy trong môi trường sandbox không cho Chromium khởi động, cần quyền chạy browser ngoài sandbox.
