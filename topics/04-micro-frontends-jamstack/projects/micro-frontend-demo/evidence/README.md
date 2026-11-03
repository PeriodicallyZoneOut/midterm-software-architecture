# Evidence MFE

[source-inspection.md](source-inspection.md) là bằng chứng đọc code: snapshot/commit, SHA-256 và trích đoạn có số dòng. Đây không phải log runtime. QA trong thư mục slides chỉ kiểm chứng slide mở/render được.

Toàn đã chạy demo trước lượt này; chưa nhận log/ảnh để đối chiếu các ca riêng. Khi xem lại evidence cá nhân, cần có: ngày chạy, working directory/commit, config URL, phiên bản công cụ, Network remoteEntry/chunks, add/remove và refresh, failure/fallback, phiên bản remote B nếu kết luận phát hành độc lập. Ghi expected/actual, vị trí ảnh/log và giới hạn; lọc cookie/token/dữ liệu cá nhân trước khi đưa vào repo.

Không tạo ảnh giao diện giả, không dùng ảnh upstream làm bằng chứng phiên chạy. [Runbook](../demo/runbook.md) là hướng dẫn thao tác.
