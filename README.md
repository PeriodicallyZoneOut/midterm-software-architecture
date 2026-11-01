# Midterm Software Architecture

Repo chuẩn bị vấn đáp giữa kỳ: kiến thức trên slide, demo và cách kiến trúc được triển khai trong từng project.

## Chủ đề

| Chủ đề | Projects |
|---|---|
| [Quality Attributes](topics/01-quality-attributes/README.md) | Online Boutique, ScriptHammer, Mini Shop |
| [Architecture Representation](topics/02-architecture-representation/README.md) | Mini Shop |
| [Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana](topics/03-microservices-infrastructure/README.md) | Online Boutique, Istio |
| [Micro-Frontends và JAMstack](topics/04-micro-frontends-jamstack/README.md) | Micro Frontend Fruit Store, Next.js Blog Starter |
| [Event Sourcing và CQRS](topics/05-event-sourcing-cqrs/README.md) | People Profiles |
| [Event-Driven Architecture](topics/06-event-driven-architecture/README.md) | People Profiles |

## Cấu trúc

```text
midterm-software-architecture/
├── README.md
├── docs/                    # Kiểm kê và backlog tổng
├── templates/               # Mẫu ghi nhận project
└── topics/
    └── <topic>/
        ├── README.md
        ├── slides/
        │   ├── outline.md
        │   ├── speaker-notes.md
        │   ├── assets/
        │   └── exports/
        └── projects/
            └── <project>/
                ├── README.md
                ├── SOURCE-NOTES.md
                ├── source/           # Bản copy nguyên project
                ├── project-knowledge-application-implementation/
                │   ├── README.md
                │   ├── 01-concepts.md
                │   ├── 02-component-mapping.md
                │   ├── 03-implementation.md
                │   └── 04-verification-and-tradeoffs.md
                ├── demo/runbook.md
                └── evidence/
```

Một chủ đề có nhiều project. Một project có thể xuất hiện trong nhiều chủ đề, nhưng phần kiến thức áp dụng tập trung riêng vào chủ đề tương ứng. Thư mục dùng cách viết `implementation`.

## Bắt đầu

1. Đọc [kiểm kê](docs/INVENTORY.md) và [task list](docs/TASKS.md).
2. Chọn chủ đề và điền slide outline/speaker notes.
3. Điền mapping và implementation từ source project đang cài.
4. Hoàn thiện runbook, chạy demo và lưu evidence trước khi đánh dấu task hoàn thành.

## Trạng thái

Đã tạo khung tài liệu cho 6 chủ đề và 10 project slots. Slide, mapping chi tiết và runbook trong từng slot là khung cần hoàn thiện. Đã copy project gốc vào `source/` của đủ 10 project slots. Git metadata bên trong các bản copy đã được xóa để quản lý bằng một repo chung; không dùng submodule. Working files và thay đổi local giữ nguyên. `SOURCE-NOTES.md` ghi nguồn gốc. Các thư mục gốc vẫn giữ nguyên. Bản copy chưa được khởi động/kiểm chứng lại; cấu hình tuyệt đối hoặc port có thể còn trỏ theo môi trường gốc. Repo chưa có remote GitHub và chưa được publish. AnonBlog đã được loại khỏi phạm vi.

## Nguồn repository

Xem [REPOSITORIES.md](REPOSITORIES.md) để biết remote URL, branch và commit của từng bản project trước khi loại bỏ Git metadata.
