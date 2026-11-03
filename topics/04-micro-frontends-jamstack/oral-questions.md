# 20 câu vấn đáp có điểm chỉ code

Trả lời theo mẫu: kết luận → luồng → file/symbol → giới hạn. Đường dẫn MFE tính từ `<workspace>/micro-frontend-demo`; JAM tính từ `<workspace>/ScriptHammer`. Mỗi đáp án là phân tích source, không phải kết quả test mới.

## Micro-Frontend — 10 câu

### 1. MFE khác SPA nguyên khối và thư viện component ở đâu?

MFE hướng tới quyền sở hữu và phát hành theo tính năng. SPA nguyên khối thường build/publish chung; thư viện component được import lúc build bên dùng; demo MFE tải remote lúc runtime. Xem `*/webpack.config.js:ModuleFederationPlugin` và `main/src/utils/index.ts:loadComponent`. Ba thư mục không tự chứng minh có ba nhóm hoặc phát hành riêng.

### 2. MAIN có `remotes: {}` thì remote được nạp thế nào?

MAIN dùng loader động: chọn URL từ registry, tạo script `remoteEntry.js`, init share scope/container, gọi `get(moduleName)` rồi factory. `main/src/components/RemoteComponent/index.tsx` bọc React.lazy; `main/src/utils/index.ts` thực hiện tải. Khác cấu hình remote URL tĩnh khai báo trong Webpack.

### 3. Exposes và shared khác nhau thế nào?

Exposes là các module remote công bố cho bên dùng, như `PRODUCTS/ProductsList`, `CART/Cart`. Shared là dependency trao đổi qua share scope, như React/React DOM singleton. Xem cấu hình PRODUCTS/CART. Singleton giảm runtime React trùng, vẫn cần tương thích phiên bản; không phải cơ chế sandbox.

### 4. Ai sở hữu state giỏ? Hãy kể luồng addItem.

CART sở hữu state Zustand. `ProductCard` publish `addItem` → bus host gọi callback → store tăng quantity/thêm hàng → publish `cart` → ghi localStorage → updater trả state mới. Mở `ProductCard`, `PubSub.publish`, `cart/src/store/index.ts:updateLocalState`. UI nhận snapshot; Products không sửa trực tiếp store Cart.

### 5. PubSub có phải message broker / event sourcing không?

Không: đây là object `window.fsEvents` gọi callbacks đồng bộ trong cùng browser, không có network broker/ACK/durable log. Nó giữ snapshot cuối cho topic `cart` trong RAM, không có event history để phục hồi nghiệp vụ. Xem `main/src/services/pubsub.ts:publish/subscribe/persistedMessages`. Đừng dùng tên “event bus” để suy diễn delivery semantics của broker.

### 6. Vì sao refresh vẫn có giỏ? Remote origin ảnh hưởng thế nào?

`cart/src/store/index.ts:getLocalState` đọc khóa `fruit-shop-cart`, tạo store và phát snapshot. Storage thuộc origin trang host, không thuộc origin máy chủ chứa remote script. Đổi host port/origin có thể thấy giỏ khác. `fruit-remotes` giữ URL, khác dữ liệu giỏ; reset URL không xóa giỏ.

### 7. Remote chết thì toàn app có chết không?

`RemoteComponent` có Suspense/ErrorBoundary để hiển thị chờ hoặc fallback trong vùng React. `fetchRemote` reject khi script lỗi; chưa có timeout/retry rõ. Mã cùng trang vẫn có thể tác động global, bus hoặc lỗi ngoài phạm vi boundary. Không bảo đảm mọi lỗi đều được cô lập; thực tế vùng nào còn dùng được cần capture của phiên demo.

### 8. Đổi URL Products có nghĩa deploy độc lập hoàn toàn không?

Chỉ cho thấy host có cơ chế chọn remote lúc chạy. CART còn import `products/src/products` và helper MAIN trong checkout/CheckoutPanel, nên giá được đóng vào bundle Cart. UI Products mới có thể đi cùng bảng giá Cart cũ. Muốn kết luận phát hành độc lập cần build/URL B, contract tương thích và evidence host không rebuild; source loader chưa đủ.

### 9. Một lệnh đến trước khi Cart đăng ký được xử lý ra sao?

`addItem`/`removeItem` không được queue/replay bền. Nếu chưa có subscriber, lệnh có thể mất. Chỉ topic `cart` được giữ snapshot; giá trị khởi tạo `{}` có thể khiến subscriber nhận payload chưa đủ schema. Xem constructor/subscribe PubSub và đăng ký ở scope module Cart store. Đây là rủi ro theo thứ tự khởi tạo, chưa được tái hiện trong lượt này.

### 10. Demo đang dùng ba server hay một Nginx? Mã remote đáng tin đến mức nào?

