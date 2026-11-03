# Kiểm tra chất lượng slide — micro-frontend

Bản cập nhật 03/11/2026: **30 trang tiếng Việt**, mẫu Technology Consulting by Slidesgo, giữ sơ đồ vector, 6 layout gốc, bìa và ghi công.

- Preflight, dry run, render và QA agent-slides: thành công.
- PowerPoint mở/render đủ 30 trang, xuất PDF/PNG thành công.
- Tràn chữ: 0; chồng hộp chữ: 0; run chữ nhỏ hơn 9pt: 0; unresolved token: 0.
- Mỗi slide có notes và nguồn. Kiểm tra các trang bổ sung qua PNG và contact sheet.

## Cảnh báo heuristic

Lint có 46 cảnh báo, không có lỗi; không tắt lint hoặc đổi threshold.

| Mã | Số | Diễn giải |
|---|---|---|
| SHAPE_OUT_OF_BOUNDS | 1 | Nhóm hình bìa nguyên bản chạm mép theo mẫu. |
| VISUAL_IMBALANCE_RISK | 11 | Bảng/sơ đồ và layout mẫu phân bố theo nội dung. |
| SHAPE_OVERLAP | 24 | Bao gồm chữ đặt trên khối; text-to-text kiểm tra riêng bằng 0. |
| LOW_TEXT_CONTRAST_RISK | 10 | Heuristic so với nền trắng, kể cả chữ trắng trên khối xanh. |

Preflight thiếu hai bộ xuất tùy chọn LibreOffice/pdftoppm; PDF/PNG được xuất bằng PowerPoint. Đây là QA tài liệu, không phải kết quả build/test/runtime của ứng dụng.
