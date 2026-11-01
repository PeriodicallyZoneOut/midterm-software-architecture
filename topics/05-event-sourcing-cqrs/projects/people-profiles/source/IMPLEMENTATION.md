# Tóm tắt triển khai

Ứng dụng quản lý hồ sơ gồm họ tên, email, ngày sinh và tuổi tự tính; hỗ trợ thêm,
sửa, xóa và xem lịch sử. Toàn bộ app, RabbitMQ và MariaDB chạy bằng Docker Compose.

## Những gì đã làm

- Thay KurrentDB bằng RabbitMQ; giữ dữ liệu MariaDB và lịch sử cũ.
- Bổ sung email vào form, event và Read DB.
- Lưu command và outbox trong cùng transaction; publisher chuyển event sang MQ.
- Triển khai hai consumer độc lập, mỗi consumer có offset riêng:
  - `read-consumer.js` dùng `adapter.js` chuyển payload thành dữ liệu trong
    `people_current` và `people_history` của MariaDB.
  - `email-consumer.js` gửi thông báo qua Gmail SMTP tới `gtvbeon@gmail.com`,
    lưu kết quả vào `email_deliveries` và thử lại khi lỗi.
- Thêm trang `/data-flow` để quan sát event, consumer, Read DB và trạng thái email.
- Thêm queue `people.events.preview` để xem payload ngay trong RabbitMQ Management.

## Luồng dữ liệu

```text
Form → API → SQL outbox → Publisher → Exchange people.events
                                      ├─ Stream people.events.retained
                                      │  ├─ Consumer Read DB → MariaDB → App đọc
                                      │  └─ Consumer Email → Gmail SMTP
                                      └─ Queue people.events.preview → Xem payload
```

Stream giữ event sau khi consumer ACK. Hai consumer dùng event ID chống xử lý
trùng; riêng gửi email vẫn có thể trùng nếu tiến trình dừng giữa lúc SMTP nhận thư
và lúc ghi kết quả vào SQL. Lịch sử nhập từ KurrentDB không gửi email lại.

## Cách xem và chạy

| Nội dung | Địa chỉ / thao tác |
| --- | --- |
| App | http://localhost:3003 |
| Quan sát toàn bộ luồng | http://localhost:3003/data-flow |
| Payload trong RabbitMQ | http://localhost:15672/#/queues/%2F/people.events.preview |
| Đăng nhập RabbitMQ | User `people_app`; mật khẩu trong `.secrets/mq-password` |
| Xem message, giữ bản sao | **Get messages** → **Nack message requeue true** → **Get Message(s)** |
| MariaDB | `127.0.0.1:3307`, database `people_read` |
| Email | Kiểm tra hộp thư `gtvbeon@gmail.com`; trạng thái trên `/data-flow` |

```bash
docker compose -p people-kurrent up -d --build --wait
docker compose -p people-kurrent ps
docker compose -p people-kurrent logs -f publisher read-consumer email-consumer
```

Đã kiểm tra dịch vụ chạy và SMTP chấp nhận gửi thư; chưa chạy bộ test đầy đủ.
`sent` là SMTP đã nhận thư, không bảo đảm thư nằm trong Inbox.
Giữ `.env.smtp`, `.secrets/` và các volume; dùng `down` không kèm `-v` để giữ dữ liệu.

Chi tiết cấu hình: [README.md](README.md).
