# Source — Istio

Workspace path: `week-03/istio`.

Upstream: https://github.com/istio/istio.

Điểm đọc code: `samples/addons/; architecture/; manifests/`.

- [ ] Ghi commit/tag hoặc snapshot hash đang demo và license.
- [ ] Ghi thay đổi local và cách áp dụng patch.
- [x] Copy nguyên thư mục project gốc vào `source/`, giữ metadata và `.git` nếu có; không dùng submodule.
- [ ] Cấu hình secret tại máy chạy; chỉ đưa `.env.example` đã lọc lên GitHub.

Bản local đã được copy nguyên trạng theo yêu cầu, gồm dependency/build, cấu hình local và Git history nếu có. Không thay thế bằng upstream mới nhất. File được giữ trên đĩa không đồng nghĩa được Git theo dõi; kiểm tra `.gitignore` khi chuẩn bị commit/publish.

Git metadata trong bản copy đã được loại bỏ để dùng repo chung. Xem URL/commit nguồn trong `REPOSITORIES.md` tại gốc repo. Working files giữ nguyên.
