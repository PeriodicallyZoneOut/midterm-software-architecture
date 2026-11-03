"""Nội dung tiếng Việt; dựng bằng agent-slides trên bố cục gốc Slidesgo."""
from deck_drawing import *

# 01 / Bìa gốc: giữ hình minh họa, nền và các nút nối.
new('Kiến trúc Micro-frontend','Kiến trúc phần mềm','micro-frontend-demo; mẫu Slidesgo',
    'Bài trình bày bắt đầu từ khái niệm micro-frontend, sau đó phân tích demo cửa hàng trái cây bằng mô hình 4+1 của Kruchten. Luận điểm chính: tách bản dựng tạo nền tảng cho phát hành độc lập, nhưng mức độ tự chủ còn phụ thuộc vào hợp đồng tích hợp. Nhận xét dựa trên mã nguồn; chưa chạy ứng dụng hay kiểm tra bản triển khai trực tuyến.',
    'title_slide',layout='TITLE',special=True)
template_art(1)
absolute_text('KIẾN TRÚC\nMICRO-FRONTEND',6.25,2.35,3.25,1.25,26,INK,True)
absolute_text('Phân tích demo cửa hàng trái cây\nTheo mô hình 4+1 góc nhìn',6.3,3.85,3.1,1.1,15,BLUE)

# 02
new('Micro-frontend chia giao diện theo nghiệp vụ','01 / Tổng quan','micro-frontends.org',
    'Micro-frontend tổ chức một giao diện lớn thành các khả năng nghiệp vụ do những nhóm khác nhau phụ trách. Mục tiêu là giảm phối hợp bắt buộc khi phát triển và phát hành tính năng. Module Federation là một cách tích hợp, không phải định nghĩa của micro-frontend. Demo chưa chứng minh có các nhóm hoặc quy trình phát hành sản xuất độc lập.', 'executive_summary')
card('Chia theo nghiệp vụ','Danh mục, giỏ hàng, tài khoản là các trách nhiệm riêng.',.5,1.84,2.84)
card('Sở hữu tính năng','Nhóm quản lý tính năng\nvà hợp đồng tích hợp.',3.58,1.84,2.84)
card('Ghép trải nghiệm','Ứng dụng chủ kết hợp các phần thành một giao diện.',6.66,1.84,2.84)
callout('Tách thư mục hoặc giảm kích thước bundle chưa đủ để tạo ranh giới kiến trúc.')

# 03
new('Tách phát hành đòi hỏi hợp đồng tương thích','01 / Phân rã và phát hành','So sánh kiến trúc; micro-frontends.org',
    'Bên trái là một đơn vị phát hành chung. Bên phải là các thành phần được dựng và chuyển giao riêng. Mũi tên biểu diễn việc đưa mã vào trình duyệt. Một kho mã chung vẫn có thể chứa micro-frontend, nhưng các bản phát hành chỉ độc lập khi hợp đồng giữa chúng ổn định và tương thích.', 'two_column')
text('Một đơn vị phát hành',.6,1.75,4,.4,16,BLUE,True)
text('Nhiều đơn vị phát hành',5.35,1.75,4.1,.4,16,BLUE,True)
node('Một bản dựng','Danh mục + giỏ + tài khoản',.6,2.4,3.8,1.1)
node('Trình duyệt','Một giao diện thống nhất',.6,4.0,3.8,.95)
line(2.5,3.5,2.5,4,arrow=True)
for x,label in [(5.35,'Danh mục'),(6.78,'Giỏ'),(8.21,'Tài khoản')]:
    rect(x,2.4,1.22,.72,PALE,BLUE,True)
    text(label,x+.08,2.59,1.06,.3,11,INK,True,align='ctr')
    line(x+.61,3.12,x+.61,3.7,arrow=True)
node('Ứng dụng chủ + trình duyệt','Cần giữ hợp đồng tương thích',5.35,3.7,4.08,1.25)

# 04
new('Cách tích hợp quyết định thời điểm ghép mô-đun','01 / Chiến lược tích hợp','Tổng hợp; tài liệu Webpack Module Federation',
    'Có thể ghép tính năng lúc dựng ứng dụng, trên máy chủ hoặc ở trình duyệt. Iframe tạo ngữ cảnh tài liệu riêng nhưng làm tích hợp trải nghiệm phức tạp hơn. Demo chọn ghép ở trình duyệt bằng Webpack 5 Module Federation. Không có một cách luôn tối ưu cho mọi yêu cầu.', 'table')
table(['Thời điểm','Cơ chế','Điểm cần phối hợp'],[
    ['Khi dựng','Gói thư viện','Dựng lại bên sử dụng'],
    ['Máy chủ / edge','Các mảnh HTML','Luồng ghép trên máy chủ'],
    ['Lúc thực thi','Mô-đun từ xa','Hợp đồng khi chạy'],
    ['Tài liệu riêng','Iframe','Trải nghiệm liên tài liệu']])
callout('Demo sử dụng tích hợp lúc thực thi: Webpack 5 Module Federation.')

