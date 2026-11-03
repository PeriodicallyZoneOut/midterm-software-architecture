# Kiểm chứng và đánh đổi MFE

**Đã làm ở lượt này:** đọc source chính, xác nhận commit/working tree, trích code và đối chiếu sơ đồ. **Thông tin từ Toàn:** demo đã được chạy trước đó. Không có log/ảnh phiên đó trong đầu vào để xác nhận từng kịch bản. Không khởi động hoặc build lại app.

| Nội dung | Cách đối chiếu phiên đã chạy | Expected theo mã | Actual / evidence lượt này |
|---|---|---|---|
| Runtime composition | Network `remoteEntry.js` và chunks | MAIN tải PRODUCTS/CART khi cần | Source loader; chưa có capture Network |
| State ownership | Add/bớt mặt hàng, theo số đếm | CART sửa Zustand; snapshot cập nhật UI | Source store + ProductCard |
| Persistence | So sánh trước/sau refresh cùng origin | Giữ giỏ theo localStorage hợp lệ | Source getLocalState; chưa có ảnh trước/sau |
| Failure | Chặn remote trước khi tải, tránh cache/container cũ | Loading hoặc fallback vùng React; không có timeout bảo đảm | Source ErrorBoundary/loader; chưa có actual |
| Đổi bản remote | URL remote build B tương thích + Reload | Host có thể nạp UI B, giá CART vẫn theo bundle | Có cơ chế đổi URL; chưa chứng minh deploy độc lập |
| Production deployment | Manifest/image/URL của phiên thật | Phân biệt dev server và bản copy Nginx | Chỉ xác nhận file cấu hình tồn tại ở bản copy |

## Ba đánh đổi để trả lời vấn đáp

1. **Tải mã động ↔ độ sẵn sàng và tin cậy.** Lỗi mạng/remote làm mất feature; remote chạy cùng trang. Suspense/ErrorBoundary giảm gián đoạn UI trong phạm vi React, không bảo vệ khỏi mọi tác động của mã remote.
2. **Shared runtime ↔ tương thích phiên bản.** React singleton giảm trùng runtime nhưng cần kiểm soát version/contract. Không suy luận `singleton` nghĩa là mọi tổ hợp version đều chạy.
3. **Bus và state owner ↔ contract/vòng đời.** PubSub giảm import trực tiếp giữa UI, song payload và thời điểm subscribe trở thành dependency. Không có durable queue; callback đồng bộ có thể ảnh hưởng bên phát.

## Giới hạn cần nhớ

Không có backend/cart DB/auth/payment thật; chưa benchmark; chưa kiểm chứng ba pipeline phát hành độc lập. Cổng CART mặc định trong một số config, replay `{}` và tải đồng thời là rủi ro tĩnh có điều kiện. Tài liệu không sửa các rủi ro này vì yêu cầu là inspection và chuẩn bị thi. [Runbook](../demo/runbook.md) ghi cách đối chiếu/khôi phục, [evidence](../evidence/README.md) phân biệt code với runtime.
