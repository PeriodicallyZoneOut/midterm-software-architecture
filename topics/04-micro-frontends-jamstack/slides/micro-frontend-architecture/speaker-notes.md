# Ghi chú thuyết trình

Thời lượng dự kiến: 20–25 phút, chưa gồm thảo luận.

## 01. Kiến trúc Micro-frontend

Bài trình bày bắt đầu từ khái niệm micro-frontend, sau đó phân tích demo cửa hàng trái cây bằng mô hình 4+1 của Kruchten. Luận điểm chính: tách bản dựng tạo nền tảng cho phát hành độc lập, nhưng mức độ tự chủ còn phụ thuộc vào hợp đồng tích hợp. Nhận xét dựa trên mã nguồn; chưa chạy ứng dụng hay kiểm tra bản triển khai trực tuyến.

Nguồn: micro-frontend-demo; mẫu Slidesgo

## 02. Micro-frontend chia giao diện theo nghiệp vụ

Micro-frontend tổ chức một giao diện lớn thành các khả năng nghiệp vụ do những nhóm khác nhau phụ trách. Mục tiêu là giảm phối hợp bắt buộc khi phát triển và phát hành tính năng. Module Federation là một cách tích hợp, không phải định nghĩa của micro-frontend. Demo chưa chứng minh có các nhóm hoặc quy trình phát hành sản xuất độc lập.

Nguồn: micro-frontends.org

## 03. Tách phát hành đòi hỏi hợp đồng tương thích

Bên trái là một đơn vị phát hành chung. Bên phải là các thành phần được dựng và chuyển giao riêng. Mũi tên biểu diễn việc đưa mã vào trình duyệt. Một kho mã chung vẫn có thể chứa micro-frontend, nhưng các bản phát hành chỉ độc lập khi hợp đồng giữa chúng ổn định và tương thích.

Nguồn: So sánh kiến trúc; micro-frontends.org

## 04. Cách tích hợp quyết định thời điểm ghép mô-đun

Có thể ghép tính năng lúc dựng ứng dụng, trên máy chủ hoặc ở trình duyệt. Iframe tạo ngữ cảnh tài liệu riêng nhưng làm tích hợp trải nghiệm phức tạp hơn. Demo chọn ghép ở trình duyệt bằng Webpack 5 Module Federation. Không có một cách luôn tối ưu cho mọi yêu cầu.

Nguồn: Tổng hợp; tài liệu Webpack Module Federation

## 05. Tự chủ phát hành đi kèm chi phí tích hợp

Tách bản dựng giúp thay đổi từng phần nhưng làm phát sinh vấn đề tải mã, tương thích thư viện và xử lý lỗi. Chia sẻ thư viện giảm trùng lặp nhưng tăng nhu cầu phối hợp phiên bản. Đây là đánh giá định tính, chưa có số đo hiệu năng. Cần cân nhắc nhu cầu tự chủ nghiệp vụ so với chi phí tích hợp.

Nguồn: Phân tích kiến trúc định tính

## 06. Từ khái niệm đến demo

Demo có ba bản dựng main, products và cart. Cần phân biệt tách bản dựng, tách trách nhiệm và độc lập phát hành. Các đề xuất cải tiến ở cuối bài chưa được áp dụng vào mã nguồn.

Nguồn: Mã nguồn micro-frontend-demo

## 07. Cửa hàng ghép danh mục, giỏ hàng và thanh toán

Ảnh có sẵn trong docs/demo.png, không phải ảnh chụp một phiên chạy mới. MAIN sở hữu khung trang, điều hướng và ô chọn URL. PRODUCTS hiển thị danh mục. CART cung cấp huy hiệu, ngăn giỏ và checkout. Checkout chỉ hiển thị mặt hàng và tổng tiền; không có dịch vụ đặt hàng, thanh toán, xác thực hay cơ sở dữ liệu.

Nguồn: docs/demo.png; main/src/App.tsx

## 08. Ứng dụng chủ ghép hai remote trong trình duyệt

Khung lớn là một tài liệu trình duyệt, không phải ba tiến trình backend. MAIN tải PRODUCTS/ProductsList ở /, CART/CheckoutPage ở /checkout và CART/Cart trong đầu trang. Sự kiện đi qua window.fsEvents. CART quản lý Zustand và ghi localStorage. Cart còn dùng PRODUCTS/ProductCard trong ngăn giỏ và checkout; phụ thuộc này được làm rõ ở các góc nhìn sau.

Nguồn: main/App.tsx; StoreHeader; RemoteComponent; cart/store

## 09. Mô hình 4+1 tách năm câu hỏi kiến trúc