# 05
new('Tự chủ phát hành đi kèm chi phí tích hợp','01 / Các đánh đổi','Phân tích kiến trúc định tính',
    'Tách bản dựng giúp thay đổi từng phần nhưng làm phát sinh vấn đề tải mã, tương thích thư viện và xử lý lỗi. Chia sẻ thư viện giảm trùng lặp nhưng tăng nhu cầu phối hợp phiên bản. Đây là đánh giá định tính, chưa có số đo hiệu năng. Cần cân nhắc nhu cầu tự chủ nghiệp vụ so với chi phí tích hợp.', 'three_column')
card('Tự chủ','Lợi ích\nĐổi từng tính năng.\n\nChi phí\nDuy trì hợp đồng.',.5,1.84,2.84,2.94)
card('Tích hợp','Lợi ích\nTải phần cần dùng.\n\nChi phí\nXử lý chậm và lỗi.',3.58,1.84,2.84,2.94)
card('Nhất quán','Lợi ích\nDùng chung trải nghiệm.\n\nChi phí\nPhối hợp thư viện.',6.66,1.84,2.84,2.94)

# 06 / Bố cục chia phần nguyên bản.
new('Từ khái niệm đến demo','02 / Demo cửa hàng trái cây','Mã nguồn micro-frontend-demo',
    'Demo có ba bản dựng main, products và cart. Cần phân biệt tách bản dựng, tách trách nhiệm và độc lập phát hành. Các đề xuất cải tiến ở cuối bài chưa được áp dụng vào mã nguồn.',
    'section_divider',layout='SECTION_HEADER',special=True)
absolute_text('02',3.35,1.28,3.3,.92,44,INK,True,align='ctr')
absolute_text('Phân tích\ndemo thực tế',2.65,2.48,4.7,1.1,27,INK,True,align='ctr')
absolute_text('Ba bản dựng; một trải nghiệm\nKiểm tra ranh giới qua mã nguồn',3.0,3.78,4,.7,13,BLUE,align='ctr')

# 07
new('Cửa hàng ghép danh mục, giỏ hàng và thanh toán','02 / Phạm vi hệ thống','docs/demo.png; main/src/App.tsx',
    'Ảnh có sẵn trong docs/demo.png, không phải ảnh chụp một phiên chạy mới. MAIN sở hữu khung trang, điều hướng và ô chọn URL. PRODUCTS hiển thị danh mục. CART cung cấp huy hiệu, ngăn giỏ và checkout. Checkout chỉ hiển thị mặt hàng và tổng tiền; không có dịch vụ đặt hàng, thanh toán, xác thực hay cơ sở dữ liệu.', 'two_column')
op('add_image',slide_index=__import__('deck_drawing').slide,path=str(ROOT/'assets/demo.png'),left=X(.5),top=Y(1.92),width=W(5.65),height=H(3.02))
text('MAIN — ứng dụng chủ',6.5,1.93,2.9,.64,15,BLUE,True)
text('Khung trang, tuyến và URL',6.5,2.68,2.9,.62,13)
text('PRODUCTS — danh mục',6.5,3.35,2.9,.55,15,BLUE,True)
text('Danh sách và thẻ sản phẩm',6.5,3.97,2.9,.6,13)
text('CART — giỏ và checkout',6.5,4.58,2.9,.58,14,BLUE,True)

# 08
new('Ứng dụng chủ ghép hai remote trong trình duyệt','02 / Sơ đồ hệ thống hiện tại','main/App.tsx; StoreHeader; RemoteComponent; cart/store',
    'Khung lớn là một tài liệu trình duyệt, không phải ba tiến trình backend. MAIN tải PRODUCTS/ProductsList ở /, CART/CheckoutPage ở /checkout và CART/Cart trong đầu trang. Sự kiện đi qua window.fsEvents. CART quản lý Zustand và ghi localStorage. Cart còn dùng PRODUCTS/ProductCard trong ngăn giỏ và checkout; phụ thuộc này được làm rõ ở các góc nhìn sau.', 'process_flow',layout='TITLE_ONLY')
rect(.5,1.8,9,3.28,LIGHT,GREY,True)
text('Một tài liệu trình duyệt / dùng chung môi trường JavaScript',.68,1.94,8.6,.28,12,MUTED,True)
node('MAIN — ứng dụng chủ','Điều hướng • URL • bộ tải remote',2.55,2.43,4.9,.97)
node('PRODUCTS','Danh sách / thẻ sản phẩm',.78,3.98,2.75,1.12)
node('CART','Giao diện giỏ / checkout\nTrạng thái Zustand',6.47,3.76,2.75,1.34)
node('Bus sự kiện','window.fsEvents',3.95,3.98,2.1,1.12,WHITE)
line(3.16,3.4,2.15,3.98,arrow=True)
line(6.84,3.4,7.84,3.76,arrow=True)
line(3.53,4.55,3.95,4.55,arrow=True)
line(6.05,4.55,6.47,4.55,arrow=True)

