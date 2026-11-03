# Trình chiếu kiến trúc Micro-frontend

Mở [bản PowerPoint](output/micro-frontend-architecture.pptx) để trình bày hoặc chỉnh sửa. Có kèm [bản PDF](output/micro-frontend-architecture.pdf), [ảnh tổng quan các trang](output/contact-sheet.png) và [ghi chú thuyết trình](speaker-notes.md).

Bản hiện tại có **30 trang bằng tiếng Việt**, dành cho môn Kiến trúc phần mềm, dự kiến 20–25 phút chưa tính thảo luận. Nội dung bắt đầu từ khái niệm chung rồi phân tích demo theo đủ **4+1 góc nhìn**. Tên API, mô-đun, biến và đường dẫn giữ theo mã nguồn.

Mẫu được sử dụng trực tiếp là **Technology Consulting by Slidesgo.pptx** trong thư mục này. Bản trình chiếu giữ hình minh họa vector gốc ở trang bìa, các đường nối và nút tròn trang trí, bố cục chia phần, nền nhấn thông điệp và trang Cảm ơn. Có sáu bố cục gốc được dùng: `TITLE`, `TITLE_ONLY`, `TITLE_AND_BODY_1`, `SECTION_HEADER`, `MAIN_POINT`, `CUSTOM_9`. Không dùng bố cục BLANK. Các sơ đồ và nhãn vẫn là đối tượng PowerPoint có thể chỉnh sửa. Phông Aptos hỗ trợ dấu tiếng Việt; dòng ghi công đã dịch nhưng giữ liên kết đến tác giả tài nguyên. Tệp mẫu gốc được giữ nguyên.

| Trang | Nội dung |
|---|---|
| 1–5 | Khái niệm, phân rã, cách tích hợp và đánh đổi |
| 6–8 | Phạm vi demo và sơ đồ hệ thống hiện tại |
| 9–11 | Mô hình 4+1, góc nhìn logic và hợp đồng mô-đun |
| 12 | Góc nhìn phát triển: workspaces và phụ thuộc nguồn |
| 13–15 | Góc nhìn tiến trình: tải mã, sự kiện và trạng thái |
| 16–17 | Góc nhìn vật lý: máy chủ phục vụ mã và chọn URL |
| 18–19 | Góc nhìn +1: kịch bản và đối chiếu bốn góc nhìn |
| 20–24 | Xử lý lỗi, quyết định kiến trúc, rủi ro và đề xuất |
| 25–30 | Phân biệt hai bản source, trình diễn, kết luận, tham khảo, bằng chứng và Cảm ơn |

[Bản rà soát kiến trúc](architecture-review.md) giải thích các nhận định. Đây là phân tích mã tĩnh; ứng dụng và bản triển khai trực tuyến chưa được chạy kiểm tra. Ảnh giao diện lấy từ `docs/demo.png`. Các đề xuất được ghi rõ và chưa áp dụng vào ứng dụng.

## Dựng lại

Lấy công cụ theo [hướng dẫn chung](../README.md) trước lần dựng đầu tiên. Cần `uv` và Python 3.12+ do uv quản lý. [mpuig/agent-slides](https://github.com/mpuig/agent-slides) nằm tại `tools/agent-slides`, commit `820782a5fb8cb8f251d7c0750e4299c321cd068c`. Công cụ thực hiện preflight, dry run, render, kiểm tra kế hoạch, lint và QA.

```powershell
uv run --project tools/agent-slides python build_deck.py
uv run --project tools/agent-slides python validate_deck.py
```

Trên Windows có Microsoft PowerPoint, xuất PDF, ảnh và kiểm tra tràn chữ:

```powershell
./export-slides.ps1
uv run --project tools/agent-slides python check_artifacts.py
```

Hoặc chạy `./rebuild.ps1` để thực hiện toàn bộ. Các lệnh chạy trong thư mục này. Có thể trích xuất lại mẫu trước khi dựng:

```powershell
uv run --project tools/agent-slides slides extract 'Technology Consulting  by Slidesgo.pptx' --output-dir project --base-template-out project/base_template.pptx --compact
```

`build_deck.py` chứa nội dung tiếng Việt; `deck_drawing.py` tạo sơ đồ, đặt nội dung trong vùng trống của bố cục và dịch dòng ghi công trên bản mẫu đã trích xuất. Mẫu đầu vào gốc không bị sửa. Ghi chú được nhúng trong từng trang và xuất riêng thành Markdown.

## Kiểm tra đầu ra

Agent-slides QA đạt yêu cầu. PowerPoint đã mở, render đủ 30 trang và xuất PDF; không phát hiện tràn chữ. Kiểm tra hình học không phát hiện hộp chữ chồng nhau. Báo cáo cũng xác nhận nội dung ghi chú tiếng Việt, sáu bố cục mẫu và hình minh họa gốc ở bìa. Chi tiết cảnh báo heuristic được ghi tại [báo cáo chất lượng](quality-review.md).

Các tệp chính:

- `output/`: PPTX, PDF, ảnh từng trang, ảnh tổng quan và báo cáo kiểm tra.
- `slides.json`: kế hoạch và thao tác dựng bằng agent-slides.
- `project/`: bản mẫu trích xuất, hợp đồng bố cục và cấu hình thiết kế.
- `speaker-notes.md`: ghi chú thuyết trình tiếng Việt.
- `output/template-layout-map.json`: đối chiếu từng trang với bố cục mẫu gốc.

Ghi công: Slidesgo; Flaticon; Freepik; Stories; mã và ảnh từ micro-frontend-demo; công cụ agent-slides của Marc Puig.

## Cập nhật ôn thi 03/11/2026

Đối chiếu task list của Toàn; không chạy lại ứng dụng. Toàn cho biết demo đã chạy trước đó, chưa đối chiếu log runtime. Bổ sung sơ đồ và kiến thức còn thiếu; source/notes/PDF trong repo ôn thi là bản dùng để review PR.
