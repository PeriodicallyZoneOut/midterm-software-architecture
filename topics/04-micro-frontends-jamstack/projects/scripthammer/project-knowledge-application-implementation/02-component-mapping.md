# Component → source → runtime của ScriptHammer

Đường dẫn tính từ `<workspace>/ScriptHammer`, snapshot ghi ở [SOURCE-NOTES](../SOURCE-NOTES.md). [Trích đoạn code và hash](../evidence/source-inspection.md) dùng để kiểm tra các nhận định.

| Component | Trách nhiệm / vào → ra | State sở hữu | File / symbol | Nơi chạy / dependency |
|---|---|---|---|---|
| Nguồn nội dung | Markdown + frontmatter → bài viết | File versioned trong Git | `public/blog/*.md` | Đầu vào của bước sinh dữ liệu |
| Generator | Parse metadata/content → JSON | `src/lib/blog/blog-data.json` | `scripts/generate-blog-data.js:generateBlogData/processMarkdownFile`; `package.json:generate:blog` | Node tại bước chuẩn bị build; chưa tự gọi trong prebuild |
| Blog routes | JSON → danh sách/slug/nội dung HTML | Snapshot nội dung trong artifact | `src/app/blog/page.tsx:getPosts`; `src/app/blog/[slug]/page.tsx:generateStaticParams`; `markdownProcessor.process` | Server Components lúc build, không SSR theo request Pages |
| Export config | Source/config → HTML/CSS/JS | basePath, assetPrefix, public env đóng vào build | `next.config.ts:nextConfig` | Next build; `output: export`, trailingSlash, unoptimized |
| Phát hành frontend | Build + Storybook + kiểm tra → artifact | `out/`, `merged-output` trong workflow | `.github/workflows/deploy.yml`; scripts stamp/retain assets | Runner dựng; GitHub Pages phục vụ tệp theo cấu hình |
| React app | HTML + JS + API → UI tương tác | Trạng thái UI, session/client cache | `src/app/layout.tsx`; `src/contexts/AuthContext.tsx` | Browser sau khi tải tài nguyên |
| Supabase client | Session/JWT → auth/data/storage/realtime | Backend sở hữu dữ liệu; browser giữ phiên | `src/lib/supabase/client.ts:createClient` | Browser gọi Supabase qua mạng |
| Auth và quyền | Login/session → tài nguyên được phép | Auth user, policies DB | `AuthContext`; `supabase/migrations/20251006_complete_monolithic_setup.sql` | UI guard ở browser; RLS ở Postgres |
| Edge Functions | JWT / request → thao tác cần secrets | Backend config, các record nghiệp vụ | `supabase/functions/create-stripe-checkout/index.ts`; `stripe-webhook/index.ts` | Deno/Supabase Functions; provider thanh toán bên ngoài |
| Messaging | Nội dung → mã hóa → gửi / queue | Khóa và dữ liệu theo thiết kế messaging | `src/services/messaging/message-service.ts`; `src/lib/messaging/encryption.ts` | Browser + backend; không phải một MFE riêng |
| Offline | Cache/queue → nội dung cũ / sync khi online | Cache Storage, IndexedDB/Dexie | `public/sw.js`; `offline-queue-service.ts` | Browser; không thay thế toàn bộ backend |
| Môi trường local | Source/dev/build → app/artifact | Named volumes tách `.next` | `docker-compose.yml:scripthammer/builder` | Dev server và builder tách; cổng host có thể tự cấp |

## Các ranh giới phải chỉ ra trên sơ đồ

1. Build runner đọc file và tạo artifact; không giữ vai trò auth/API production.
2. Static host phục vụ tài nguyên; browser mới gọi API bằng session người dùng.
3. Backend xác minh quyền và giữ secrets; không trông chờ browser ẩn button để bảo vệ dữ liệu.
4. Frontend, DB/schema/RLS và Edge Functions có vòng đời riêng; deploy Pages không tự đồng nghĩa deploy backend. `edge-functions.yml` kiểm tra kiểu Deno không phải bằng chứng functions đã chạy production.

Không mô tả .NET messaging là backend chính: cấu hình mặc định là Supabase. Provider là một nhánh tùy chọn; offline sync hiện vẫn tạo Supabase client trực tiếp. Slide giữ phần này để giải thích giới hạn có sẵn, không yêu cầu chạy thêm hệ thống.
