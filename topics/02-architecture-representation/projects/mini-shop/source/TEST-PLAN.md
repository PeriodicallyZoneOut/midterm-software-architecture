# Kế hoạch kiểm thử chi tiết

## Môi trường và dữ liệu

Chạy `npm ci`, `npm run verify`; tích hợp/E2E yêu cầu stack Compose healthy. BASE_URL mặc định http://127.0.0.1:8080. Dữ liệu giả, sản phẩm test prefix `Test`; dùng UUID/key mới cho mỗi lần chạy. Không dùng production, không xóa volume. Chromium có sẵn trên máy hoặc đặt CHROMIUM_PATH. Các ca tự động nằm trong tests/ và scripts/verify-stack.sh.

## Unit — không cần database

| ID | Bước | Mong đợi |
|---|---|---|
| U01 | Giá 15000, SL 2 và giá 9000, SL 3 | Tổng 57000, subtotal đúng |
| U02 | SL 0, -1, 1.5, 100; 21 dòng; ID trùng; email sai | Validation fail |
| U03 | Đổi thứ tự item, thêm khoảng trắng tên | Canonical hash không đổi |
| U04 | Cùng key nhưng đổi SL | Hash thay đổi |
| U05 | Giá tối đa, 20 dòng x99 | Tổng là safe integer |

## API integration — qua gateway, database thật

| ID | Bước | Mong đợi |
|---|---|---|
| A01 | GET products | >=5 seed, JSON contract |
| A02 | Tạo/sửa sản phẩm, đọc lại | 201/200; dữ liệu đúng |
| A03 | Gửi giá âm/thập phân/unknown field, PATCH rỗng | 400, không ghi |
| A04 | Gửi đơn valid | 201, snapshot/tổng đúng |
| A05 | Đổi giá/tên sản phẩm rồi đọc đơn cũ | Snapshot không đổi |
| A06 | Gửi lại cùng key/body | 200, cùng ID |
| A07 | Cùng key/body khác | 409 |
| A08 | 6 yêu cầu đồng thời cùng key | Đúng một 201, còn lại 200, một ID |
| A09 | Product UUID không có/inactive | 404/409, tổng số đơn không tăng |
| A10 | SL sai, ID trùng, thiếu key, JSON hỏng, body quá lớn | 400 hoặc 413 |
| A11 | Pagination và ID không có | page/pageSize đúng; 404; pageSize>50 →400 |
| A12 | Public gọi /internal hoặc route lạ | 404; không lộ nội bộ |
| A13 | Header X-Request-Id | Trả lại ID hợp lệ qua gateway |
| A14 | Client gửi priceVnd trong item | 400, không tin giá client |

## Transaction failure injection — `npm run test:transaction`

| ID | Bước | Mong đợi |
|---|---|---|
| A15 | Trigger tạm chặn ghi item thứ hai của sản phẩm test riêng | API 500; số order và item không đổi, rollback cả item đầu |
| A16 | Gỡ trigger, gửi lại cùng key | 201, hai item, không bị giữ key do transaction thất bại |

Script chỉ tạo trigger tên UUID trong Orders DB của lab và gỡ trong finally; chạy tuần tự, không song song test khác.

## Browser E2E

| ID | Bước | Mong đợi |
|---|---|---|
| E01 | Vào catalog, search, thêm giỏ, reload | Cart được giữ |
| E02 | Nhập tên/email, tạo đơn | Chuyển detail, tổng và item đúng |
| E03 | Mở list và detail trực tiếp/reload | SPA routing đúng |
| E04 | Admin tạo/sửa/ẩn sản phẩm | UI và API đồng bộ |
| E05 | Viewport 390x844, điều hướng/cart | Không tràn ngang, controls truy cập được |
| E06 | Browser console/pageerror | Không có lỗi runtime |
| E07 | Mất response lần đầu sau commit, reload cart, gửi lại | Không sinh đơn trùng |

## Docker / failure / persistence

| ID | Bước | Mong đợi |
|---|---|---|
| D01 | compose config, up --build --wait | Sáu container healthy |
| D02 | Stop products; GET orders; POST order mới | Đọc đơn 200, tạo đơn 503 trong <8s |
| D03 | Start products; tạo đơn | 201; tự phục hồi |
| D04 | Restart orders-db, đợi healthy | Orders đọc/ghi được trở lại |
| D05 | Tạo đơn, down, up --wait; đọc ID cũ | Dữ liệu còn, seed không ghi đè |
| D06 | Build/up --no-deps products | Orders container ID/StartedAt không đổi |
| D07 | Kiểm tra networks/grants | User chỉ sở hữu DB mình; không publish DB host |
| D08 | Replay đơn đã tạo khi Products dừng | 200, không cần Products |

## Vòng sửa lỗi

1. Build/unit trước; sửa mọi lỗi rồi chạy lại nhóm liên quan.
2. Khởi động Compose, chạy API, sửa contract/transaction nếu fail.
3. Chạy browser, sửa UX/runtime và chạy lại.
4. Chạy fault/recovery/persistence/independent deployment.
5. Ghi lệnh, kết quả thật và giới hạn vào docs/VERIFICATION.md; không đánh dấu PASS cho ca chưa chạy.