Bốn góc nhìn bổ sung cho nhau; các kịch bản liên kết và giúp kiểm chứng chúng. Logic nói về chức năng; phát triển nói về tổ chức mã; tiến trình nói về thực thi và tương tác; vật lý nói về nơi chạy phần mềm. Đây không phải năm tầng của hệ thống. Với frontend, phải phân biệt máy chủ phân phối mã và runtime thực thi trong trình duyệt.

Nguồn: Philippe Kruchten, mô hình 4+1, IEEE Software, 1995

## 10. Góc nhìn logic phân chia trách nhiệm chức năng

Đây là phân rã trách nhiệm, chưa phải sơ đồ import hay tiến trình. MAIN ghép giao diện và cung cấp dịch vụ tích hợp. PRODUCTS sở hữu danh mục trong mã và thẻ sản phẩm. CART sở hữu số lượng, lưu giỏ và tổng tiền. Cart lấy giá bằng import mã nguồn; góc nhìn phát triển sẽ làm rõ phần phụ thuộc nằm sau ranh giới logic.

Nguồn: main/App.tsx; products/components; cart/components và store

## 11. Giao diện remote công khai gồm năm mô-đun

PRODUCTS công khai ProductsList, ProductCard và products. CART công khai Cart và CheckoutPage. MAIN dùng ba mô-đun giao diện chính; Cart dùng ProductCard qua helper của host. Dù PRODUCTS/products đã được expose, Cart vẫn import trực tiếp products/src/products. Tên container, tên mô-đun, props và phiên bản thư viện đều thuộc hợp đồng tích hợp.

Nguồn: products/webpack.config.js; cart/webpack.config.js

## 12. Góc nhìn phát triển bộc lộ phụ thuộc mã nguồn

Yarn workspaces và Turborepo tổ chức ba ứng dụng trong một kho mã. Mũi tên liền biểu diễn Cart import mã host và danh sách sản phẩm. Nét đứt biểu diễn host lấy mô-đun qua federation lúc chạy. CheckoutPage và CheckoutPanel đều import chéo thư mục. Vì vậy, các bản dựng riêng vẫn phụ thuộc nhau lúc biên dịch. Trang Products chạy riêng còn có cấu hình CART tĩnh, khác registry động của host.

Nguồn: package.json; cart/features/checkout; cart/components/CheckoutPanel

## 13. Góc nhìn tiến trình mô tả tải mã bất đồng bộ

React.lazy gọi loadComponent. Nếu chưa có window[remoteName], loader khởi tạo share scope, chèn remoteEntry.js rồi gọi init. Nó tiếp tục gọi get, thực thi factory và trả module cho React. Tải mã là bất đồng bộ nhưng mã đã nhận chạy trong trình duyệt. Container được lưu theo tên toàn cục, không theo URL. Sơ đồ gộp bước lấy và thực thi factory ở phía loader để dễ đọc.

Nguồn: main/index.tsx; RemoteComponent; main/utils/index.ts

## 14. Lệnh qua bus; Cart sở hữu thay đổi trạng thái

ProductCard phát addItem. Store Cart đăng ký addItem và removeItem khi mô-đun được nạp. Handler gọi action Zustand. Trong hàm cập nhật, Cart tạo danh sách mới, phát snapshot cart, ghi localStorage rồi trả trạng thái cho Zustand. ProductCard nhận snapshot; CartButton đọc store bằng selector. Bus gọi subscriber đồng bộ, không có broker mạng hoặc hàng đợi cho lệnh đến quá sớm.

Nguồn: ProductCard; main/services/pubsub.ts; cart/store/index.ts

## 15. Ba loại trạng thái có cơ chế lưu khác nhau

Registry URL thuộc MAIN và lưu trong fruit-remotes. Giỏ thuộc CART và lưu trong fruit-shop-cart. persistedTopics của PubSub chỉ giữ thông điệp gần nhất trong bộ nhớ phiên JavaScript hiện tại, không phải lưu bền. Sau reload, Cart đọc localStorage và phát snapshot. Phạm vi localStorage thuộc origin trang host, không thuộc origin phục vụ tệp remote.

Nguồn: main/context/remotes.tsx; PubSub; cart/store/index.ts

## 16. Ba máy chủ phân phối mã cho một runtime phía khách

Môi trường phát triển có ba tiến trình webpack-dev-server ở cổng 9001, 9002 và 9003. Trình duyệt lấy HTML, host bundle rồi remoteEntry.js và các chunk. Mã của cả ba chạy trong trang host. Mũi tên là yêu cầu HTTP lấy tài nguyên, không phải lời gọi nghiệp vụ giữa ba backend. README có liên kết Vercel nhưng hạ tầng triển khai thực tế chưa được kiểm chứng.

