# Runbook nhắc demo MFE đã chuẩn bị

**Không thực thi các bước này trong lượt tạo tài liệu.** Toàn cho biết demo đã chạy. Chỉ dùng runbook để diễn tập/đối chiếu bằng chứng cá nhân, không thay môi trường đã chạy bằng bản copy khác.

## Môi trường và điểm mở

Working directory: `<workspace>/micro-frontend-demo`. Package manager `yarn@3.6.1`; root khai báo Node >=16, npm >=8, đây là yêu cầu trong source chứ không xác nhận phiên bản trên máy. Dùng dependency đã chuẩn bị; nếu dựng môi trường mới, theo README/lockfile của đúng snapshot. Không ghi secret hoặc env thực vào report.

Lệnh trong source để nhớ: `yarn start` (Turbo start ba workspace), `yarn build` (build ba workspace). Không có Compose ở source chính. MAIN `http://localhost:9001`, PRODUCTS `http://localhost:9002`, CART `http://localhost:9003`; hai remote entry là `:9002/remoteEntry.js` và `:9003/remoteEntry.js`. URL thực có thể đã đổi theo môi trường Toàn.

## Kịch bản ngắn và expected

| Bước | Thao tác trên phiên của Toàn | Expected / ý nghĩa | Evidence cần đối chiếu |
|---|---|---|---|
| 0 | Xác nhận đúng working directory/commit và URL đang dùng | Không nhầm bản copy Docker | Phiên bản, cấu hình đã lọc |
| 1 | Mở MAIN; DevTools Network trước khi reload | Thấy HTTP remoteEntry/chunks của PRODUCTS/CART | Network capture; tránh cache che lần tải |
| 2 | Add một loại hai lần, giảm một lần, xóa | Count và UI đồng nhất theo store CART | Ảnh/video; ProductCard và store |
| 3 | Thêm hàng rồi refresh cùng origin | Giỏ phục hồi từ `fruit-shop-cart` | Trước/sau refresh; storage đã lọc |
| 4 | Mở `/checkout` | Danh sách và tổng tiền, chưa có giao dịch | Ảnh + chỉ priceMap trong code |
| 5 | Nếu đã chuẩn bị remote B, đổi URL qua RemoteControls + Reload | UI có thể đổi; ghi host có rebuild không | URL/build version B, Network, host version |
| 6 | Dùng DevTools chặn remote trước lần tải hoặc URL lỗi đã chuẩn bị | Quan sát actual loading/fallback và phần UI còn dùng được | Ảnh lỗi + vùng hoạt động; không suy luận trước |

Readiness cần kiểm tra trong phiên thật: host mở được, hai remote trả entry và chunks hợp lệ, add/remove phản ánh đúng. HTTP 200 một mình chưa xác nhận UI nghiệp vụ.

## Recovery và dừng

Gỡ Network blocking; khôi phục URL remote đã ghi trước khi thử; chọn Reload. `window` container/cached JS có thể che lỗi remote nếu chặn sau khi đã nạp. Không xóa `fruit-shop-cart` để sửa URL; reset URL khác reset giỏ. Nếu terminal start do mình mở, Ctrl+C dừng dev servers, dữ liệu localStorage vẫn ở browser. Không dừng container hoặc tiến trình của người khác.

Nếu không có build B đã chuẩn bị, trình bày cơ chế và giới hạn từ code, giữ mục phát hành độc lập chưa xác nhận. Không cần tạo thêm deployment chỉ cho lượt tài liệu này. [Evidence](../evidence/README.md).
