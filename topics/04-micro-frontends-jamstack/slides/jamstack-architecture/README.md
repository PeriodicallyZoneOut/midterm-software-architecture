# Kiến trúc JAMstack — Phân tích ScriptHammer

Mở [PowerPoint](output/jamstack-architecture.pptx) để trình bày hoặc chỉnh sửa. Có kèm [PDF](output/jamstack-architecture.pdf), [ảnh tổng quan](output/contact-sheet.png) và [ghi chú thuyết trình](speaker-notes.md).

Bộ trình chiếu có **35 trang tiếng Việt**, dự kiến 25–30 phút chưa tính thảo luận. Nội dung giới thiệu JAMstack rồi phân tích ScriptHammer theo **4+1 góc nhìn**, tập trung vào ranh giới build/runtime, API, dữ liệu, quyền truy cập và triển khai.

Dùng trực tiếp mẫu **Technology Consulting by Slidesgo** trong thư mục này: giữ hình vector bìa, họa tiết đường nối/nút tròn, trang chia phần, nền nhấn kết luận và trang Cảm ơn. Có sáu bố cục gốc, không dùng BLANK. Hộp, mũi tên và nhãn trong các sơ đồ là đối tượng PowerPoint có thể chỉnh sửa. Tệp mẫu đầu vào được giữ nguyên; phông nội dung hỗ trợ dấu tiếng Việt.

| Trang | Nội dung |
|---|---|
| 1–5 | JAMstack, hai luồng build/runtime, JavaScript–APIs–Markup, đánh đổi |
| 10–12 | CSR/SSR/SSG/ISR, pipeline Markdown → JSON → HTML, rebuild/cache |
| 6–9 | Phạm vi ScriptHammer, sơ đồ hệ thống và bằng chứng static export |
| 13–15 | Mô hình 4+1, góc nhìn logic và ranh giới tin cậy |
| 16–17 | Góc nhìn phát triển: mã nguồn, đầu ra và pipeline |
| 18–21 | Góc nhìn tiến trình: auth, tin nhắn, offline, thanh toán/webhook |
| 22–23 | Góc nhìn vật lý: nơi dựng, nơi chạy, đơn vị triển khai |
| 24–25 | Góc nhìn +1: ca sử dụng và truy vết thanh toán |
| 26–30 | Thuộc tính chất lượng, bảo mật, .NET provider, quyết định và đề xuất |
| 31–35 | Gợi ý trình diễn, kết luận, tham khảo, bản đồ mã và Cảm ơn |

Kiến trúc chính theo cấu hình **Supabase mặc định**. Nhánh .NET chỉ là tùy chọn cho messaging; slide không giả định nó đang được triển khai. Mã hiện tại được ưu tiên hơn các mô tả cũ. Chẳng hạn, Docker có thể cấp cổng host tự động, hàng đợi pending có nội dung rõ và đường sync vẫn gọi Supabase trực tiếp.

Phạm vi là **rà soát mã tĩnh**. Không chạy build/test của ScriptHammer, không gọi backend, không thực hiện thanh toán và không xác minh bản triển khai trực tuyến. Bộ slide và ghi chú được dựng, kiểm tra kỹ thuật và render riêng. Xem [bản rà soát kiến trúc](architecture-review.md).

## Dựng lại tài liệu

Cần `uv` và Python 3.12+ do uv quản lý. Lấy công cụ theo [hướng dẫn chung](../README.md) trước lần dựng đầu tiên. Công cụ [mpuig/agent-slides](https://github.com/mpuig/agent-slides) ở `tools/agent-slides`, commit `820782a5fb8cb8f251d7c0750e4299c321cd068c`.

```powershell
uv run --project tools/agent-slides python build_deck.py
uv run --project tools/agent-slides python validate_deck.py
```

Trên Windows có Microsoft PowerPoint, chạy toàn bộ luồng dựng, QA, xuất PDF/ảnh và kiểm tra hình học:

```powershell
./rebuild.ps1
```

Nếu cần trích xuất lại mẫu trước khi dựng:

```powershell
uv run --project tools/agent-slides slides extract 'Technology Consulting  by Slidesgo.pptx' --output-dir project --base-template-out project/base_template.pptx --compact
```

Các tệp quan trọng:

- `build_deck.py`: nội dung và sơ đồ của 32 trang.
- `deck_drawing.py`: đối tượng vector, bố cục mẫu và định dạng tiếng Việt.
- `slides.json`: kế hoạch và thao tác dựng bằng agent-slides.
- `project/`: hợp đồng bố cục và bản mẫu đã trích xuất.
- `output/`: PPTX, PDF, ảnh, bằng chứng và báo cáo kiểm tra.
- `output/template-layout-map.json`: đối chiếu trang với bố cục gốc.
- `quality-review.md`: kết quả kiểm tra và giải thích cảnh báo heuristic.

Ghi công: Slidesgo, Flaticon, Freepik, Stories; nguồn phân tích là ScriptHammer; công cụ agent-slides của Marc Puig. Hai deck được cập nhật theo cùng phạm vi ôn tập của Toàn.

## Cập nhật ôn thi 03/11/2026

Đối chiếu task list của Toàn; không chạy lại ứng dụng. Toàn cho biết demo đã chạy trước đó, chưa đối chiếu log runtime. Bổ sung sơ đồ và kiến thức còn thiếu; source/notes/PDF trong repo ôn thi là bản dùng để review PR.
