# JAMstack và các chế độ render trong ScriptHammer

JAMstack dựng trước giao diện và tách nó khỏi các dịch vụ động. **JavaScript** tạo tương tác và gọi dịch vụ; **APIs** cung cấp auth/dữ liệu/nghiệp vụ; **Markup** là HTML dựng sẵn. Nó không phải tên framework hay cam kết toàn bộ ứng dụng không có backend.

ScriptHammer dùng Next.js `output: 'export'`. Frontend có thể được phân phối bằng hosting tĩnh, trong khi browser gọi Supabase Auth/Postgres/Storage/Realtime và Edge Functions. Server Components đọc nội dung lúc build vẫn phù hợp static export; từ “server” không đồng nghĩa xử lý request production.

| Chế độ | Tạo HTML / cập nhật | Cần server render production? | Áp dụng ở demo |
|---|---|---|---|
| CSR | Browser chạy JS, lấy dữ liệu API và cập nhật UI | Không cần Next server; API vẫn có backend | Auth, dữ liệu theo phiên, messaging/payment UI |
| SSR | Server tạo HTML theo request | Có | Chỉ đối chiếu lý thuyết; không có trong deployment static export |
| SSG | Sinh HTML lúc build | Hosting chỉ cần phục vụ tệp | Blog và các route export được |
| ISR | Runtime hỗ trợ tái tạo trang sau build | Có hạ tầng hỗ trợ | Không có với `output: export` trên Pages |

Hydration gắn React/tương tác vào HTML đã nhận. SSG và CSR có thể cùng xuất hiện trong một ứng dụng: có HTML khung từ build, dữ liệu cá nhân lấy sau đăng nhập. Trình duyệt gọi API mỗi lần cần dữ liệu khác với việc Next server SSR cả trang.

## Build time và request/runtime

**Build:** đọc code, JSON nội dung và cấu hình; sinh route HTML/assets; bundle `NEXT_PUBLIC_*`. **Request tệp:** hosting trả HTML/JS/CSS. **Runtime browser:** React, session, fetch/API, service worker/IndexedDB. **Runtime backend:** Supabase và functions xử lý quyền, dữ liệu, secrets. Runner CI không phải backend xử lý request người dùng.

Nội dung blog cố định theo artifact build; dữ liệu giỏ/tin nhắn/tài khoản trên API không cần rebuild blog mỗi khi thay đổi. Đổi biến `NEXT_PUBLIC_*` dùng trong bundle cần build/phát hành frontend; đổi secret backend không đồng nghĩa thay bundle công khai.

## Pipeline nội dung thật

`public/blog/*.md` → `scripts/generate-blog-data.js` (gray-matter) → `src/lib/blog/blog-data.json` → `generateStaticParams` và trang blog → `markdownProcessor.process` → HTML/assets export. Đây không phải `_posts → api.ts → remark` của Blog Starter. **`generate:blog` là bước riêng**, hiện không được gọi bởi `prebuild` hoặc workflow deploy; cần sinh JSON trước khi build nếu thay nội dung Markdown.

Repo dùng nội dung từ Git/Markdown/JSON trong pipeline được phân tích, không có bằng chứng một headless CMS bên ngoài tham gia luồng này. Headless CMS là lựa chọn kiến trúc tổng quát, không phải thành phần đã triển khai.

## Cache, phát hành và đánh đổi

Frontend tĩnh dễ phân phối/cache, giảm nhu cầu vận hành server render. Đổi lại, nội dung dựng sẵn cần rebuild/redeploy, nhiều client có thể còn artifact/cấu hình cũ, và tác vụ động phụ thuộc API. `stamp-sw-version.mjs` đổi version SW lúc build; workflow có giữ assets cũ theo cửa sổ 14 ngày để giảm lỗi chunk. Các cơ chế đó không bảo đảm mọi cache đồng nhất hoặc người dùng luôn có phiên bản mới ngay.

Static hosting không tự cấp quyền dữ liệu. Route guard chỉ điều khiển trải nghiệm; Supabase JWT/RLS và kiểm tra trong Edge Functions mới quyết định truy cập. Secrets như service-role/Stripe secret không thuộc `NEXT_PUBLIC_*`. Phần này giải thích boundary cho JAMstack, không mở rộng thành audit bảo mật của thành viên khác.