Nguồn: webpack.config.js và lệnh start của ba ứng dụng

## 17. Đổi URL remote có hiệu lực sau khi tải lại trang

Reload ghi hai URL vào fruit-remotes rồi tải lại tài liệu. RemotesProvider ưu tiên dữ liệu lưu trước mặc định. Reload xóa các container toàn cục đã tải; chỉ đổi URL mà không reload có thể vẫn dùng container cũ. Reset xóa cấu hình remote, không xóa giỏ. Cách này không thay được bảng giá đã biên dịch vào Cart hoặc cấu hình remote tĩnh của trang Products chạy riêng.

Nguồn: RemoteControls; context/remotes.tsx; utils/index.ts

## 18. Kịch bản liên kết hành vi với bốn góc nhìn

Các kịch bản gồm xem danh mục, thay đổi giỏ, xem checkout và reload để khôi phục giỏ. Nhà phát triển còn có kịch bản đổi URL remote. Đây là bản đồ hành vi rút gọn, không phải biểu diễn đầy đủ các quan hệ UML include/extend. Hành vi được suy ra từ mã nguồn, chưa phải kết quả kiểm thử chấp nhận đã chạy.

Nguồn: App.tsx; ProductCard; CheckoutPanel; RemoteControls

## 19. Luồng checkout đi qua đủ bốn góc nhìn

Giả sử host, remote tương thích đã tải và Cart đã đăng ký nhận lệnh. Người dùng thêm một quả táo, mở giỏ rồi chọn Checkout. CheckoutPanel gọi navigate trong router host; MAIN tải CART/CheckoutPage. Trang tính tiền từ bảng giá import và hiển thị PRODUCTS/ProductCard. Kết quả chỉ là màn hình tổng tiền, không gửi giao dịch thanh toán. Cùng một kịch bản cần được giải thích bằng cả bốn góc nhìn.

Nguồn: StoreHeader; CheckoutPanel; cart/features/checkout

## 20. Fallback giới hạn lỗi nhưng không cô lập mã

Suspense hiển thị trạng thái chờ. Khi tải bị từ chối hoặc component lỗi trong phạm vi React hỗ trợ, ErrorBoundary hiển thị fallback cục bộ. Loader chưa có timeout hoặc retry rõ ràng. ErrorBoundary không cô lập biến toàn cục, không bắt mọi lỗi bất đồng bộ và không tạo sandbox. Lỗi ProductCard còn có thể ảnh hưởng giao diện trong giỏ. Đây là đánh giá từ mã nguồn, chưa đo độ sẵn sàng.

Nguồn: RemoteComponent; ErrorBoundary; utils/index.ts

## 21. Các quyết định cân bằng linh hoạt và ràng buộc

Đây là các quyết định suy luận từ triển khai, không phải hồ sơ ADR có sẵn. Container động cho phép đổi vị trí mã nhưng cần tải mạng và hợp đồng API. React và React DOM được cấu hình singleton với requiredVersion. Bus giảm lời gọi trực tiếp nhưng vẫn là API toàn cục. Zustand đặt trạng thái trong Cart; localStorage chưa phải nguồn dữ liệu nghiệp vụ phía máy chủ.

Nguồn: Webpack configs; PubSub; remotes context; cart store

## 22. Thay remote không loại bỏ phụ thuộc lúc dựng

Cart import thẳng main/src/components/RemoteComponent và products/src/products. Bảng giá nằm trong bản dựng Cart, nên đổi URL Products có thể thay ProductCard mà không thay dữ liệu tính tổng. Các bản khác phiên bản có nguy cơ hiển thị giá và tính tổng không nhất quán. Chia sẻ mã có thể hợp lý, nhưng cần công khai và quản lý phiên bản thay vì import chéo nguồn ứng dụng.

Nguồn: cart/features/checkout; cart/components/CheckoutPanel

## 23. Ba rủi ro trong mã làm yếu tính độc lập

CART_HOST mặc định trỏ 9002, dù Cart phục vụ 9003; lệnh start đã truyền đúng 9003. PubSub khởi tạo replay cart bằng {} và gửi ngay cho subscriber. Nếu ProductCard nhận trước snapshot đầu tiên, cart có thể thành undefined và lỗi findIndex. Loader chưa gộp promise của các lần tải đầu; lệnh tới trước khi Cart đăng ký cũng có thể mất. Đây là các rủi ro có điều kiện từ mã nguồn, chưa được tái hiện khi chạy.

