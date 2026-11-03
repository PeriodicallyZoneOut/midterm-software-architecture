# Hai bộ slide tiếng Việt của Toàn

| Chủ đề | PDF | Bản gốc chỉnh sửa | Speaker notes |
|---|---|---|---|
| Micro-Frontend — 30 trang | [PDF](micro-frontend-architecture/output/micro-frontend-architecture.pdf) | [PPTX](micro-frontend-architecture/output/micro-frontend-architecture.pptx) | [Notes từng trang](micro-frontend-architecture/speaker-notes.md) |
| JAMstack / ScriptHammer — 35 trang | [PDF](jamstack-architecture/output/jamstack-architecture.pdf) | [PPTX](jamstack-architecture/output/jamstack-architecture.pptx) | [Notes từng trang](jamstack-architecture/speaker-notes.md) |

[Đối chiếu khoảng trống](gap-review.md) · [Dàn ý 8 trang trình bày chính](outline.md) · [Ghi chú trình bày ngắn](speaker-notes.md).

Hai deck dài giữ phân tích 4+1 và sơ đồ cũ để học/hỏi sâu. Task list gợi ý 6–8 slide cho cả hai chủ đề; lộ trình 8 trang lấy từ hai deck có sẵn, không bắt trình chiếu toàn bộ 65 trang.

Trong workspace, PDF cũng được xuất đúng vị trí yêu cầu: `micro-frontend-architecture/output/micro-frontend-architecture.pdf` và `jamstack-architecture/output/jamstack-architecture.pdf`. Các bản ở đây có cùng SHA-256 với hai PDF đó; xem [delivery-manifest.json](delivery-manifest.json).

## Mẫu và nguồn dựng

Dùng mẫu `jamstack-architecture/Technology Consulting  by Slidesgo.pptx` cho cả hai; bản MFE cũ có cùng hash. Mỗi thư mục deck chứa tệp mẫu, `build_deck.py`, `deck_drawing.py`, `slides.json`, hợp đồng `project/`, asset và scripts QA/export. Các sơ đồ dùng shape/text vector có thể sửa trong PPTX.

Công cụ: [mpuig/agent-slides](https://github.com/mpuig/agent-slides), commit `820782a5fb8cb8f251d7c0750e4299c321cd068c`. Đã dùng workflow slides-build: inspect contract → preflight → dry run → render → QA → export PowerPoint → kiểm tra hình học. Không chạy hệ thống demo.

## Dựng lại slide trên Windows

Thực hiện trong một trong hai thư mục deck. Cần `uv`, Git, Python 3.12+ theo dự án agent-slides và Microsoft PowerPoint để xuất PDF/PNG. Lần đầu lấy công cụ vào thư mục không được commit:

```powershell
git clone https://github.com/mpuig/agent-slides tools/agent-slides
git -C tools/agent-slides checkout 820782a5fb8cb8f251d7c0750e4299c321cd068c
./rebuild.ps1
```

`rebuild.ps1` chỉ dựng tài liệu. Script không khởi động/build micro-frontend-demo hoặc ScriptHammer. `slides.json` và profile được tái tạo từ generator; asset roots trong profile được cập nhật theo vị trí checkout. Nếu cần kiểm tra thủ công các bước, xem README của từng deck. `project/` là hợp đồng mẫu đã trích; không cần trích lại khi chỉ đổi nội dung.

## Kết quả kiểm tra

Hai deck đều có QA `ok: true`, PowerPoint mở đủ 30/35 trang, tràn chữ 0, chồng hộp chữ 0. Lint còn cảnh báo heuristic về artwork gốc/khối chứa chữ/bố cục và màu nền; xem `quality-review.md` của mỗi deck, không coi lint là hoàn toàn sạch. QA này không xác nhận runtime, production build hoặc backend của hai ứng dụng.
