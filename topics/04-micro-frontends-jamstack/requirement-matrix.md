# Ma trận yêu cầu phần Toàn

Nguồn: [phân công mục 7, mục 10](../../docs/TEAM-ASSIGNMENT.md), [tasks E01–E11, H01–H07](../../docs/TASKS.md) và chỉ dẫn thay Blog Starter bằng ScriptHammer. Chỉ đóng phần tài liệu đã có bằng chứng; deployment không được xác nhận lại trong lượt này.

| Yêu cầu | Tài liệu / code để trả lời | Slide sau cập nhật | Trạng thái |
|---|---|---|---|
| E01: domain, composition, host/remote/exposes/shared, trade-off | MFE concepts; mapping Webpack | MFE 2–5, 11, 21 | Đã bổ sung tài liệu |
| E02: remote tải lúc chạy, build/deploy boundary | MFE implementation; runbook; bản copy Docker được phân biệt | MFE 13, 16–17, 25 | Có code evidence; runtime chưa đối chiếu |
| E03: loader sequence | `loadComponent`, `fetchRemote`, share scope, container factory | MFE 13 | Đã có sơ đồ + lời giải thích |
| E04: add/remove, state owner, snapshot, persistence | ProductCard → PubSub → store → localStorage | MFE 14–15 | Đã có sơ đồ + lời giải thích |
| E05: remote unavailable, đổi bản remote, giới hạn tự chủ | MFE verification và runbook | MFE 20, 22–23, 26 | Có hướng dẫn; chưa có actual/log mới |
| E06: JAM; build/request time; CSR/SSR/SSG/ISR | ScriptHammer concepts và bảng mode | JAM 2–5, 10 | Đã bổ sung phần còn thiếu |
| E07: production export evidence | `next.config.ts`, deploy workflow; evidence README | JAM 9, 22–23 | Xác nhận cấu hình; không tạo log build app |
| E08: pipeline nội dung | `public/blog` → `generate:blog` → JSON → routes → export | JAM 11 | Đã thay pipeline Blog Starter bằng pipeline thật |
| E09: vòng đời nội dung/rebuild/cache | ScriptHammer implementation, runbook | JAM 12 | Có expected và điểm đọc artifact; chưa chạy lại |
| E10: hosting thực | Runner build; artifact/Pages phục vụ; Supabase xử lý API | JAM 22–23 | Phân tích cấu hình; chưa xác minh URL triển khai |
| E11 cũ: ScriptHammer là demo phụ | Lựa chọn mới: ScriptHammer là demo chính | Toàn bộ JAM | Đã thay theo chỉ dẫn người dùng |
| H01: notes và sơ đồ có giải thích | Hai bộ implementation + speaker notes theo từng slide | Cả hai deck | Đã hoàn thiện |
| H02 / bàn giao: 8–10 câu mỗi chủ đề | [10 câu MFE + 10 câu JAMstack](oral-questions.md) | Tra cứu khi ôn | Đã hoàn thiện |
| Runbook/evidence | `projects/*/demo`, `projects/*/evidence` | MFE 26; JAM 31 | Đã viết; không điền giả kết quả runtime |
| PDF + bản gốc + kiểm tra mở | `slides/*/output`, QA và PowerPoint report | 30 trang MFE; 35 trang JAM | Xem báo cáo QA được bàn giao |

Các checkbox E02/E05/E07/E09 trong task list giữ mở vì bao gồm việc chạy/thu evidence, dù phần hướng dẫn đã hoàn thiện. Không cập nhật trạng thái của thành viên hoặc chủ đề khác.
