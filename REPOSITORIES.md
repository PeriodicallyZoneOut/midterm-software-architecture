# Nguồn repository của các project

Ghi nhận trước khi xóa Git metadata trong các bản project đã copy. Repo chung là `midterm-software-architecture`, nhánh `main`. Các working files và thay đổi chưa commit được giữ nguyên; repo gốc ngoài thư mục này không bị sửa.

Ngày ghi nhận: 2026-11-01T15:29:46.280852+00:00.

## Project có Git metadata

| Bản project trong repo chung | Remote gốc | Branch | Commit đang checkout |
|---|---|---|---|
| [topics/01-quality-attributes/projects/online-boutique/source](topics/01-quality-attributes/projects/online-boutique/source/) | origin: [https://github.com/GoogleCloudPlatform/microservices-demo.git](https://github.com/GoogleCloudPlatform/microservices-demo.git) | `main` | `38e7348eb289eb5b87c0c6e8cb19ced0449dc389` |
| [topics/01-quality-attributes/projects/scripthammer/source](topics/01-quality-attributes/projects/scripthammer/source/) | origin: [https://github.com/TortoiseWolfe/ScriptHammer.git](https://github.com/TortoiseWolfe/ScriptHammer.git) | `main` | `40f984fdf894025b10116ff67cd6b2b1c504659f` |
| [topics/03-microservices-infrastructure/projects/istio/source](topics/03-microservices-infrastructure/projects/istio/source/) | origin: [https://github.com/istio/istio.git](https://github.com/istio/istio.git) | `master` | `4e2c1c576e33a7b411ee7f38ac4bb9dd45c36631` |
| [topics/03-microservices-infrastructure/projects/online-boutique/source](topics/03-microservices-infrastructure/projects/online-boutique/source/) | origin: [https://github.com/GoogleCloudPlatform/microservices-demo.git](https://github.com/GoogleCloudPlatform/microservices-demo.git) | `main` | `38e7348eb289eb5b87c0c6e8cb19ced0449dc389` |
| [topics/04-micro-frontends-jamstack/projects/blog-starter/source](topics/04-micro-frontends-jamstack/projects/blog-starter/source/) | Không cấu hình remote | `master` | `8e740126e9dfa44911809fe8f0cbd458b308cebf` |
| [topics/04-micro-frontends-jamstack/projects/micro-frontend-demo/source](topics/04-micro-frontends-jamstack/projects/micro-frontend-demo/source/) | origin: [https://github.com/rautio//micro-frontend-demo.git](https://github.com/rautio//micro-frontend-demo.git) | `main` | `9a4d33596453d2d76da9d8ebb0b5c9249a0a024d` |

## Nguồn tham khảo bổ sung

- Blog Starter không có remote trong bản Git local. README demo ghi nguồn mẫu: [vercel/next.js — examples/blog-starter](https://github.com/vercel/next.js/tree/canary/examples/blog-starter). Đây là nguồn tham khảo, không phải remote đã cấu hình.
- Mini Shop và People Profiles không có `.git` trong bản copy tại thời điểm ghi nhận; chưa xác định URL repository gốc.

## Sau khi hợp nhất

- Đã xóa `.git` ở sáu bản project liệt kê phía trên; giữ `.git` tại gốc repo chung.
- Không sử dụng submodule. Các file source thuộc working tree của repo chung, chịu quy tắc `.gitignore`.
- Commit/branch trên bảng là thông tin nguồn gốc; lịch sử Git cũ không được nhập vào lịch sử repo chung.
- Chưa tạo commit, chưa cấu hình remote hay publish repo chung.
