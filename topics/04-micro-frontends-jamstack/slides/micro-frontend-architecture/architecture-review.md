# Rà soát kiến trúc micro-frontend-demo

Commit đã đọc: `9a4d33596453d2d76da9d8ebb0b5c9249a0a024d`. Đây là phân tích mã tĩnh, không phải kiểm thử ứng dụng hoặc đánh giá triển khai sản xuất.

Demo có ba bản dựng Webpack: `main`, `products`, `cart`. MAIN tải mô-đun từ xa để ghép giao diện React. Cart sở hữu trạng thái Zustand; Products và Cart tương tác qua bus PubSub đồng bộ do host cung cấp. Tách bản dựng tạo nền tảng cho phát hành riêng, nhưng import chéo mã nguồn làm giảm tính độc lập.

## Bằng chứng cho mô hình 4+1

| Góc nhìn | Nội dung | Mã nguồn |
|---|---|---|
| Logic | Trách nhiệm của host, danh mục và giỏ | [App](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/src/App.tsx), [StoreHeader](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/src/components/StoreHeader/index.tsx), [ProductCard](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/products/src/components/ProductCard/index.tsx) |
| Phát triển | Tổ chức workspace và phụ thuộc nguồn | [package.json](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/package.json), [CheckoutPage](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/cart/src/features/checkout/index.tsx), [CheckoutPanel](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/cart/src/components/CheckoutPanel/index.tsx) |
| Tiến trình | Tải mã bất đồng bộ; gọi sự kiện đồng bộ | [RemoteComponent](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/src/components/RemoteComponent/index.tsx), [loader](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/src/utils/index.ts), [PubSub](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/src/services/pubsub.ts) |
| Vật lý | Ba máy chủ phục vụ tệp; một trang trình duyệt thực thi | [MAIN](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/webpack.config.js), [PRODUCTS](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/products/webpack.config.js), [CART](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/cart/webpack.config.js) |
| +1 Kịch bản | Xem danh mục, sửa giỏ, checkout, reload, đổi URL | [Cart store](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/cart/src/store/index.ts), [RemoteControls](https://github.com/rautio/micro-frontend-demo/blob/9a4d33596453d2d76da9d8ebb0b5c9249a0a024d/main/src/components/RemoteControls/index.tsx) |

Ba máy chủ phát triển không đồng nghĩa ba môi trường thực thi giao diện được cô lập. Các mô-đun chạy chung trong tài liệu của host.

## Hợp đồng tích hợp

PRODUCTS expose `./ProductsList`, `./ProductCard`, `./products`; CART expose `./Cart`, `./CheckoutPage`. MAIN tải ProductsList tại `/`, CheckoutPage tại `/checkout` và Cart trong đầu trang. Cart dựng ProductCard ở ngăn giỏ và checkout.

Các lệnh là `addItem`, `removeItem`; snapshot là `cart` với payload `{ cart: [...] }`. PubSub gọi subscriber đồng bộ. Cart lưu dữ liệu dưới khóa `fruit-shop-cart`; host lưu URL dưới `fruit-remotes`. Replay của bus chỉ tồn tại trong bộ nhớ, không phải lưu bền. localStorage thuộc origin trang host.

## Nhận định quan trọng

| Nhận định | Bằng chứng cụ thể | Hệ quả |
|---|---|---|
| Import chéo nguồn | Checkout dòng 5 và 10; CheckoutPanel dòng 6 và 11 | Cart phụ thuộc helper từ main và dữ liệu từ products. Nên quản lý hợp đồng/gói dùng chung có phiên bản. |
| Bảng giá gắn vào bản Cart | Checkout tạo priceMap tại dòng 20, tính tổng dòng 28 | Đổi URL remote không cập nhật bảng giá đã biên dịch. Các bản khác phiên bản có thể không nhất quán. |
| Cổng Cart mặc định sai | main/webpack.config.js dòng 9; products/webpack.config.js dòng 7 | Mặc định 9002 thay vì 9003. Lệnh start thông thường truyền 9003 nên tránh lỗi này. |
| Replay ban đầu thiếu cart | PubSub khởi tạo {} tại dòng 25–28; gửi ngay tại dòng 69–70 | ProductCard nhận quá sớm có thể gán undefined rồi lỗi findIndex. Đây là rủi ro có điều kiện, chưa tái hiện khi chạy. |
| Chưa gộp tải đồng thời | loadComponent chỉ kiểm tra window[remoteName] | Các lần tải đầu cùng lúc có thể chèn nhiều script. Cần giữ promise đang tải. |
| Lệnh đến trước đăng ký có thể mất | Chỉ topic cart được replay; store đăng ký addItem/removeItem lúc nạp mô-đun | Cần quy tắc sẵn sàng hoặc chính sách xử lý lệnh sớm. |
| ErrorBoundary không phải sandbox | Các mô-đun chạy cùng tài liệu và biến toàn cục | Chỉ giới hạn một số lỗi tải/render; chưa có timeout/retry rõ ràng. |

Ứng dụng chưa có backend, đăng nhập, cơ sở dữ liệu, gửi đơn hoặc thanh toán thật. Liên kết Vercel trong README không được dùng làm bằng chứng cho hạ tầng hiện tại. Đề xuất ở trang 24 chưa được triển khai vào mã nguồn.

## Tài liệu tham khảo

- [Micro Frontends — Michael Geers](https://micro-frontends.org/).
- [Webpack Module Federation](https://webpack.js.org/concepts/module-federation/).
- [Mô hình 4+1 — Philippe Kruchten, 1995](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf).
- [mpuig/agent-slides](https://github.com/mpuig/agent-slides).
