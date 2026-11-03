# Đối chiếu slide cũ với yêu cầu phần Toàn

Đầu vào là hai PDF ngoài repo, notes/generator tương ứng; yêu cầu từ TEAM-ASSIGNMENT mục 7/10, tasks E01–E11/H và chỉ dẫn đổi JAMstack sang ScriptHammer. Mẫu bắt buộc là Technology Consulting by Slidesgo trong thư mục jamstack-architecture.

| Hạng mục | Trước cập nhật | Thay đổi đúng phạm vi |
|---|---|---|
| Mẫu | Hai template có cùng SHA-256; giữ mẫu, sơ đồ và 4+1 | Dùng cùng tệp mẫu từ bộ JAMstack cho bản bàn giao; không đổi phong cách |
| MFE host/remote/state/load/failure/shared | Đã có trong 29 trang | Giữ các nội dung và notes; bổ sung tài liệu mapping/sequence để đọc |
| MFE runtime/deploy boundary | Slide tập trung ba dev server; tài liệu repo nói Compose/Nginx | Thêm trang 25 dạng sơ đồ, phân biệt nguồn chính với bản copy; deck thành 30 trang |
| JAMstack và hệ thống | 32 trang đã phân tích ScriptHammer, repo ôn thi vẫn ghi Blog Starter | Đồng bộ repo/ma trận/phân công sang ScriptHammer; giữ bộ phân tích đã có |
| CSR/SSR/SSG/ISR | Chưa có bảng so sánh rõ bốn mode | Thêm trang 10: thời điểm tạo HTML và mode thực có |
| Pipeline nội dung | Có nhắc JSON/generateStaticParams nhưng chưa đi từ Markdown | Thêm trang 11 có diagram MD → generator → JSON → routes → export; nhấn generator chưa tự gọi |
| Rebuild/cache | Có nguyên lý và cache tổng quát, thiếu kịch bản nội dung A/B | Thêm trang 12: sửa nguồn → sinh JSON/build → publish/đối chiếu cache; deck thành 35 trang |
| Production/runtime evidence | Slide cũ là static inspection | Giữ giới hạn đó; Toàn đã chạy nhưng chưa đối chiếu log. Không tạo build/Network evidence giả |
| Ôn tập và thời lượng | Deck dài 20–30 phút mỗi bộ; khung repo chưa điền | Notes theo trang + lộ trình 8 trang chính; 10 câu hỏi mỗi chủ đề |

Trang thêm có action title, nguồn, notes và sơ đồ/bảng cùng phong cách cũ. Các trang cũ được đánh số lại tự động; mapping và outline theo số trang sau cập nhật.

Preflight/dry run/render/QA của agent-slides đã thành công. PowerPoint mở/render đủ trang và xuất PDF, kiểm tra tràn chữ/chồng hộp chữ bằng 0. Đã xem PNG các trang bổ sung và contact sheet. Báo cáo lint còn warning được giải thích trong quality-review, không tự coi mọi cảnh báo là lỗi nội dung.

Không thêm tính năng ứng dụng, triển khai mới, benchmark, security audit hoặc nội dung của thành viên khác.
