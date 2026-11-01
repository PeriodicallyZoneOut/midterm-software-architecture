# Source — Micro Frontend Fruit Store

Workspace path: `micro-frontend/micro-frontend-demo`.

Upstream: https://github.com/rautio/micro-frontend-demo.

Điểm đọc code: `main/src/utils/index.ts; main/src/services/pubsub.ts; products/src/; cart/src/store/index.ts; */webpack.config.js`.

- [ ] Ghi commit/tag hoặc snapshot hash đang demo và license.
- [ ] Ghi thay đổi local và cách áp dụng patch.
- [x] Copy nguyên thư mục project gốc vào `source/`, giữ metadata và `.git` nếu có; không dùng submodule.
- [ ] Cấu hình secret tại máy chạy; chỉ đưa `.env.example` đã lọc lên GitHub.

Bản local đã được copy nguyên trạng theo yêu cầu, gồm dependency/build, cấu hình local và Git history nếu có. Không thay thế bằng upstream mới nhất. File được giữ trên đĩa không đồng nghĩa được Git theo dõi; kiểm tra `.gitignore` khi chuẩn bị commit/publish.

Git metadata trong bản copy đã được loại bỏ để dùng repo chung. Xem URL/commit nguồn trong `REPOSITORIES.md` tại gốc repo. Working files giữ nguyên.
