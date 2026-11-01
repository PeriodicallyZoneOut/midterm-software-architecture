# Hồ sơ · RabbitMQ Stream · Hai consumer

Tóm tắt những gì đã triển khai: [IMPLEMENTATION.md](IMPLEMENTATION.md).

App có họ tên, email, ngày sinh và tuổi tự tính. Ghi mới/sửa/xóa tạo event trên
RabbitMQ Stream. Hai consumer độc lập đọc cùng stream: một lưu Read DB MariaDB,
một gửi email thông báo tới **gtvbeon@gmail.com**.

## Xem ở đâu?

- App: **http://localhost:3003**
- Trang quan sát MQ, hai consumer, MariaDB và email: **http://localhost:3003/data-flow**
- RabbitMQ Management: **http://localhost:15672** → Queues and Streams →
  **people.events.preview** → **Get messages** để xem payload JSON ngay trong UI.
  Chọn Ack mode có **requeue true** để giữ bản sao khi xem.
  Queue preview nhận bản sao từ exchange; stream gốc `people.events.retained` vẫn giữ event.
  Đọc queue preview không chạy lại hai consumer nghiệp vụ hoặc gửi lại email. Username: `people_app`, password trong
  `.secrets/mq-password` trên máy. Không đưa password vào chat hoặc git.
- MariaDB: **127.0.0.1:3307**, database `people_read`. Trang quan sát có bảng SQL.
- JSON trạng thái: `/api/projection`; nội dung event trên broker: `/api/mq/events`.

Nút **Đọc lại MQ — không xóa** tạo một reader tạm thời đọc stream trực tiếp.
Reader này không thay đổi offset của hai consumer nghiệp vụ. Trang giữ 20 event
cuối đã đọc trong lượt xem, với giới hạn thời gian 1,5 giây cho demo.

## Luồng dữ liệu

```mermaid
flowchart LR
    UI[Form có email] --> API[Command API]
    API --> Outbox[(SQL command state + outbox)]
    Outbox --> Publisher[Publisher confirms]
    Publisher --> MQ[(RabbitMQ retained stream)]
    MQ --> C1[Consumer 1: read-consumer.js]
    MQ --> C2[Consumer 2: email-consumer.js]
    C1 --> Read[(MariaDB Read DB)]
    Read --> Query[Danh sách / lịch sử]
    C2 --> SMTP[Gmail SMTP]
    SMTP --> Mail[gtvbeon@gmail.com]
```

Stream là `people.events.retained`, exchange fanout `people.events`. Mỗi consumer
có offset riêng trong `mq_consumer_offsets`. ACK trên stream không xóa message.
Không cấu hình max-age/max-length retention. Volume `mq_data` giữ dữ liệu khi dừng
container; quản trị viên vẫn có thể chủ động xóa stream/volume.

API transaction lưu `people_commands` và `mq_outbox` cùng nhau. Publisher gửi event,
đợi broker confirm rồi đánh dấu published. Nếu crash sau confirm, có thể publish lại;
consumer dùng event ID chống xử lý trùng.

### Consumer 1 — Read DB

`read-consumer.js` nhận event và gọi `adapter.js`:

1. Kiểm tra event; dùng `consumer_inbox` để nhận biết event đã áp dụng.
2. Lưu snapshot vào `people_history` và cập nhật `people_current` nếu phiên bản mới hơn.
3. Ghi inbox và offset cùng transaction, COMMIT rồi ACK.

Danh sách và lịch sử SELECT từ Read DB. Ghi command dùng bảng trạng thái riêng để
kiểm tra version, không dùng bản chiếu đang trễ. API đợi tối đa 3 giây cho consumer
Read DB rồi trả `projected`; timeout vẫn giữ event đã commit và báo chờ đồng bộ.

### Consumer 2 — Email

`email-consumer.js` đọc cùng stream, gửi thông báo tới `gtvbeon@gmail.com` qua SMTP.
Email của hồ sơ được lưu trong payload và Read DB; người nhận thông báo cố định.
Tài khoản gửi và nhận có thể cùng Gmail.

