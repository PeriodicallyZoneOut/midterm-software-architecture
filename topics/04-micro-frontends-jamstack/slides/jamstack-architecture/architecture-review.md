# Rà soát kiến trúc JAMstack của ScriptHammer

Snapshot: commit `a2dd31ae25ea30c678d990432c7e2b60b4faeda7`. Phân tích từ mã local; không suy ra rằng cấu hình trong kho mã đã được triển khai đúng trên dịch vụ thật. Không sửa mã nguồn ScriptHammer.

## Kết luận kiến trúc

ScriptHammer xuất frontend Next.js thành tệp tĩnh cho GitHub Pages. React trong trình duyệt gọi Supabase để xác thực, đọc/ghi dữ liệu, lưu tệp và nhận thay đổi. Edge Functions xử lý thao tác cần secrets, tích hợp thanh toán và webhook. Trình duyệt còn có service worker, cache và IndexedDB cho một số khả năng ngoại tuyến.

Đây là **frontend tĩnh với backend động**, không phải một hệ thống không có backend. Server Components đọc tệp ở bước dựng vẫn phù hợp static export; không có Next.js SSR theo yêu cầu trong luồng Pages này.

## 4+1 góc nhìn và bằng chứng

| Góc nhìn | Trách nhiệm được thể hiện | Mã nguồn |
|---|---|---|
| Logic | UI, điều phối auth/messaging/payment, dịch vụ backend | [app](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/app/layout.tsx), [AuthContext](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/contexts/AuthContext.tsx), [MessageService](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/services/messaging/message-service.ts), [Stripe client](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/lib/payments/stripe.ts) |
| Phát triển | Frontend, SQL, Deno Functions và công cụ kiểm tra có đầu ra riêng | [package.json](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/package.json), [tsconfig](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/tsconfig.json), [migration](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/supabase/migrations/20251006_complete_monolithic_setup.sql), [workflow Edge](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/.github/workflows/edge-functions.yml) |
| Tiến trình | API auth, mã hóa, queue, webhook và đồng bộ bất đồng bộ | [client](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/lib/supabase/client.ts), [encryption](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/lib/messaging/encryption.ts), [queue](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/services/messaging/offline-queue-service.ts), [webhook](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/supabase/functions/stripe-webhook/index.ts) |
| Vật lý | Runner dựng, Pages phục vụ, browser thực thi, Supabase và provider xử lý nghiệp vụ | [Next config](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/next.config.ts), [deploy.yml](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/.github/workflows/deploy.yml), [Docker Compose](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/docker-compose.yml), [Edge checkout](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/supabase/functions/create-stripe-checkout/index.ts) |
| +1 Kịch bản | Đọc blog, đăng nhập, gửi tin, offline, checkout và phát hành khi có client cũ | [blog](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/app/blog/page.tsx), [AuthContext](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/contexts/AuthContext.tsx), [MessageService](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/services/messaging/message-service.ts), [Stripe client](https://github.com/TortoiseWolfe/ScriptHammer/blob/a2dd31ae25ea30c678d990432c7e2b60b4faeda7/src/lib/payments/stripe.ts) |

## Bằng chứng cốt lõi

| Nhận định | Vị trí cụ thể | Hệ quả kiến trúc |
|---|---|---|
| Static export | `next.config.ts:43`, trailingSlash dòng 46, unoptimized dòng 48 | Production phục vụ tệp, không cần `next start`. |
| Nội dung đọc khi dựng | `app/blog/page.tsx` đọc `blog-data.json`; `blog/[slug]/page.tsx:253` có generateStaticParams | Nội dung này đổi theo lần build; dữ liệu người dùng đổi qua API. |
| Deploy tệp và Storybook | `deploy.yml:72`, `:173`, `:334`, `:349` | Runner dựng, ghép artifact rồi Pages phân phối; runner không xử lý request nghiệp vụ. |
| Giữ chunk cũ | `deploy.yml:331` đặt RETAIN_DAYS là 14; bước retention có continue-on-error | Đây là giảm thiểu lỗi HTML cũ/chunk mới, không phải bảo đảm cache luôn nhất quán. |
| JWT và RLS | Supabase client + SQL: messages có RLS ở dòng 3305; policy tham gia hội thoại ở dòng 3308 trở đi | Route guard là UX; quyền thực sự nằm ở backend. |
| Edge dùng đặc quyền | `create-stripe-checkout/index.ts` xác minh JWT, kiểm tra template_user_id, expiry và chain/session trước khi dùng Stripe | Service role cần kiểm tra nghiệp vụ riêng vì có thể bỏ qua RLS. |
| Browser checkout không xác nhận cuối cùng | `lib/payments/stripe.ts`; `stripe-webhook/index.ts` | Redirect hỗ trợ UI; webhook có chữ ký và xử lý event là đường xác nhận backend. |

## Những giới hạn cần giải thích đúng

**Ngoại tuyến không có nghĩa mọi thứ đều chạy được.** `public/sw.js` chỉ xử lý những request theo quy tắc; bỏ request không phải GET, `_next`, payload `.txt` và một số media. Messaging cần phiên, khóa và thông tin hội thoại sẵn có để gửi offline. API, xác thực mới và dữ liệu chưa cache vẫn phụ thuộc mạng.

**Hàng đợi không chỉ có ciphertext.** `message-service.ts:374` trở đi truyền cả ciphertext và `content` vào hàng chờ. `offline-queue-service.ts:57` tạo đối tượng bằng cách trải dữ liệu đầu vào rồi ghi IndexedDB. Khi sync thành công, dòng 296–297 xóa `content` và `plaintext_content`. Bài kiểm tra `offline-queue-plaintext.test.ts` còn kiểm tra việc giữ nội dung khi sync thất bại và xóa queue khi clearKeys. Vì vậy không khẳng định mọi dữ liệu trong IndexedDB đều đã mã hóa.

**Lớp provider chưa bao trùm mọi đường đi.** `backend.config.ts:37` chọn Supabase mặc định hoặc .NET. MessageService gọi `this.provider.sendMessage` tại dòng 418. Nhưng `offline-queue-service.ts:145–146` tạo Supabase client trực tiếp rồi upsert `messages` tại dòng 225. `createMessagingClient` chỉ trả lại chính client đã truyền vào. Thay registry không đủ để chứng minh toàn bộ offline sync độc lập backend. Nhánh .NET cũng không thay các miền auth và payment của ứng dụng.

**Mã hóa nội dung không thay mọi biện pháp bảo mật.** ECDH/AES-GCM diễn ra ở browser và API chuyển ciphertext, nhưng vẫn có metadata. Khóa không extractable hạn chế xuất khóa thô, không tự ngăn XSS sử dụng khả năng của khóa. Đây không phải audit mật mã hoặc chứng nhận bảo mật.

**Các đơn vị phát hành khác nhau phải tương thích.** Bundle frontend chứa cấu hình `NEXT_PUBLIC_*` tại thời điểm build. Schema/RLS, Edge code và secrets có vòng đời backend riêng. Workflow `edge-functions.yml` kiểm tra kiểu Deno, không phải bằng chứng đã deploy functions.

## Tài liệu cũ và nguồn chuẩn

README và sơ đồ kiến trúc cũ nói đến 12 Edge Functions. Snapshot đang đọc có 18 thư mục endpoint chứa `index.ts`, chưa tính `_shared`. Các slide không dùng con số cũ làm phạm vi đầy đủ. Hướng dẫn localhost:3000 cũng cần đối chiếu `docker-compose.yml:62`: mặc định `SH_PORT:-0` để Docker cấp cổng host; xem cổng bằng `docker compose port scripthammer 3000`.

Không xác minh phiên bản SQL/Edge thật, secrets, cấu hình OAuth, tình trạng Pages, uptime, hiệu năng hoặc kết quả test của hệ thống. Các đề xuất ở trang 30 được đánh dấu rõ và chưa triển khai.

## Nguồn khái niệm

- [JAMstack](https://jamstack.org/what-is-jamstack/).
- [Next.js static exports](https://nextjs.org/docs/app/guides/static-exports); mã local dùng Next.js 15.5, không giả định trùng phiên bản tài liệu mới nhất.
- [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Edge Functions](https://supabase.com/docs/guides/functions).
- [Kruchten: mô hình 4+1](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf).
- [mpuig/agent-slides](https://github.com/mpuig/agent-slides).