# 09
new('Mô hình 4+1 tách năm câu hỏi kiến trúc','03 / Khung phân tích','Philippe Kruchten, mô hình 4+1, IEEE Software, 1995',
    'Bốn góc nhìn bổ sung cho nhau; các kịch bản liên kết và giúp kiểm chứng chúng. Logic nói về chức năng; phát triển nói về tổ chức mã; tiến trình nói về thực thi và tương tác; vật lý nói về nơi chạy phần mềm. Đây không phải năm tầng của hệ thống. Với frontend, phải phân biệt máy chủ phân phối mã và runtime thực thi trong trình duyệt.', 'icon_grid')
node('Logic','Hệ thống có trách nhiệm gì?',.55,1.88,3.62,1.16)
node('Phát triển','Mã nguồn được tổ chức ra sao?',5.83,1.88,3.62,1.16)
node('Tiến trình','Các phần thực thi và tương tác?',.55,3.79,3.62,1.16)
node('Vật lý','Phần mềm chạy ở đâu?',5.83,3.79,3.62,1.16)
rect(4.25,2.97,1.5,1.05,BLUE,rounded=True)
text('+1',4.4,3.07,1.2,.47,24,WHITE,True,align='ctr')
text('Kịch bản',4.37,3.62,1.26,.27,12,WHITE,True,align='ctr')
for a,b in [((4.17,2.45),(4.5,2.97)),((5.83,2.45),(5.5,2.97)),((4.17,4.36),(4.5,4.02)),((5.83,4.36),(5.5,4.02))]: line(*a,*b,arrow=True)

# 10
new('Góc nhìn logic phân chia trách nhiệm chức năng','03 / Góc nhìn 1 — logic','main/App.tsx; products/components; cart/components và store',
    'Đây là phân rã trách nhiệm, chưa phải sơ đồ import hay tiến trình. MAIN ghép giao diện và cung cấp dịch vụ tích hợp. PRODUCTS sở hữu danh mục trong mã và thẻ sản phẩm. CART sở hữu số lượng, lưu giỏ và tổng tiền. Cart lấy giá bằng import mã nguồn; góc nhìn phát triển sẽ làm rõ phần phụ thuộc nằm sau ranh giới logic.', 'three_column')
card('Ứng dụng chủ','Ghép giao diện\nQuản lý tuyến\nTra cứu remote\nCung cấp bus',.5,1.84,2.84)
card('Danh mục','Hiển thị sản phẩm\nDựng thẻ sản phẩm\nPhát lệnh thêm / xóa\nNhận ảnh chụp giỏ',3.58,1.84,2.84)
card('Giỏ hàng','Quản lý số lượng\nLưu giỏ cục bộ\nDựng huy hiệu / ngăn\nTính tổng checkout',6.66,1.84,2.84)
callout('Phân chia chức năng rõ chưa đồng nghĩa với độc lập mã nguồn hoặc phát hành.')

# 11
new('Giao diện remote công khai gồm năm mô-đun','03 / Góc nhìn logic — hợp đồng mô-đun','products/webpack.config.js; cart/webpack.config.js',
    'PRODUCTS công khai ProductsList, ProductCard và products. CART công khai Cart và CheckoutPage. MAIN dùng ba mô-đun giao diện chính; Cart dùng ProductCard qua helper của host. Dù PRODUCTS/products đã được expose, Cart vẫn import trực tiếp products/src/products. Tên container, tên mô-đun, props và phiên bản thư viện đều thuộc hợp đồng tích hợp.', 'table')
table(['Container','Mô-đun công khai','Nơi sử dụng'],[
    ['PRODUCTS','./ProductsList','MAIN: tuyến /'],
    ['PRODUCTS','./ProductCard','CART: ngăn giỏ, checkout'],
    ['PRODUCTS','./products','Cart import thẳng nguồn'],
    ['CART','./Cart','MAIN: StoreHeader'],
    ['CART','./CheckoutPage','MAIN: /checkout']], [2.05,2.82,4.13])
callout('Hợp đồng gồm tên mô-đun, props và các thư viện dùng chung tương thích.')

# 12
new('Góc nhìn phát triển bộc lộ phụ thuộc mã nguồn','03 / Góc nhìn 2 — phát triển','package.json; cart/features/checkout; cart/components/CheckoutPanel',
    'Yarn workspaces và Turborepo tổ chức ba ứng dụng trong một kho mã. Mũi tên liền biểu diễn Cart import mã host và danh sách sản phẩm. Nét đứt biểu diễn host lấy mô-đun qua federation lúc chạy. CheckoutPage và CheckoutPanel đều import chéo thư mục. Vì vậy, các bản dựng riêng vẫn phụ thuộc nhau lúc biên dịch. Trang Products chạy riêng còn có cấu hình CART tĩnh, khác registry động của host.', 'process_flow',layout='TITLE_ONLY')
text('Một kho mã / Yarn workspaces / tác vụ Turborepo',.6,1.76,8.8,.42,14,BLUE,True)
node('main/','Khung trang\nMã bộ tải remote',.6,2.48,2.55,1.3)
node('cart/','Giao diện giỏ\nStore Zustand',3.73,2.48,2.55,1.3)
node('products/','Danh mục\nThẻ sản phẩm',6.85,2.48,2.55,1.3)
line(3.73,3.1,3.15,3.1,arrow=True)
line(6.28,3.1,6.85,3.1,arrow=True)
path([(1.86,2.48),(1.86,2.18),(5,2.18),(5,2.48)],dashed=True)
path([(1.86,3.78),(1.86,4.53),(8.13,4.53),(8.13,3.78)],dashed=True)
text('Nét liền: import mã nguồn   |   Nét đứt: lấy mô-đun lúc chạy',.62,4.86,8.8,.31,12,MUTED)

