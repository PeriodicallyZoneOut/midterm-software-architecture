# Nguồn chính Micro-Frontend của Toàn

- Workspace: `<workspace>/micro-frontend-demo` (nằm cạnh repo tài liệu).
- Upstream: [rautio/micro-frontend-demo](https://github.com/rautio/micro-frontend-demo).
- Commit đọc: `9a4d33596453d2d76da9d8ebb0b5c9249a0a024d`, branch `main`; working tree sạch khi inspect ngày 03/11/2026.
- Điểm bắt đầu: [loader tại snapshot](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/src/utils/index.ts), [store](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/cart/src/store/index.ts).
- Không thấy tệp LICENSE riêng trong snapshot gốc; không tự gán giấy phép. README/upstream là nguồn provenance, không thay giấy phép.

Bản `source/` trong slot này là bản copy trước đó, có Docker/Compose/Nginx và thay đổi local so với upstream. Nó được giữ nguyên để không ảnh hưởng công việc đã có, nhưng **không phải nguồn chính được dùng để mô tả demo của Toàn**. Không chuyển runtime hoặc dependency từ bản này sang source chính.

[Source inspection](evidence/source-inspection.md) lưu hash và trích đoạn các file quan trọng, giúp đọc PR mà không phải tải toàn bộ repo gốc. Lượt này không sửa hay chạy ứng dụng. Thông tin chạy thành công là do Toàn cung cấp; chưa đối chiếu log/ảnh phiên chạy.
