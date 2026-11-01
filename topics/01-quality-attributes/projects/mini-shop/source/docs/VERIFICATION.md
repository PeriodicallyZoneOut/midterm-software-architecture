# Kết quả implement / test / verify

Ngày chạy: 2026-10-01, trên Omarchy. App dùng database Docker riêng; không thay đổi dữ liệu MariaDB trên host.

## Kết quả thực tế

| Nhóm | Kết quả | Bằng chứng |
|---|---|---|
| Build | PASS, frontend + 3 backend TypeScript strict | [build-unit-verification.log](build-unit-verification.log) |
| Unit | PASS 5/5 | [build-unit-verification.log](build-unit-verification.log), U01–U05 |
| API integration | PASS 14 subtest (15 tính cả parent) | [api-verification.log](api-verification.log); gồm hồi quy A03b |
| Browser | PASS 5 bài tổng hợp E01–E07 | [browser-verification.log](browser-verification.log), desktop 1440 và mobile 390 |
| Transaction rollback | PASS 2/2 | [transaction-verification.log](transaction-verification.log) |
| Docker lifecycle | PASS D01–D08 | [stack-verification.log](stack-verification.log) |

Các kiểm thử API và browser chạy qua frontend Nginx → gateway → backend thật → MariaDB thật, không mock database. Riêng E07 chặn phản hồi ở trình duyệt **sau khi server đã xử lý thành công**, để chứng minh retry không tạo thêm đơn.

Lượt cuối: API 15/15 tính cả parent; browser 5/5 trong 12,1 giây; unit 5/5. Đã chạy lại sau fault/recovery.

Triển khai độc lập được xác minh bổ sung bằng recreate thật: [deployment-verification.log](deployment-verification.log). Products đổi container ID; Orders giữ nguyên ID và StartedAt.

Ảnh giao diện: [desktop](screenshots/catalog-desktop.png), [mobile](screenshots/catalog-mobile.png), [đơn hàng](screenshots/orders-desktop.png).

## Lỗi đã phát hiện và sửa

1. **PATCH dùng giá trị mặc định của schema tạo.** Test A03 nhận 200 cho body rỗng. Nguyên nhân: `.partial()` trên schema có default vẫn sinh field mặc định trong Zod. Tách `createInput` có defaults khỏi `patchInput` không defaults. Thêm A03b xác nhận PATCH tên không tự bật lại sản phẩm hoặc xóa mô tả. Chạy lại API: tất cả pass.
2. **Kiểm tra vòng đời cần chứng minh recreate thật.** Một build không đổi nội dung có thể giữ nguyên container. Bổ sung `--force-recreate` và so sánh Products container ID; đồng thời kiểm tra Orders ID và StartedAt không đổi.
3. **Tiến trình npm trong sandbox không tải được registry.** Dừng lần cài bị kẹt, cài lại với quyền mạng và cache trong /tmp. Không bỏ qua lỗi build hay thay database bằng mock.

## Điều đã xác nhận

- Sáu container healthy; chỉ frontend publish port local.
- Các backend có network và quyền database riêng.
- Đồng thời 6 POST cùng key: đúng một lần tạo mới, còn lại replay cùng ID.
- Sửa giá sản phẩm không thay đổi snapshot đơn cũ.
- Products dừng: tạo đơn mới 503 trong thời hạn, đọc đơn và replay vẫn hoạt động.
- Products và Orders DB phục hồi: API ghi/đọc trở lại.
- Down/up không xóa volume: đơn cũ tồn tại.
- Trigger tạm làm lỗi item thứ hai: không còn order hoặc item dở dang; key có thể dùng lại sau rollback. Trigger đã được gỡ.
- Browser checkout, admin, deep-link, cart reload và mobile không có lỗi runtime trong các ca đã chạy.

## Phạm vi chưa kiểm thử / giới hạn

Chưa load test, chưa test cluster nhiều máy, chưa auth/security production, chưa kill process đúng thời điểm commit, chưa mô phỏng mọi lỗi mạng hoặc hết đĩa. Hai DB trên cùng máy không cung cấp HA. Image tags chưa pin digest. Kiểm tra UI tự động không thay thế accessibility audit đầy đủ.

Dữ liệu test được giữ để có thể xem đơn và snapshot; test sản phẩm mới sẽ được chuyển sang ngừng bán khi kết thúc. Không xóa dữ liệu có sẵn.