# 13
new('Góc nhìn tiến trình mô tả tải mã bất đồng bộ','03 / Góc nhìn 3 — tiến trình','main/index.tsx; RemoteComponent; main/utils/index.ts',
    'React.lazy gọi loadComponent. Nếu chưa có window[remoteName], loader khởi tạo share scope, chèn remoteEntry.js rồi gọi init. Nó tiếp tục gọi get, thực thi factory và trả module cho React. Tải mã là bất đồng bộ nhưng mã đã nhận chạy trong trình duyệt. Container được lưu theo tên toàn cục, không theo URL. Sơ đồ gộp bước lấy và thực thi factory ở phía loader để dễ đọc.', 'process_flow',layout='TITLE_ONLY')
for x,label in [(.55,'Giao diện React'),(3.6,'Bộ tải của host'),(6.65,'Container remote')]:
    rect(x,1.82,2.8,.5,BLUE,rounded=True)
    text(label,x+.1,1.95,2.6,.27,13,WHITE,True,align='ctr')
for x in [1.95,5,8.05]: line(x,2.4,x,4.85,GREY,dashed=True,width=.8)
for y,a,b,label in [(2.7,1.95,5,'1  lazy(loadComponent)'),(3.24,5,8.05,'2  remoteEntry.js + init'),(3.78,5,8.05,"3  get('./Module')"),(4.33,8.05,5,'4  factory → module'),(4.85,5,1.95,'5  dựng giao diện')]:
    line(a,y,b,y,arrow=True)
    text(label,min(a,b)+.08,y-.31,abs(b-a)-.1,.28,11)
text('Thời gian ↓   |   Tải qua mạng; thực thi trong cùng tài liệu trình duyệt.',.6,5.06,8.8,.25,10,MUTED)

# 14
new('Lệnh qua bus; Cart sở hữu thay đổi trạng thái','03 / Góc nhìn tiến trình — thêm vào giỏ','ProductCard; main/services/pubsub.ts; cart/store/index.ts',
    'ProductCard phát addItem. Store Cart đăng ký addItem và removeItem khi mô-đun được nạp. Handler gọi action Zustand. Trong hàm cập nhật, Cart tạo danh sách mới, phát snapshot cart, ghi localStorage rồi trả trạng thái cho Zustand. ProductCard nhận snapshot; CartButton đọc store bằng selector. Bus gọi subscriber đồng bộ, không có broker mạng hoặc hàng đợi cho lệnh đến quá sớm.', 'process_flow')
node('ProductCard','Phát addItem\n{ name, price }',.5,2.12,2.4,1.35)
node('Bus của host','window.fsEvents\nGọi hàm đồng bộ',3.8,2.12,2.4,1.35)
node('Store Cart','Kiểm tra tên\nĐổi số lượng',7.1,2.12,2.4,1.35)
line(2.9,2.79,3.8,2.79,arrow=True)
line(6.2,2.79,7.1,2.79,arrow=True)
path([(8.3,3.47),(8.3,3.92),(5,3.92),(5,3.47)])
text('Snapshot: cart { cart: [...] }',3.5,4.06,4,.31,12,BLUE,True)
path([(3.8,3.17),(3.3,3.17),(3.3,4.65),(1.7,4.65),(1.7,3.47)])
text('Cập nhật thẻ sản phẩm',.6,4.9,3,.3,12)
text('Lưu: fruit-shop-cart',6.4,4.9,3,.3,12)

# 15
new('Ba loại trạng thái có cơ chế lưu khác nhau','03 / Góc nhìn tiến trình — quản lý trạng thái','main/context/remotes.tsx; PubSub; cart/store/index.ts',
    'Registry URL thuộc MAIN và lưu trong fruit-remotes. Giỏ thuộc CART và lưu trong fruit-shop-cart. persistedTopics của PubSub chỉ giữ thông điệp gần nhất trong bộ nhớ phiên JavaScript hiện tại, không phải lưu bền. Sau reload, Cart đọc localStorage và phát snapshot. Phạm vi localStorage thuộc origin trang host, không thuộc origin phục vụ tệp remote.', 'three_column')
card('Cấu hình remote','Chủ sở hữu: MAIN\n\nwindow.fsRemotes\nlocalStorage:\nfruit-remotes',.5,1.85,2.84,2.9)
card('Dữ liệu giỏ hàng','Chủ sở hữu: CART\n\nStore Zustand\nlocalStorage:\nfruit-shop-cart',3.58,1.85,2.84,2.9)
card('Thông điệp gần nhất','Chủ sở hữu: bus\n\nwindow.fsEvents\nChỉ giữ trong bộ nhớ\nTạo lại sau reload',6.66,1.85,2.84,2.9)
callout('Origin của trang host quyết định phạm vi localStorage, dù mã đến từ remote khác.')