Source chính trong workspace khai báo ba dev server 9001/9002/9003. Bản copy trong repo có Docker/Nginx gộp ba bundles trong một image; không gán cấu hình này cho source chính. Remote script chạy với quyền trang host, nên URL remote là ranh giới tin cậy; ErrorBoundary không giảm quyền truy cập dữ liệu. Mở `*/webpack.config.js` và so sánh `source/compose.yaml` của bản copy.

## JAMstack / ScriptHammer — 10 câu

### 1. Vì sao ScriptHammer là ví dụ JAMstack dù có auth và thanh toán?

`next.config.ts` xuất frontend thành tệp; JavaScript gọi Supabase và Edge Functions cho nghiệp vụ động. J là JS tương tác, A là dịch vụ API, M là HTML dựng sẵn. JAMstack tách phân phối frontend khỏi backend, không xóa backend. Mở config, Supabase client và `lib/payments/stripe.ts`.

### 2. CSR/SSR/SSG/ISR khác nhau và mode nào thực có?

CSR dựng/cập nhật UI trong browser; SSR render theo request ở server; SSG tạo HTML lúc build; ISR tái tạo trang sau build nhờ runtime hỗ trợ. ScriptHammer static export dùng SSG và CSR cho dữ liệu động. SSR/ISR chỉ so sánh lý thuyết, không có trong luồng Pages này. Xem `output: export`, blog `generateStaticParams`.

### 3. Server Component đọc `fs` có mâu thuẫn static hosting không?

Không. Code đọc JSON chạy lúc build và tạo artifact; Pages trả tệp đã sinh, không chạy `fs` theo request. `src/app/blog/page.tsx:getPosts` và `blog/[slug]/page.tsx` đọc `blog-data.json`. Cần phân biệt Node lúc build với Node server render production.

### 4. Hãy chỉ pipeline blog thật thay cho `_posts` trong tài liệu cũ.

`public/blog/*.md` → `scripts/generate-blog-data.js`/gray-matter → `src/lib/blog/blog-data.json` → `generateStaticParams` + trang blog/markdownProcessor → HTML/assets export. Không dùng `api.ts` hoặc remark của Blog Starter để giải thích ScriptHammer. Xem generator và script `generate:blog`.

### 5. Sửa Markdown rồi build có chắc thấy bài mới không?

Chưa chắc: `prebuild` và deploy workflow đang đọc không gọi `generate:blog`. JSON cũ có thể tiếp tục được dùng. Cần sinh JSON, build/export, kiểm tra slug HTML, publish artifact rồi đối chiếu cache/client cũ. Sửa source không thay bản đã publish. Mở `package.json`, generator và `deploy.yml`.

### 6. Dev server hiển thị bài có chứng minh SSG production không?

Không. Bằng chứng phù hợp là build log và HTML/assets export của đúng commit, cộng hosting phục vụ artifact đó. `next dev` biên dịch theo nhu cầu khác production. Trong lượt chuẩn bị này chỉ xác nhận config, không có build log app mới; không tự đánh dấu E07 đã hoàn thành.

### 7. Hosting chính là `next start` hay Pages? Có phải CDN local không?

Cấu hình chính là static export; deploy workflow ghép `out/` với Storybook thành `merged-output` rồi Pages. Script `start: next start` tồn tại không đổi semantics của export. Local dev/serve tệp không phải bằng chứng CDN triển khai. Không cần Next server render để phục vụ artifact export; tình trạng URL production phải đối chiếu evidence riêng.

### 8. Đổi Supabase URL hoặc khóa công khai có cần build lại không?

Các giá trị `NEXT_PUBLIC_*` được bundle vào frontend lúc build; đổi env trên máy chủ static không tự sửa JS đã phát hành. Cần build/publish frontend với cấu hình mới. Secrets backend có vòng đời khác, không đưa service-role/Stripe secret vào bundle. Xem next config và Supabase client.

### 9. Có route guard là dữ liệu đã an toàn chưa?

Guard chỉ điều khiển UI. Browser có thể gọi API trực tiếp; quyền phải ở JWT/RLS và kiểm tra trong Edge Functions. Xem `AuthContext`, migration RLS và `create-stripe-checkout`. Checkout function dùng đặc quyền cần kiểm tra user/quy tắc nghiệp vụ; redirect browser không thay webhook có chữ ký làm xác nhận backend.

### 10. Deploy mới xong mọi người đều thấy bản mới và app chạy offline đầy đủ không?

Không có bảo đảm đó. Cache/SW và tab cũ có thể dùng bản trước; workflow giữ assets cũ, build stamp version SW để giảm bất tương thích. SW chỉ cache theo quy tắc; auth mới/API/dữ liệu chưa cache vẫn cần mạng. Queue messaging có điều kiện phiên/khóa/dữ liệu, không làm toàn app offline. Xem `sw.js`, stamp script, retention workflow và offline queue service.
