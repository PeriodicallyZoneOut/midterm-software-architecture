# Runbook nhắc demo JAMstack / ScriptHammer

**Đây là hướng dẫn, không phải log đã chạy.** Toàn đã chạy hệ thống; lượt tài liệu này không build/start app, không gọi Supabase hoặc payment provider.

## Môi trường

Working directory: `<workspace>/ScriptHammer`, commit theo SOURCE-NOTES. Dùng môi trường Docker/pnpm, dependency và env của phiên đã chuẩn bị. `docker-compose.yml` có `scripthammer` là dev service và `builder` là service build riêng, có volume `.next` riêng; không build trong container dev đang chạy.

Các lệnh có trong cấu hình để đối chiếu (chỉ chạy lại khi Toàn tự diễn tập):

```powershell
# Trong <workspace>/ScriptHammer; xem cổng vì SH_PORT mặc định có thể tự cấp.
docker compose port scripthammer 3000
# Khi đã thay Markdown và cần tạo production artifact:
docker compose run --rm builder pnpm run generate:blog
docker compose run --rm builder pnpm run build
```

`generate:blog` ghi JSON vào source bind mount, cần giữ thay đổi nội dung trong phạm vi bản diễn tập. Không tự xóa/ghi đè dữ liệu đang dùng. Build chuẩn export ra `out/`; nếu dùng `NEXT_DIST_DIR`, đối chiếu đường dẫn thực theo cấu hình/script đã chọn. `next start` không phải cách phục vụ static export. Dùng static server đã chuẩn bị cho artifact khi trình diễn production; không gọi dev server là CDN.

## Kịch bản chứng minh ranh giới build/runtime

| Bước | Đọc / thao tác | Expected | Evidence của phiên thật |
|---|---|---|---|
| 1 | Mở `next.config.ts` và build log/artifact đã có | `output: export`, có HTML/assets | Commit/tool versions, log, route HTML |
| 2 | Chọn một bài published; đối chiếu MD, JSON và HTML `/blog/<slug>/` | Cùng nội dung bản A | Đường dẫn, hash/timestamp và đoạn nội dung |
| 3 | Giải thích thay MD khi artifact A đang được serve | HTML A chưa đổi | So sánh bản A, không chỉ xem MD public |
| 4 | Khi đã chuẩn bị kịch bản B, sinh JSON rồi build/export/publish | JSON/HTML B chứa thay đổi | Build log B, hash A/B, screenshot source HTML |
| 5 | So sánh phiên sạch và phiên còn cache/SW | Có thể khác version trước khi cập nhật cache | Network/Application SW version, thời điểm |
| 6 | Mở một luồng API đã cấu hình, ví dụ đăng nhập hoặc đọc dữ liệu test | Frontend static gọi API động bằng session | Network đã lọc token; không cần thanh toán thật |

Readiness theo môi trường: artifact có route cần demo, static server trả đúng assets/basePath; API/session đã cấu hình nếu trình diễn luồng động. Có HTML file chưa chứng minh Supabase healthy và ngược lại.

## Recovery và điểm giới hạn

Nếu bài mới không xuất hiện, kiểm tra theo thứ tự MD → JSON → HTML export → artifact đã publish → browser cache/SW. Nếu route/asset 404, đối chiếu basePath/assetPrefix/URL hosting. Không reset DB/volumes để sửa lỗi frontend. Nếu API không sẵn sàng, có thể giải thích code boundary và artifact tĩnh, ghi actual lỗi thay vì nói API đã thành công.

Hoàn tác đúng thay đổi bài diễn tập bằng cách khôi phục bản đã lưu trước khi sửa; không dùng lệnh reset toàn repo. Dừng static server do mình mở bằng Ctrl+C. Khi muốn dừng dev service riêng của mình, dùng `docker compose stop scripthammer`, không xóa volumes. Ghi rõ expected/actual của phiên cá nhân trong evidence; tài liệu này không thêm log giả.