# 16
new('Ba máy chủ phân phối mã cho một runtime phía khách','03 / Góc nhìn 4 — vật lý','webpack.config.js và lệnh start của ba ứng dụng',
    'Môi trường phát triển có ba tiến trình webpack-dev-server ở cổng 9001, 9002 và 9003. Trình duyệt lấy HTML, host bundle rồi remoteEntry.js và các chunk. Mã của cả ba chạy trong trang host. Mũi tên là yêu cầu HTTP lấy tài nguyên, không phải lời gọi nghiệp vụ giữa ba backend. README có liên kết Vercel nhưng hạ tầng triển khai thực tế chưa được kiểm chứng.', 'process_flow',layout='TITLE_ONLY')
for x,name,port,body in [(.5,'MAIN','9001','HTML + host bundle'),(3.58,'PRODUCTS','9002','remoteEntry.js + chunk'),(6.66,'CART','9003','remoteEntry.js + chunk')]:
    node('Máy chủ '+name,body+'\nlocalhost:'+port,x,1.88,2.84,1.4)
    line(x+1.42,3.91,x+1.42,3.28,arrow=True)
    text('HTTP GET',x+.6,3.51,1.7,.27,12,BLUE,True)
node('Trình duyệt — trang host tại localhost:9001','MAIN + PRODUCTS + CART chạy chung; localStorage thuộc origin này.',.5,3.92,9,1.22)

# 17
new('Đổi URL remote có hiệu lực sau khi tải lại trang','03 / Góc nhìn vật lý — chọn bản mã','RemoteControls; context/remotes.tsx; utils/index.ts',
    'Reload ghi hai URL vào fruit-remotes rồi tải lại tài liệu. RemotesProvider ưu tiên dữ liệu lưu trước mặc định. Reload xóa các container toàn cục đã tải; chỉ đổi URL mà không reload có thể vẫn dùng container cũ. Reset xóa cấu hình remote, không xóa giỏ. Cách này không thay được bảng giá đã biên dịch vào Cart hoặc cấu hình remote tĩnh của trang Products chạy riêng.', 'process_flow')
card('1 / Sửa URL','Chọn nơi phục vụ\nProducts hoặc Cart.',.5,2.0,2.84,2.45)
card('2 / Lưu và tải lại','Ghi fruit-remotes.\nTải lại cả trang.',3.58,2.0,2.84,2.45)
card('3 / Phân giải lại','Đọc registry.\nTải remoteEntry.js.',6.66,2.0,2.84,2.45)
line(3.34,3.2,3.58,3.2,arrow=True)
line(6.42,3.2,6.66,3.2,arrow=True)
callout('Chọn mã lúc chạy không thay thế được dữ liệu đã gắn vào bản dựng Cart.')

# 18
new('Kịch bản liên kết hành vi với bốn góc nhìn','03 / Góc nhìn +1 — các ca sử dụng','App.tsx; ProductCard; CheckoutPanel; RemoteControls',
    'Các kịch bản gồm xem danh mục, thay đổi giỏ, xem checkout và reload để khôi phục giỏ. Nhà phát triển còn có kịch bản đổi URL remote. Đây là bản đồ hành vi rút gọn, không phải biểu diễn đầy đủ các quan hệ UML include/extend. Hành vi được suy ra từ mã nguồn, chưa phải kết quả kiểm thử chấp nhận đã chạy.', 'icon_grid')
node('Người mua','Tác nhân chính',.5,2.63,1.95,1.13,BLUE,WHITE)
for x,y,a,b in [(3.16,1.9,'Xem danh mục','PRODUCTS/ProductsList'),(6.55,1.9,'Thay đổi giỏ','addItem / removeItem'),(3.16,3.79,'Xem checkout','CART/CheckoutPage'),(6.55,3.79,'Tải lại trang','Khôi phục từ localStorage')]: node(a,b,x,y,2.95,1.22)
line(2.45,3.2,3.16,2.51,arrow=True)
line(2.45,3.2,3.16,4.4,arrow=True)
line(6.11,2.51,6.55,2.51,arrow=True)
text('Nhà phát triển: đổi URL → tải lại → lặp lại luồng mua hàng.',.6,5.1,8.8,.26,11.5,BLUE,True)

# 19
new('Luồng checkout đi qua đủ bốn góc nhìn','03 / Góc nhìn +1 — truy vết kịch bản','StoreHeader; CheckoutPanel; cart/features/checkout',
    'Giả sử host, remote tương thích đã tải và Cart đã đăng ký nhận lệnh. Người dùng thêm một quả táo, mở giỏ rồi chọn Checkout. CheckoutPanel gọi navigate trong router host; MAIN tải CART/CheckoutPage. Trang tính tiền từ bảng giá import và hiển thị PRODUCTS/ProductCard. Kết quả chỉ là màn hình tổng tiền, không gửi giao dịch thanh toán. Cùng một kịch bản cần được giải thích bằng cả bốn góc nhìn.', 'table')
