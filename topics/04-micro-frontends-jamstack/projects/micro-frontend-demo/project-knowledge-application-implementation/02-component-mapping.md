# Mapping Micro-Frontend → code → runtime

Đường dẫn tính từ **`<workspace>/micro-frontend-demo`**. Source chính khác bản `source/` trong repo ở phần Docker/build. [Nguồn và phiên bản](../SOURCE-NOTES.md); [trích đoạn kèm hash](../evidence/source-inspection.md).

| Component / trách nhiệm | Contract vào → ra | State sở hữu | File / symbol | Nơi thực thi / lỗi |
|---|---|---|---|---|
| MAIN / shell, tuyến | `/` → ProductsList; `/checkout` → CheckoutPage | Route, cấu hình remote | `main/src/App.tsx`; `StoreHeader`; `RemoteWrapper` | Browser; thiếu remote làm vùng tương ứng lỗi |
| Registry URL | URL form / env → URL container | `fruit-remotes` trong localStorage | `main/src/context/remotes.tsx`; `RemoteControls` | Browser; URL sai hoặc container cũ cần reload |
| Loader | remoteName, URL, moduleName → module factory | `window[remoteName]` | `main/src/utils/index.ts:loadComponent/fetchRemote` | Browser tải HTTP script; chưa có timeout/retry rõ |
| React wrapper | loader promise → lazy component | Trạng thái tải/render React | `main/src/components/RemoteComponent/index.tsx` | `Suspense`, `ErrorBoundary`; không phải sandbox |
| PRODUCTS | `./ProductsList`, `./ProductCard`, `./products` | Danh mục trong source; UI snapshot giỏ | `products/webpack.config.js`; `products/src/products.ts`; `ProductCard` | Container PRODUCTS trong trang MAIN |
| Event bus | `subscribe/publish/unsubscribe`; topics addItem/removeItem/cart | Subscribers, snapshot cuối trong RAM | `main/src/services/pubsub.ts:PubSub`; `main/src/App.tsx` | Đồng bộ trong browser; không có broker |
| CART store | add/remove → `{cart: [...]}` | Zustand; lưu `fruit-shop-cart` | `cart/src/store/index.ts:store/updateLocalState` | Browser; lỗi JSON/localStorage có thể ảnh hưởng khởi tạo |
| CART UI | `./Cart`, `./CheckoutPage` | Đọc Zustand; đếm số lượng | `cart/webpack.config.js`; `CartButton`; `features/checkout` | Browser; checkout không gửi đơn |
| Webpack / shared | exposes + dependencies → bundles | Cấu hình build | `{main,products,cart}/webpack.config.js` | Node lúc build/dev; React singleton theo version |
| Máy chủ phát triển | HTTP HTML/JS/chunks → browser | Tệp build/dev | `*/package.json:start`; `devServer.port` | MAIN 9001, PRODUCTS 9002, CART 9003 theo code |

## Đọc cấu hình theo thứ tự

1. `products/webpack.config.js`: `name: PRODUCTS`, `filename: remoteEntry.js`, `exposes`.
2. `cart/webpack.config.js`: `name: CART`, `./Cart` và `./CheckoutPage`; dependency remote PRODUCTS.
3. `main/webpack.config.js`: `DefinePlugin` truyền URL mặc định, shared React; host tải động qua utils.
4. `main/src/context/remotes.tsx`: kiểm tra URL thực lấy từ registry hay giá trị compile-time; cổng CART fallback 9002 trong Webpack khác cổng devServer 9003, còn lệnh start truyền 9003.

## Phân biệt hai bản MFE

Bản trong workspace không có `compose.yaml`, `Dockerfile` hoặc `docker/nginx.conf`. Bản copy `topics/04-micro-frontends-jamstack/projects/micro-frontend-demo/source/` có những tệp đó: Compose bind `127.0.0.1:9001:80`; một image Nginx phục vụ `dist` với `/products/`, `/cart/`. Không dùng container đó như bằng chứng runtime của source chính. Sơ đồ slide 25 thể hiện sự khác biệt; việc inspect không thay đổi hoặc chạy bản nào.