Nguồn: main/webpack.config.js; PubSub; main/utils/index.ts

## 24. Hợp đồng rõ giúp củng cố ranh giới phát hành

Đây là đề xuất, không phải kiến trúc hiện tại. Tách loader và schema thành gói tích hợp có phiên bản. Products cung cấp API danh mục rõ ràng cho Cart. Bổ sung manifest đáng tin cậy, trạng thái sẵn sàng, timeout, retry và gộp promise tải. Kiểm thử hợp đồng cần kiểm tra tổ hợp bản cũ và mới. API dữ liệu có thể là mô-đun có phiên bản hoặc dịch vụ; không giả định demo hiện có backend.

Nguồn: Đề xuất từ kết quả rà soát mã nguồn

## 25. Hai bản source có cách phục vụ khác nhau

Nguồn chính theo yêu cầu là micro-frontend-demo nằm cạnh repo ôn thi. Bản này có Webpack dev server trên 9001, 9002 và 9003; không có Dockerfile hoặc Compose. Bản copy trong topics/04-micro-frontends-jamstack/projects/micro-frontend-demo/source có Dockerfile, compose.yaml và Nginx phục vụ chung dist qua cổng 9001, với /products/ và /cart/. Cấu hình copy không phải bằng chứng triển khai của nguồn chính. Compose gộp ba bundles trong một image; không thể dùng số thư mục hoặc remoteEntry.js để kết luận phát hành production độc lập. Không chạy hai bản trong lượt chuẩn bị tài liệu này.

Nguồn: Workspace micro-frontend-demo; bản copy source/ trong repo ôn thi

## 26. Luồng demo ngắn làm rõ các ranh giới kiến trúc

Đây là hướng dẫn cho buổi học, không phải nhật ký thao tác đã chạy. Cài phụ thuộc theo Yarn 3.6.1 rồi chạy yarn start trong micro-frontend-demo. Kiểm tra ba cổng và hai remoteEntry.js. Thêm hàng, mở giỏ, vào checkout rồi reload để quan sát localStorage. Nếu có bản remote tương thích khác, đổi URL và chọn Reload. Thử URL không truy cập được để quan sát fallback. Reset URL không xóa giỏ.

Nguồn: README; lệnh start; RemoteControls; cart store

## 27. Tách bản dựng là bước đầu; hợp đồng quyết định tự chủ

Demo thể hiện tải giao diện từ xa, trách nhiệm hướng tính năng và trạng thái do Cart sở hữu. Mô hình 4+1 cũng làm lộ phụ thuộc nguồn và runtime dùng chung. Tự chủ phát hành đòi hỏi hợp đồng phiên bản, vòng đời tích hợp và xử lý lỗi. Câu hỏi: đổi giá trong Products có phải dựng lại Cart không? Hãy kết hợp góc nhìn phát triển và luồng checkout để giải thích.

Nguồn: Tổng hợp phân tích mã nguồn demo

## 28. Tài liệu gốc hỗ trợ các khái niệm kiến trúc

micro-frontends.org giải thích mô hình và ranh giới tổ chức. Webpack giải thích container, share scope và tải remote. Bài báo Kruchten năm 1995 là nguồn cho mô hình 4+1. agent-slides trích xuất, dựng và kiểm tra tệp trình chiếu. Bố cục cùng đồ họa được giữ từ mẫu Technology Consulting by Slidesgo do người dùng cung cấp.

Nguồn: Các tài liệu chính thức được liên kết bên dưới

## 29. Bản đồ mã nguồn giúp kiểm tra các nhận định

Đường dẫn tính từ micro-frontend-demo. App và StoreHeader chỉ ra vị trí ghép giao diện. Context và utils chỉ ra cách tìm URL, tải container. PubSub và ProductCard chỉ ra hợp đồng sự kiện. Store Cart là nơi thay đổi và lưu giỏ. Checkout và CheckoutPanel cho thấy import chéo. Webpack cùng package.json xác nhận exports và cổng phục vụ. Đây là rà soát tĩnh, chưa chạy ứng dụng cho nhiệm vụ này.

Nguồn: Kho mã micro-frontend-demo trong workspace

## 30. Cảm ơn!

Mời thảo luận: thay đổi nào trong Products không cần dựng lại Cart? ErrorBoundary bảo vệ được phạm vi nào? Góc nhìn nào cho thấy bảng giá được gắn vào bản dựng? Trang kết thúc giữ bố cục Thanks và dòng ghi công Slidesgo, Flaticon, Freepik, Stories của mẫu gốc.

Nguồn: Mẫu Technology Consulting by Slidesgo; mã nguồn demo