table(['Góc nhìn','Điểm được quan sát'],[
    ['Logic','Chọn sản phẩm → giỏ → checkout'],
    ['Phát triển','Cart phụ thuộc helper và bảng giá'],
    ['Tiến trình','Lệnh → store → tuyến → tải thành phần'],
    ['Vật lý','Trình duyệt lấy các tệp qua HTTP']], [2.3,6.7])
callout('Kết quả: mặt hàng và tổng tiền xuất hiện tại /checkout; chưa có thanh toán thật.')

# 20
new('Fallback giới hạn lỗi nhưng không cô lập mã','04 / Thuộc tính chất lượng','RemoteComponent; ErrorBoundary; utils/index.ts',
    'Suspense hiển thị trạng thái chờ. Khi tải bị từ chối hoặc component lỗi trong phạm vi React hỗ trợ, ErrorBoundary hiển thị fallback cục bộ. Loader chưa có timeout hoặc retry rõ ràng. ErrorBoundary không cô lập biến toàn cục, không bắt mọi lỗi bất đồng bộ và không tạo sandbox. Lỗi ProductCard còn có thể ảnh hưởng giao diện trong giỏ. Đây là đánh giá từ mã nguồn, chưa đo độ sẵn sàng.', 'three_column')
card('Remote chậm','Cơ chế\nReact Suspense\n\nGiới hạn\nChưa có timeout rõ.',.5,1.85,2.84,2.95)
card('Tải / render lỗi','Cơ chế\nErrorBoundary cục bộ\n\nGiới hạn\nChưa có điều khiển thử lại.',3.58,1.85,2.84,2.95)
card('Remote gây sự cố','Bối cảnh\nChạy chung tài liệu\n\nGiới hạn\nKhông có sandbox.',6.66,1.85,2.84,2.95)

# 21
new('Các quyết định cân bằng linh hoạt và ràng buộc','04 / Phân tích quyết định kiến trúc','Webpack configs; PubSub; remotes context; cart store',
    'Đây là các quyết định suy luận từ triển khai, không phải hồ sơ ADR có sẵn. Container động cho phép đổi vị trí mã nhưng cần tải mạng và hợp đồng API. React và React DOM được cấu hình singleton với requiredVersion. Bus giảm lời gọi trực tiếp nhưng vẫn là API toàn cục. Zustand đặt trạng thái trong Cart; localStorage chưa phải nguồn dữ liệu nghiệp vụ phía máy chủ.', 'table')
table(['Quyết định','Lợi ích','Ràng buộc'],[
    ['Container động','Chọn nơi tải mã','Sẵn sàng và API'],
    ['React singleton','Dùng chung runtime','Tương thích phiên bản'],
    ['Bus của host','Tách bên phát / nhận','Schema và vòng đời'],
    ['Zustand trong Cart','Rõ chủ sở hữu dữ liệu','Khôi phục và đồng bộ']])

# 22
new('Thay remote không loại bỏ phụ thuộc lúc dựng','04 / Giới hạn độc lập trong mã hiện tại','cart/features/checkout; cart/components/CheckoutPanel',
    'Cart import thẳng main/src/components/RemoteComponent và products/src/products. Bảng giá nằm trong bản dựng Cart, nên đổi URL Products có thể thay ProductCard mà không thay dữ liệu tính tổng. Các bản khác phiên bản có nguy cơ hiển thị giá và tính tổng không nhất quán. Chia sẻ mã có thể hợp lý, nhưng cần công khai và quản lý phiên bản thay vì import chéo nguồn ứng dụng.', 'process_flow')
node('Bản Products A','Dữ liệu sản phẩm mới\nProductCard mới',.6,2.05,3.48,1.35)
node('Bản Cart B','Bảng giá import cũ\nMã helper từ host',5.92,2.05,3.48,1.35)
line(4.08,2.72,5.92,2.72,arrow=True,dashed=True)
text('ProductCard\nqua remote',4.16,3.03,1.69,.63,11,BLUE,True,align='ctr')
node('Rủi ro kiến trúc','Giao diện có thể đổi, trong khi tổng tiền vẫn dùng bảng giá của bản Cart cũ.',.6,4.0,8.8,1.04,WHITE)
path([(7.66,3.4),(7.66,3.72),(5,3.72),(5,4.0)])

# 23
new('Ba rủi ro trong mã làm yếu tính độc lập','04 / Kết quả rà soát mã nguồn','main/webpack.config.js; PubSub; main/utils/index.ts',
    'CART_HOST mặc định trỏ 9002, dù Cart phục vụ 9003; lệnh start đã truyền đúng 9003. PubSub khởi tạo replay cart bằng {} và gửi ngay cho subscriber. Nếu ProductCard nhận trước snapshot đầu tiên, cart có thể thành undefined và lỗi findIndex. Loader chưa gộp promise của các lần tải đầu; lệnh tới trước khi Cart đăng ký cũng có thể mất. Đây là các rủi ro có điều kiện từ mã nguồn, chưa được tái hiện khi chạy.', 'three_column')
