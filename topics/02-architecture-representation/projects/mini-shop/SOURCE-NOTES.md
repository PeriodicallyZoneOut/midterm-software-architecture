# Source Notes — Mini Shop (Chủ đề 2: Architecture Representation)

* **Workspace path gốc trước khi copy:** `lab-01/microservices-project-demo`.
* **Thư mục làm việc hiện tại:** `topics/02-architecture-representation/projects/mini-shop/source/`.
* **Nguồn gốc & Metadata:**
  * Bản đồ án Lab 01 (`lab-01-mini-shop`, `"private": true` trong `package.json`).
  * Theo [`REPOSITORIES.md`](../../../../REPOSITORIES.md), bản gốc không có `.git` metadata riêng khi hợp nhất vào repo chung `midterm-software-architecture`.
  * Phiên bản runtime cố định trong `Dockerfile` và `compose.yaml`: Node.js `24-alpine`, Nginx `alpine` (1.27), MariaDB `11.8`, TypeScript `^5.9.0`, Express `^5.1.0`, Zod `^3.25.0`, React `^19.1.0`.
* **Điểm đọc code chính:**
  * `frontend/src/main.tsx`, `frontend/nginx.conf`, `frontend/Dockerfile`
  * `services/gateway/src/index.ts`, `services/gateway/src/http.ts`
  * `services/products/src/index.ts`, `services/products/src/db.ts`, `services/products/src/http.ts`
  * `services/orders/src/index.ts`, `services/orders/src/domain.ts`, `services/orders/src/db.ts`, `services/orders/src/http.ts`
  * `compose.yaml`, `Dockerfile`
* **Thay đổi cấu hình local đã thực hiện:**
  * Tạo file `.env` local từ `.env.example` để phục vụ chạy `docker compose up` (file `.env` nằm trong `.gitignore`, không đẩy secret lên Git).
  * Hiệu đính tài liệu đối chiếu trong `project-knowledge-application-implementation/` khớp 100% với DDL và HTTP handlers thực tế.

## Checklist trạng thái Source

- [x] Ghi phiên bản runtime/dependencies đang demo và nguồn gốc trong `REPOSITORIES.md`.
- [x] Ghi thay đổi cấu hình local (`.env` từ `.env.example`).
- [x] Copy nguyên thư mục project gốc vào `source/`, quản lý bằng repo chung; không dùng submodule.
- [x] Cấu hình `.env` tại máy chạy; chỉ đưa `.env.example` lên GitHub.