Khi SMTP chấp nhận thư, consumer ghi `email_deliveries` và offset rồi ACK.
`status=sent` nghĩa là SMTP đã chấp nhận, không khẳng định thư đã vào Inbox.
Trang quan sát hiển thị recipient, trạng thái, số lần gửi, lỗi, Message-ID và nội dung.
Gửi lỗi/chưa có SMTP: consumer giữ vị trí, thử lại sau 30 giây; consumer Read DB
vẫn tiếp tục độc lập. Một thư lỗi sẽ chặn các thư sau của consumer Email đến khi sửa.

Bản ghi `sent` ngăn gửi lại khi message được phát lại. SMTP không có distributed
transaction với SQL: crash sau khi SMTP nhận nhưng trước khi ghi trạng thái có thể
gây gửi trùng. Message-ID xác định theo event ID giúp truy vết, không bảo đảm Gmail
sẽ loại mọi thư trùng.

## Chạy hoàn toàn bằng Docker

```bash
./setup.sh
```

Script tạo secret còn thiếu rồi build/chạy. Không cài Node.js, npm hoặc DB lên host.
Tên project vẫn là `people-kurrent` để giữ volume MariaDB đang có.

```bash
docker compose -p people-kurrent up -d --build --wait
docker compose -p people-kurrent ps
docker compose -p people-kurrent logs -f publisher read-consumer email-consumer
```

`init-db` là bước migration chạy một lần rồi thoát mã 0, không phải consumer.
Các service chạy lâu dài: app, RabbitMQ, MariaDB, publisher, read-consumer,
email-consumer. Publisher là producer chuyển outbox sang MQ.

Dừng và giữ dữ liệu:

```bash
docker compose -p people-kurrent down
```

Giữ `.secrets/`, `.env.smtp`, volume `read_data`, `mq_data`. Không dùng `down -v`
nếu muốn giữ dữ liệu. Cổng chỉ mở loopback, app hiện chưa có đăng nhập.

## Gmail SMTP

Bật 2-Step Verification trên tài khoản gửi, tạo App Password tại
https://myaccount.google.com/apppasswords rồi điền `.env.smtp`:

```dotenv
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=gtvbeon@gmail.com
SMTP_PASS=APP_PASSWORD_16_KY_TU_KHONG_CO_DAU_CACH
SMTP_FROM=gtvbeon@gmail.com
```

Dùng App Password, không dùng mật khẩu đăng nhập Gmail. File này được gitignore,
không copy vào image; chỉ consumer Email được mount. Nếu editor thay file bằng
inode mới, recreate consumer để cập nhật bind mount:

```bash
docker compose -p people-kurrent up -d --no-deps --force-recreate email-consumer
```

## Dữ liệu từ phiên bản KurrentDB

KurrentDB không còn là service chạy. Volume cũ được giữ làm bản lưu.
Dữ liệu Read DB và lịch sử được giữ; command state bootstrap từ snapshot hiện tại.
Lịch sử cũ được publish lên retained stream với `notifyEmail: false`, để xem lại
trên MQ mà không gửi hàng loạt email cũ. Consumer Email hiển thị `skipped-history`.
Các hồ sơ cũ chưa có email để NULL; nhập email khi sửa. Thao tác mới yêu cầu email.

Code: `store.js` command/outbox; `publisher.js` publish; `mq.js` broker/retained viewer;
`consumer.js` vòng lặp; `read-consumer.js` + `adapter.js` SQL; `email-consumer.js` SMTP;
`read-db.js` query; `mq-schema.js` migration; `public/data-flow.*` màn hình quan sát.

Tham khảo: [RabbitMQ Streams](https://www.rabbitmq.com/docs/streams),
[Publisher confirms](https://www.rabbitmq.com/docs/confirms),
[Google App Passwords](https://support.google.com/accounts/answer/185833).