card('Lệch cấu hình','Cart mặc định: 9002.\n\nLệnh start sửa: 9003.\n\nCấu hình rõ khi dựng.',.5,1.85,2.84,2.96)
card('Replay thiếu dữ liệu','Giá trị ban đầu: {}.\n\nBên nhận cần { cart }.\n\nKhởi tạo đúng schema.',3.58,1.85,2.84,2.96)
card('Đua lúc khởi động','Chưa gộp promise tải.\n\nLệnh không có hàng đợi.\n\nKiểm tra sẵn sàng.',6.66,1.85,2.84,2.96)

# 24
new('Hợp đồng rõ giúp củng cố ranh giới phát hành','04 / Kiến trúc đề xuất — chưa triển khai','Đề xuất từ kết quả rà soát mã nguồn',
    'Đây là đề xuất, không phải kiến trúc hiện tại. Tách loader và schema thành gói tích hợp có phiên bản. Products cung cấp API danh mục rõ ràng cho Cart. Bổ sung manifest đáng tin cậy, trạng thái sẵn sàng, timeout, retry và gộp promise tải. Kiểm thử hợp đồng cần kiểm tra tổ hợp bản cũ và mới. API dữ liệu có thể là mô-đun có phiên bản hoặc dịch vụ; không giả định demo hiện có backend.', 'process_flow')
node('Ứng dụng chủ','Tuyến + manifest\nChính sách tải / thử lại',.55,1.9,2.7,1.34)
node('Hợp đồng phiên bản','Loader + schema\nVòng đời + tương thích',3.65,1.9,2.7,1.34,BLUE,WHITE)
node('Kiểm tra phát hành','Kiểm thử hợp đồng\nPhối hợp bản cũ / mới',6.75,1.9,2.7,1.34)
line(3.25,2.57,3.65,2.57,arrow=True)
line(6.35,2.57,6.75,2.57,arrow=True)
node('Products','Giao diện + API danh mục rõ ràng',.55,4.0,4,1.12)
node('Cart','Trạng thái + checkout; bỏ import chéo',5.45,4.0,4,1.12)
line(4.55,4.56,5.45,4.56,arrow=True)
path([(5,3.24),(5,3.64),(2.55,3.64),(2.55,4)])
path([(5,3.64),(7.45,3.64),(7.45,4)])

new('Hai bản source có cách phục vụ khác nhau','04 / Giới hạn triển khai của demo','Workspace micro-frontend-demo; bản copy source/ trong repo ôn thi',
    'Nguồn chính theo yêu cầu là micro-frontend-demo nằm cạnh repo ôn thi. Bản này có Webpack dev server trên 9001, 9002 và 9003; không có Dockerfile hoặc Compose. Bản copy trong topics/04-micro-frontends-jamstack/projects/micro-frontend-demo/source có Dockerfile, compose.yaml và Nginx phục vụ chung dist qua cổng 9001, với /products/ và /cart/. Cấu hình copy không phải bằng chứng triển khai của nguồn chính. Compose gộp ba bundles trong một image; không thể dùng số thư mục hoặc remoteEntry.js để kết luận phát hành production độc lập. Không chạy hai bản trong lượt chuẩn bị tài liệu này.', 'process_flow',layout='TITLE_ONLY')
node('Nguồn chính trong workspace','Webpack: MAIN :9001\nPRODUCTS :9002; CART :9003',.55,1.9,4.0,1.42)
node('Bản copy trong repo ôn thi','Docker build → một dist / image\nNginx :9001; /products/; /cart/',5.45,1.9,4.0,1.42)
node('Một tài liệu trình duyệt','Host tải mã remote qua HTTP; mọi remote chạy chung JavaScript.',.55,4.0,8.9,1.0)
line(2.55,3.32,2.55,4.0,arrow=True)
line(7.45,3.32,7.45,4.0,arrow=True)
callout('Tách build và tải lúc chạy có thật; phát hành độc lập cần evidence riêng.',5.09)

# 25
new('Luồng demo ngắn làm rõ các ranh giới kiến trúc','05 / Gợi ý trình diễn trên lớp','README; lệnh start; RemoteControls; cart store',
    'Đây là hướng dẫn cho buổi học, không phải nhật ký thao tác đã chạy. Cài phụ thuộc theo Yarn 3.6.1 rồi chạy yarn start trong micro-frontend-demo. Kiểm tra ba cổng và hai remoteEntry.js. Thêm hàng, mở giỏ, vào checkout rồi reload để quan sát localStorage. Nếu có bản remote tương thích khác, đổi URL và chọn Reload. Thử URL không truy cập được để quan sát fallback. Reset URL không xóa giỏ.', 'process_flow')
for j,(a,b) in enumerate([('Khởi động','Cài phụ thuộc; chạy yarn start trong thư mục demo.'),('Theo dõi','Mở :9001 → thêm hàng → giỏ → checkout → tải lại.'),('Thay bản mã','Đổi URL sang remote tương thích; chọn Reload.'),('Thử lỗi','Dùng URL không truy cập được; quan sát vùng lỗi.')]):
    y=1.85+j*.79
    rect(.5,y,.47,.5,BLUE,rounded=True)
    text(str(j+1),.63,y+.13,.23,.28,14,WHITE,True)
    text(a,1.15,y+.03,1.65,.55,14.5,BLUE,True)
    text(b,3.05,y+.03,6.3,.59,13.5)

