# Micro-Frontend: kiến thức để giải thích demo

Micro-Frontend chia một frontend thành các năng lực nghiệp vụ có quyền sở hữu và vòng đời phát hành riêng. Trong demo, MAIN là shell/host, PRODUCTS quản lý danh mục, CART quản lý giỏ và checkout. Source cho thấy ranh giới chức năng; không chứng minh tổ chức có ba nhóm hoặc đã deploy riêng.

## So sánh để chọn kiến trúc

| Cách tổ chức | Ghép mã lúc nào | Khi đổi tính năng | Chi phí |
|---|---|---|---|
| SPA nguyên khối | Cùng build | Thường phát hành lại bundle chung | Phối hợp phát hành; runtime đơn giản |
| Thư viện component | Import lúc build bên dùng | Nâng phiên bản rồi rebuild bên dùng | Quản lý API package; không có remote runtime |
| MFE runtime như demo | Browser tải remote lúc chạy | Có thể đổi URL/build remote tương thích | Tải mạng, lỗi remote, hợp đồng và version |

MFE phù hợp khi tự chủ tính năng/phát hành có giá trị hơn chi phí tích hợp. Không cần MFE chỉ vì giao diện có nhiều component. Demo cùng dùng React; MFE không bắt buộc đa framework.

## Module Federation trong mã thật

- **Host:** MAIN có `remotes: {}` trong Webpack nhưng dùng custom loader để tải remote động; không được suy ra host không dùng federation từ object rỗng này.
- **Remote:** Webpack tạo container có tên `PRODUCTS` hoặc `CART`, manifest entry là `remoteEntry.js`.
- **Exposes:** PRODUCTS công bố `./ProductsList`, `./ProductCard`, `./products`; CART công bố `./Cart`, `./CheckoutPage`. Tên container và tên expose tạo hợp đồng mà loader phải dùng đúng.
- **Shared:** cấu hình trải `dependencies`, rồi cấu hình riêng React/React DOM với `singleton`, `eager`, `requiredVersion`. Share scope cho các container trao đổi dependency runtime. Singleton giảm bản React trùng nhưng vẫn cần tương thích API; không bảo đảm mọi dependency chỉ có một bản.
- **Runtime composition:** loader nạp script, khởi tạo share scope/container, lấy factory rồi trả module cho React.lazy. Chia build không tạo process hoặc sandbox browser riêng.

## State ownership và liên kết giữa các phần

CART là nơi được quyền sửa giỏ. PRODUCTS phát `addItem`/`removeItem`; CART nhận, sửa Zustand, phát `cart` snapshot và ghi `fruit-shop-cart`. Host giữ registry URL ở `fruit-remotes`. PubSub do MAIN tạo trên `window.fsEvents`, gọi callback đồng bộ, chỉ giữ snapshot cuối của topic được chọn trong RAM. Nó không có ACK, retry bền hoặc giao tiếp qua mạng.

localStorage thuộc origin trang host; remote tải từ cổng khác vẫn chạy trong trang host. Không có đồng bộ giỏ nhiều thiết bị, server source of truth hay transaction DB. Số tiền checkout chỉ là phép tính UI từ bảng giá import vào bundle CART; chưa có đặt hàng/thanh toán backend.

## Lợi ích và đánh đổi cần nêu

Tải runtime cho phép chọn nơi cấp UI và đặt trách nhiệm state rõ. Đổi lại phải quản lý contract event, exposed module, shared version, CSS/UX và lỗi tải. Cart còn import trực tiếp helper MAIN và bảng giá PRODUCTS: đây là coupling lúc build, hạn chế phát hành độc lập. ErrorBoundary/Suspense giúp UI báo lỗi/chờ, nhưng không ngăn remote truy cập biến toàn cục hoặc dữ liệu origin. Chỉ dùng URL remote đáng tin là điều kiện của thiết kế, không phải một control đã được kiểm chứng trong demo.

Nguồn cụ thể: `main/webpack.config.js`, `products/webpack.config.js`, `cart/webpack.config.js`, `main/src/utils/index.ts`, `main/src/services/pubsub.ts`, `cart/src/store/index.ts`. Bản đồ đầy đủ ở [mapping](02-component-mapping.md); [câu hỏi ôn](../../../oral-questions.md).
