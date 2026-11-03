# Kiểm chứng và đánh đổi JAMstack

Toàn cho biết đã chạy hệ thống. Lượt này chỉ inspect source và dựng slide; không build/start ScriptHammer, không gọi API. Phải phân biệt **cấu hình có trong code** với **artifact production/HTTP đã quan sát**.

| Khẳng định | Bằng chứng hiện có | Đối chiếu runtime / artifact của phiên đã chạy | Giới hạn |
|---|---|---|---|
| Có chủ đích static export | `next.config.ts: output: export` | Build log + HTML/assets export của đúng commit | Config không tự chứng minh build thành công |
| Blog đọc dữ liệu lúc build | `getPosts`, `generateStaticParams`, markdownProcessor | Tìm nội dung cụ thể trong HTML slug export | Dev server không đủ chứng minh SSG production |
| Markdown cần JSON trung gian | `generate:blog`, generator và blog routes | So sánh MD → JSON → HTML của bản A/B | prebuild/deploy không tự gọi generator |
| Có hosting tĩnh trong thiết kế | `deploy.yml: merged-output → Pages` | Artifact và deployment URL thực của Toàn | Không gọi localhost Node dev server là CDN |
| API cung cấp dữ liệu động | Supabase client/AuthContext/services | Network của phiên test đã cấu hình | Source không xác nhận backend/keys/policies live |
| Có cache/SW/queue | `sw.js`, stamp script, queue service | Phiên sạch so với phiên cache, offline theo phạm vi | Không bảo đảm toàn app offline |

## Đánh đổi trọng tâm

- **Tệp dựng sẵn ↔ thời gian cập nhật nội dung.** Không cần render server cho mỗi trang; phải sinh dữ liệu/rebuild/publish khi nội dung build thay. Nếu nội dung cần thay theo request, dùng API/client hoặc hosting render phù hợp thay vì gọi Pages là SSR.
- **Tách frontend/backend ↔ hợp đồng giữa các bản.** Client cũ còn hoạt động sau deploy; schema/RLS/functions phải tương thích. Deploy static frontend không tự deploy toàn backend.
- **Cache ↔ độ mới và độ nhất quán.** Tải lại nhanh hơn không đồng nghĩa thấy bản mới ngay. Giữ chunks cũ giảm lỗi tham chiếu nhưng có chi phí lưu trữ/vòng đời.
- **API trực tiếp từ browser ↔ thực thi quyền backend.** Browser dùng cấu hình công khai/JWT; backend phải kiểm tra quyền. Cấu hình hay route guard frontend không thay RLS/kiểm tra trong function.

Không bổ sung benchmark, audit bảo mật hay deployment mới vì ngoài yêu cầu lượt này. SSR/ISR chỉ là kiến thức so sánh, không phải khả năng đã triển khai. [Runbook](../demo/runbook.md) và [evidence](../evidence/README.md) ghi rõ nơi đối chiếu kết quả cá nhân.