# 26 / Bố cục nhấn thông điệp nguyên bản.
new('Tách bản dựng là bước đầu; hợp đồng quyết định tự chủ','05 / Kết luận','Tổng hợp phân tích mã nguồn demo',
    'Demo thể hiện tải giao diện từ xa, trách nhiệm hướng tính năng và trạng thái do Cart sở hữu. Mô hình 4+1 cũng làm lộ phụ thuộc nguồn và runtime dùng chung. Tự chủ phát hành đòi hỏi hợp đồng phiên bản, vòng đời tích hợp và xử lý lỗi. Câu hỏi: đổi giá trong Products có phải dựng lại Cart không? Hãy kết hợp góc nhìn phát triển và luồng checkout để giải thích.',
    'big_statement',layout='MAIN_POINT',special=True)
absolute_text('TÁCH BẢN DỰNG\nLÀ BƯỚC ĐẦU',2.1,1.67,5.8,1.05,28,INK,True,align='ctr')
absolute_text('Hợp đồng tương thích\nquyết định mức độ tự chủ',2.15,3.0,5.7,1.05,23,BLUE,True,align='ctr')
absolute_text('Thảo luận: đổi giá trong Products có cần dựng lại Cart?',1.8,4.56,6.4,.45,12,INK,align='ctr')

# 27
new('Tài liệu gốc hỗ trợ các khái niệm kiến trúc','Phụ lục / Tài liệu tham khảo','Các tài liệu chính thức được liên kết bên dưới',
    'micro-frontends.org giải thích mô hình và ranh giới tổ chức. Webpack giải thích container, share scope và tải remote. Bài báo Kruchten năm 1995 là nguồn cho mô hình 4+1. agent-slides trích xuất, dựng và kiểm tra tệp trình chiếu. Bố cục cùng đồ họa được giữ từ mẫu Technology Consulting by Slidesgo do người dùng cung cấp.', 'content_text')
for j,(label,url) in enumerate([
    ['Micro-frontends — Michael Geers','https://micro-frontends.org/'],
    ['Webpack — Module Federation','https://webpack.js.org/concepts/module-federation/'],
    ['Philippe Kruchten — Mô hình 4+1 (1995)','https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf'],
    ['mpuig — Công cụ agent-slides','https://github.com/mpuig/agent-slides']]):
    y=1.82+j*.78
    text(label,.6,y,8.8,.34,14,BLUE,True,href=url)
    text(url,.6,y+.39,8.8,.31,10.5,MUTED,href=url)

# 28
new('Bản đồ mã nguồn giúp kiểm tra các nhận định','Phụ lục / Đối chiếu bằng chứng','Kho mã micro-frontend-demo trong workspace',
    'Đường dẫn tính từ micro-frontend-demo. App và StoreHeader chỉ ra vị trí ghép giao diện. Context và utils chỉ ra cách tìm URL, tải container. PubSub và ProductCard chỉ ra hợp đồng sự kiện. Store Cart là nơi thay đổi và lưu giỏ. Checkout và CheckoutPanel cho thấy import chéo. Webpack cùng package.json xác nhận exports và cổng phục vụ. Đây là rà soát tĩnh, chưa chạy ứng dụng cho nhiệm vụ này.', 'table')
table(['Nội dung kiểm tra','Tệp mã nguồn'],[
    ['Ghép giao diện, tuyến','main/App.tsx; StoreHeader'],
    ['Tìm và tải remote','main/context/remotes.tsx; utils/index.ts'],
    ['Lệnh và replay','main/services/pubsub.ts; ProductCard'],
    ['Trạng thái và lưu giỏ','cart/src/store/index.ts'],
    ['Phụ thuộc mã nguồn','cart/.../checkout; CheckoutPanel'],
    ['Exports và cổng','{main,products,cart}/webpack.config.js']], [3.05,5.95])
text('Phạm vi: phân tích mã tĩnh; chưa kiểm thử hành vi của ứng dụng.',.6,5.1,8.8,.26,11,MUTED)

# 29 / Bố cục Thanks gốc giữ nguyên dòng ghi công và liên kết của mẫu.
new('Cảm ơn!','Kết thúc','Mẫu Technology Consulting by Slidesgo; mã nguồn demo',
    'Mời thảo luận: thay đổi nào trong Products không cần dựng lại Cart? ErrorBoundary bảo vệ được phạm vi nào? Góc nhìn nào cho thấy bảng giá được gắn vào bản dựng? Trang kết thúc giữ bố cục Thanks và dòng ghi công Slidesgo, Flaticon, Freepik, Stories của mẫu gốc.',
    'end_slide',layout='CUSTOM_9',special=True)
absolute_text('CẢM ƠN!',2.35,.72,5.3,.9,38,INK,True,align='ctr')
absolute_text('Câu hỏi và thảo luận',2.65,1.87,4.7,.5,20,BLUE,True,align='ctr')
absolute_text('Một thay đổi trong Products có thể\nphát hành độc lập với Cart đến mức nào?',2.1,2.75,5.8,1.1,18,INK,align='ctr')

finish()
