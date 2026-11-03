# Evidence JAMstack

[source-inspection.md](source-inspection.md) chứa commit/package version, hash và trích code config/generator/routes/workflow. Các mẩu source chứng minh thiết kế, không chứng minh build/HTTP/backend hiện hoạt động.

Toàn đã chạy demo; lượt này không chạy lại hoặc tạo log thay thế. Để đối chiếu phiên cá nhân, tìm: build log production, route HTML/assets đúng snapshot, MD/JSON/HTML A và B cùng hash/timestamp, artifact/hosting URL thực, trạng thái cache/SW, Network API đã lọc token. Dev server và `.next/dev` không đủ chứng minh export production. Nếu chưa có evidence cho một ca, giữ ca đó chưa xác nhận.

Không đưa `.env`, JWT, cookie, private/service-role key, OAuth secret hoặc dữ liệu người dùng thật vào report. Không phát sinh thanh toán/gọi backend chỉ để lấp evidence. [Runbook](../demo/runbook.md) ghi expected và cách recovery.
