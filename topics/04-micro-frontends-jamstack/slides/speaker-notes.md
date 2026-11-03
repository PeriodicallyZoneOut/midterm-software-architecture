# Ghi chú cho lộ trình trình bày chính

Notes đầy đủ của 30/35 trang nằm ở [MFE](micro-frontend-architecture/speaker-notes.md) và [JAMstack](jamstack-architecture/speaker-notes.md). Mỗi trang dưới đây khoảng 60–90 giây, chỉ là gợi ý diễn tập. Không nói các bước demo đã chạy trong lượt tài liệu này.

| Trang | Cách giải thích bằng lời | File nên mở | Evidence / giới hạn |
|---|---|---|---|
| MFE 2 | Vấn đề là phát triển/phát hành tính năng. MAIN ghép shell, Products và Cart có trách nhiệm riêng. MFE không bắt buộc nhiều framework hoặc nhiều repo. | `*/webpack.config.js` | Source không chứng minh ba nhóm/phát hành riêng |
| MFE 11 | PRODUCTS và CART công bố năm module; MAIN lấy UI qua loader. Shared React singleton khác exposes: một bên chia sẻ runtime dependency, bên kia công bố module. | Exposes/shared ở hai remote; MAIN loader | Module contract/name/version phải tương thích |
| MFE 13 | Lần theo từng mũi tên: React.lazy → loadComponent → share scope → HTTP remoteEntry → init → get → factory → render. Remote server phục vụ mã, browser thực thi. | `utils/index.ts`; RemoteComponent | Network evidence của phiên Toàn; ErrorBoundary không phải sandbox |
| MFE 14 | ProductCard phát lệnh; CART là owner. Bus gọi đồng bộ, store publish snapshot rồi ghi storage, updater trả state. Refresh đọc storage, không replay event log. | ProductCard; PubSub; store | Chỉ local browser; không có backend/transaction |
| JAM 2 | Dựng trước HTML để phân phối tệp; JS vẫn gọi API. Auth, messaging/payment có backend Supabase/functions riêng. | next.config; Supabase client | Config không xác nhận deployment live |
| JAM 10 | So sánh thời điểm render bốn mode. Demo kết hợp SSG và CSR; không có Next SSR/ISR trong export/Pages. Server Component đọc file là bước build. | blog/page; static params | Không dùng next dev làm bằng chứng production |
| JAM 11 | Đi từ MD qua generator/gray-matter thành JSON; static params lấy slug, processor tạo HTML. Nhấn prebuild/deploy chưa tự gọi generate:blog. | package.json; generator; slug page | Không nhầm `_posts` của Blog Starter |
| JAM 12 | A đang serve không đổi chỉ vì source MD đổi. Sinh JSON/build B, publish rồi so cache/SW. API đổi dữ liệu runtime theo đường khác. | deploy.yml; stamp script; SW | Dùng artifact/log A/B thật của Toàn; không tạo kết quả thay thế |

Kết mỗi phần bằng một đánh đổi: MFE tự chủ UI cần contract/version/trust; JAMstack phân phối tệp cần quản lý nội dung/cache và tương thích API. Khi chưa có evidence runtime của câu hỏi, trả lời “source cho thấy …; phiên runtime này chưa được đối chiếu trong lượt chuẩn bị tài liệu”, rồi chỉ đúng file.
