"""Bài trình bày JAMstack / ScriptHammer bằng tiếng Việt, dùng agent-slides."""
from deck_drawing import *

# 01 — Giữ bìa và hình minh họa vector của mẫu Slidesgo.
new('Kiến trúc JAMstack — ScriptHammer','Kiến trúc phần mềm','ScriptHammer; mẫu Technology Consulting by Slidesgo',
    'Bài trình bày đi từ nguyên lý JAMstack đến cách ScriptHammer triển khai chúng. Trọng tâm là ranh giới giữa dựng trước, phục vụ tệp, thực thi ở trình duyệt và backend API. Dùng mô hình 4+1 để tách trách nhiệm, mã nguồn, luồng thực thi và hạ tầng. Phân tích dựa trên mã nguồn trong workspace; chưa chạy ứng dụng, gọi backend hoặc xác minh bản triển khai trực tuyến.',
    'title_slide',layout='TITLE',special=True)
template_art(1)
absolute_text('KIẾN TRÚC\nJAMSTACK',6.25,2.35,3.25,1.25,29,INK,True)
absolute_text('Phân tích hệ thống ScriptHammer\nTheo mô hình 4+1 góc nhìn',6.3,3.85,3.1,1.1,15,BLUE)

# 02
new('JAMstack tách giao diện dựng sẵn khỏi API','01 / Tổng quan','jamstack.org/what-is-jamstack',
    'Hai nguyên lý cốt lõi là dựng trước giao diện và tách giao diện khỏi các dịch vụ nghiệp vụ. HTML cùng tài nguyên được phục vụ như tệp; JavaScript gọi API khi cần dữ liệu hoặc thao tác cá nhân hóa. Đây là cách phân chia trách nhiệm của kiến trúc, không phải tên một framework cụ thể.', 'executive_summary')
card('Dựng trước','Tạo HTML và tài nguyên\ntrước khi có yêu cầu.',.5,1.84,2.84)
card('Phục vụ tệp','Máy chủ tĩnh hoặc CDN\nphân phối giao diện.',3.58,1.84,2.84)
card('Gọi dịch vụ','Trình duyệt dùng API\ncho dữ liệu động.',6.66,1.84,2.84)
callout('Ranh giới chính: tạo giao diện khi dựng; xử lý nghiệp vụ động qua API.')

# 03
new('Luồng dựng và luồng sử dụng diễn ra khác lúc','01 / Hai luồng của kiến trúc','Sơ đồ minh họa kiến trúc JAMstack',
    'Hàng trên là luồng tạo và phát hành tài nguyên. Hàng dưới là luồng người dùng sử dụng ứng dụng. Tệp tĩnh không tự thay đổi mỗi khi dữ liệu nghiệp vụ thay đổi. API cung cấp dữ liệu theo phiên người dùng. Mũi tên xuống từ kho tệp đến trình duyệt biểu diễn phân phối tài nguyên; hai luồng không phải một chuỗi xử lý HTTP duy nhất.', 'process_flow',layout='TITLE_ONLY')
node('Mã và nội dung','Nguồn đầu vào',.55,1.93,2.65,1.14)
node('Bộ dựng','Sinh HTML / CSS / JS',3.68,1.93,2.65,1.14)
node('Máy chủ tĩnh','Phân phối tài nguyên',6.81,1.93,2.65,1.14)
line(3.2,2.5,3.68,2.5,arrow=True)
line(6.33,2.5,6.81,2.5,arrow=True)
node('API nghiệp vụ','Dữ liệu và thao tác động',.55,3.98,3.5,1.14)
node('Trình duyệt','Nhận tệp rồi thực thi JavaScript',5.75,3.98,3.7,1.14)
line(8.14,3.07,8.14,3.98,arrow=True)
line(5.75,4.55,4.05,4.55,arrow=True)
text('Yêu cầu API',4.1,4.76,1.6,.3,11,BLUE,True)
text('Dựng / phát hành',.6,3.25,3.8,.3,12,BLUE,True)
text('Sử dụng lúc chạy',.6,3.65,3.8,.3,12,BLUE,True)

# 04
new('JAM không giới hạn ứng dụng ở nội dung tĩnh','01 / JavaScript — APIs — Markup','Tổng hợp khái niệm; cấu trúc ScriptHammer',
    'JavaScript tạo tương tác, API cung cấp năng lực động, còn markup tạo nền giao diện được dựng trước. Một ứng dụng có thể có đăng nhập, thanh toán và trò chuyện nhưng vẫn phân phối frontend tĩnh. Không có runtime máy chủ Next.js không có nghĩa là không có backend: các dịch vụ API vẫn thực thi trên máy chủ.', 'three_column')
card('J — JavaScript','Tương tác và điều hướng\nQuản lý phiên\nGọi dịch vụ từ trình duyệt',.5,1.84,2.84)
card('A — APIs','Xác thực và dữ liệu\nThao tác cần bí mật\nThông báo thời gian thực',3.58,1.84,2.84)
card('M — Markup','HTML dựng sẵn\nCSS và tài nguyên\nNền cho trải nghiệm',6.66,1.84,2.84)
callout('Frontend tĩnh vẫn có thể cung cấp trải nghiệm động nhờ backend API.')

# 05
new('Dựng sẵn đổi chi phí máy chủ thành chi phí tích hợp','01 / Đánh đổi kiến trúc','Phân tích định tính; không phải số đo hiệu năng',
    'Phân phối tệp giảm nhu cầu vận hành máy chủ render theo từng yêu cầu. Đổi lại, nội dung dựng sẵn cần phát hành lại, dịch vụ động phụ thuộc API và cấu hình phiên bản phải đồng bộ. CDN không tự giải quyết truy vấn cơ sở dữ liệu, quyền truy cập hay gửi tiền. Những lợi ích dưới đây là kỳ vọng kiến trúc, không phải kết quả benchmark ScriptHammer.', 'three_column')
card('Phân phối','Thuận lợi\nTệp dễ cache.\n\nĐánh đổi\nPhải quản lý bản cũ.',.5,1.84,2.84,2.94)
card('Nội dung','Thuận lợi\nHTML có sẵn.\n\nĐánh đổi\nĐổi nội dung cần dựng.',3.58,1.84,2.84,2.94)
card('Dịch vụ','Thuận lợi\nTách năng lực backend.\n\nĐánh đổi\nPhụ thuộc API và quyền.',6.66,1.84,2.84,2.94)

# 06
new('Từ JAMstack đến ScriptHammer','02 / Hệ thống cụ thể','Mã nguồn ScriptHammer trong workspace',
    'ScriptHammer là một nền tảng Next.js với xác thực, thanh toán, nhắn tin mã hóa, giao diện quản trị và PWA. Chọn ba miền auth, messaging và payments làm kịch bản đại diện cho kiến trúc. Những tính năng khác như blog, bản đồ và 3D vẫn nằm trong frontend nhưng không được phân tích chi tiết từng mô-đun. Kiến trúc chính theo cấu hình Supabase mặc định.',
    'section_divider',layout='SECTION_HEADER',special=True)
absolute_text('02',3.35,1.28,3.3,.92,44,INK,True,align='ctr')
absolute_text('Phân tích\nScriptHammer',2.65,2.48,4.7,1.1,27,INK,True,align='ctr')
absolute_text('Frontend tĩnh; nghiệp vụ động\nĐối chiếu cấu hình và mã nguồn',3.0,3.78,4,.7,13,BLUE,align='ctr')

# 07
new('ScriptHammer ghép nội dung với nghiệp vụ động','02 / Phạm vi phân tích','src/app; src/services; src/lib/payments; public/sw.js',
    'Blog và docs có nội dung đọc khi dựng; các trang React tăng cường hành vi trên trình duyệt. Auth dùng Supabase, messaging có mã hóa và hàng đợi ngoại tuyến, payments dùng Edge Functions với Stripe hoặc PayPal. Kho mã còn có giao diện admin và các tính năng bản đồ, 3D. Sự hiện diện của mã không chứng minh mọi dịch vụ đều đang được cấu hình hoặc hoạt động ở bản triển khai thật.', 'three_column')
card('Giao diện và nội dung','Next.js + React\nBlog và tài liệu\nThành phần dùng chung\nPWA và hỗ trợ truy cập',.5,1.84,2.84,2.94)
card('Nghiệp vụ người dùng','Đăng nhập và hồ sơ\nNhắn tin mã hóa\nThanh toán / thuê bao\nQuản trị',3.58,1.84,2.84,2.94)
card('Dịch vụ phụ trợ','Supabase Auth / Data\nRealtime và Storage\nEdge Functions\nStripe, PayPal, email',6.66,1.84,2.84,2.94)

# 08
new('Trình duyệt kết nối frontend tĩnh với backend','02 / Sơ đồ hệ thống hiện tại','next.config.ts; layout.tsx; Supabase client; Edge Functions',
    'Đây là sơ đồ thành phần cho cấu hình mặc định. Pages phân phối HTML/CSS/JS; trình duyệt mới là nơi gọi Supabase qua HTTPS và kết nối Realtime. Edge Functions xử lý việc cần bí mật và tích hợp dịch vụ thanh toán/email. Edge có thể đọc, ghi dữ liệu backend. Cache Storage và IndexedDB là lưu trữ của trình duyệt. Không có Next.js application server trong luồng production static export.', 'process_flow',layout='TITLE_ONLY')
node('GitHub Pages','HTML / CSS / JS',.55,1.9,2.65,1.13)
node('Trình duyệt','React + các dịch vụ UI',3.68,1.9,2.65,1.13)
node('Supabase','Auth • Data • Realtime\nStorage',6.81,1.9,2.65,1.13)
line(3.2,2.47,3.68,2.47,arrow=True)
line(6.33,2.47,6.81,2.47,arrow=True)
node('Lưu trong trình duyệt','Cache / IndexedDB',.55,4.0,2.65,1.13)
node('Edge Functions','Bí mật và nghiệp vụ',3.68,4.0,2.65,1.13)
node('Dịch vụ bên ngoài','Stripe / PayPal / email',6.81,4.0,2.65,1.13)
line(5,3.03,5,4,arrow=True)
line(6.33,4.56,6.81,4.56,arrow=True)
path([(3.68,2.6),(3.43,2.6),(3.43,3.48),(1.87,3.48),(1.87,4)])
path([(6.1,4),(6.55,3.48),(8.14,3.48),(8.14,3.03)])
text('HTTPS / WS',6.18,3.13,2.3,.28,10,BLUE,True)

# 09
new('Cấu hình và mã xác nhận frontend được xuất tĩnh','02 / Đối chiếu JAMstack với triển khai','next.config.ts; blog/page.tsx; deploy.yml; stripe.ts',
    'next.config.ts đặt output: export, trailingSlash và images.unoptimized. Blog đọc JSON qua fs khi dựng; tuyến slug có generateStaticParams. Workflow dựng và xuất bản tài nguyên tĩnh. Các thao tác động gọi Supabase hoặc Edge Functions từ browser. Server Component vẫn có thể chạy trong lúc build; vì vậy không nên nói toàn bộ logic của dự án chỉ chạy ở trình duyệt.', 'table')
table(['Nguyên lý','Bằng chứng trong mã'],[
    ['Dựng trước','output: export; blog đọc JSON khi build'],
    ['Tuyến sinh sẵn','generateStaticParams cho blog / docs'],
    ['Phân phối tệp','out/ → artifact → GitHub Pages'],
    ['Dữ liệu động','Supabase client; gọi Edge Functions']], [2.6,6.4])
callout('Server Component ở bước build không phải SSR theo từng yêu cầu khi production.')

# Bổ sung theo E06/E08/E09: phân biệt mode và pipeline đúng ScriptHammer.
new('Bốn chế độ khác nhau ở thời điểm tạo HTML','02 / CSR — SSR — SSG — ISR','next.config.ts; blog/[slug]/page.tsx; Supabase client',
    'CSR dựng phần giao diện động ở browser từ JavaScript và API. SSR tạo HTML theo từng request trên server. SSG sinh HTML lúc build. ISR tái tạo trang trên hạ tầng runtime hỗ trợ sau lần build. ScriptHammer dùng SSG/static export cho frontend và CSR cho dữ liệu theo phiên. GitHub Pages chỉ phục vụ tệp; cấu hình output export không hỗ trợ Next.js SSR theo request hay ISR. Server Component có thể chạy lúc build. Các chế độ SSR và ISR ở đây là đối chiếu lý thuyết, không phải tính năng đã chạy trong demo.', 'table')
table(['Chế độ','HTML / cập nhật','Trong ScriptHammer'],[
    ['CSR','Browser + API','Auth, messaging, payments'],
    ['SSR','Server mỗi request','Không có trong static export'],
    ['SSG','Build → tệp HTML','Blog và routes xuất tĩnh'],
    ['ISR','Runtime tái tạo trang','Không có trên Pages']], [1.15,3.35,4.5])
callout('Static export + tương tác CSR có thật; SSR và ISR chỉ dùng để so sánh.')

new('Blog đi qua JSON trước khi sinh HTML tĩnh','02 / Pipeline nội dung ScriptHammer','generate-blog-data.js; blog-data.json; blog/[slug]/page.tsx',
    'Nguồn là public/blog/*.md, không phải _posts của Blog Starter. Lệnh pnpm run generate:blog dùng gray-matter đọc frontmatter và nội dung rồi ghi src/lib/blog/blog-data.json. Trang danh sách đọc JSON; generateStaticParams lấy slug từ JSON. Trang chi tiết dùng markdownProcessor.process để tạo nội dung HTML trong lần build/export. prebuild và deploy.yml hiện không gọi generate:blog, nên phải chạy bước sinh JSON rõ ràng khi cập nhật Markdown. Chỉ sửa Markdown rồi next build có thể vẫn lấy JSON cũ. Sơ đồ mô tả mã, chưa chạy build ứng dụng trong lượt này.', 'process_flow',layout='TITLE_ONLY')
for x,a,b in [(.55,'Markdown','public/blog/*.md'),(3.68,'Sinh JSON','generate:blog + gray-matter'),(6.81,'Dữ liệu build','src/lib/blog/blog-data.json')]:
    node(a,b,x,1.9,2.65,1.12)
for a,b in [(3.2,3.68),(6.33,6.81)]: line(a,2.46,b,2.46,arrow=True)
node('Routes + markdownProcessor','generateStaticParams → trang blog',.55,3.76,4.0,1.15)
node('Export → hosting → browser','HTML + assets; không render lại mỗi request',5.45,3.76,4.0,1.15)
path([(8.14,3.02),(8.14,3.35),(2.55,3.35),(2.55,3.76)])
line(4.55,4.33,5.45,4.33,arrow=True)
callout('generate:blog là bước riêng; prebuild không tự sinh lại blog-data.json.',5.06)

new('Nội dung mới cần sinh dữ liệu và phát hành lại','02 / Rebuild và vòng đời cache','package.json; deploy.yml; stamp-sw-version.mjs; public/sw.js',
    'Kịch bản ôn thi: bản A đang được phục vụ; thay Markdown nguồn chưa đổi HTML của bản A. Sinh lại JSON, build/export bản B rồi xuất bản artifact thì hosting mới có HTML B. Browser vẫn có thể thấy cache hoặc service worker cũ, vì vậy cần đối chiếu artifact và phiên sạch với phiên cũ. Build gọi strip-css-script-tags và stamp-sw-version; workflow giữ assets cũ để giảm lỗi chunk cho client còn mở. API cập nhật dữ liệu theo phiên mà không cần rebuild blog. Đây là hướng dẫn expected result, không phải nhật ký chạy hoặc bằng chứng CDN thật.', 'process_flow')
card('1 / Sửa nguồn','Markdown đổi.\n\nHTML bản A vẫn giữ\nnội dung đã phát hành.',.5,1.84,2.84,2.8)
card('2 / Dựng bản B','generate:blog → build\n\nKiểm tra JSON, slug\nvà tệp HTML export.',3.58,1.84,2.84,2.8)
card('3 / Phát hành','Artifact B → hosting\n\nĐối chiếu cache / SW\nvới một phiên sạch.',6.66,1.84,2.84,2.8)
line(3.34,3.2,3.58,3.2,arrow=True)
line(6.42,3.2,6.66,3.2,arrow=True)
callout('API thay dữ liệu động; rebuild thay nội dung đã dựng và cấu hình NEXT_PUBLIC_*.')

# 10
new('Mô hình 4+1 tách năm câu hỏi về hệ thống','03 / Khung phân tích','Philippe Kruchten, mô hình 4+1, 1995',
    'Logic giải thích các năng lực nghiệp vụ; phát triển giải thích tổ chức mã và đơn vị dựng; tiến trình giải thích sự kiện và tương tác lúc chạy; vật lý giải thích nơi đặt tài nguyên và dịch vụ. Kịch bản nối bốn góc nhìn. Trong JAMstack, việc phân biệt bước dựng với runtime đặc biệt quan trọng để tránh nhầm runner CI thành máy chủ ứng dụng.', 'icon_grid')
node('Logic','Những trách nhiệm nào?',.55,1.88,3.62,1.16)
node('Phát triển','Mã và bản dựng tổ chức ra sao?',5.83,1.88,3.62,1.16)
node('Tiến trình','Đăng nhập / gửi / thanh toán?',.55,3.79,3.62,1.16)
node('Vật lý','Tệp, dữ liệu và mã chạy ở đâu?',5.83,3.79,3.62,1.16)
rect(4.25,2.97,1.5,1.05,BLUE,rounded=True)
text('+1',4.4,3.07,1.2,.47,24,WHITE,True,align='ctr')
text('Kịch bản',4.37,3.62,1.26,.27,12,WHITE,True,align='ctr')
for a,b in [((4.17,2.45),(4.5,2.97)),((5.83,2.45),(5.5,2.97)),((4.17,4.36),(4.5,4.02)),((5.83,4.36),(5.5,4.02))]: line(*a,*b,arrow=True)

# 11
new('Góc nhìn logic phân chia giao diện và nghiệp vụ','03 / Góc nhìn 1 — logic','src/app; contexts/AuthContext; services/messaging; lib/payments',
    'Routes và các thành phần dựng giao diện. Contexts và hooks kết nối trạng thái UI với dịch vụ. AuthContext điều phối phiên; MessageService điều phối mã hóa và lấy/gửi tin; thư viện payments điều phối checkout và kết quả. Backend sở hữu xác thực, lưu dữ liệu và thao tác đặc quyền. Các nhóm trách nhiệm là mô-đun trong một frontend, không phải các micro-frontend phát hành độc lập.', 'three_column')
card('Giao diện','Routes và components\nContext / hooks\nĐiều hướng, consent\nTrạng thái hiển thị',.5,1.84,2.84,2.94)
card('Điều phối nghiệp vụ','Phiên đăng nhập\nMã hóa và hàng đợi tin\nLuồng checkout\nĐồng bộ dữ liệu',3.58,1.84,2.84,2.94)
card('Năng lực backend','Auth / Postgres / RLS\nRealtime / Storage\nEdge Functions\nCổng thanh toán',6.66,1.84,2.84,2.94)

# 12
new('Quyền truy cập được thực thi ở backend','03 / Góc nhìn logic — ranh giới tin cậy','ProtectedRoute; SQL migration; create-stripe-checkout',
    'ProtectedRoute kiểm soát trải nghiệm hiển thị trên client. Người dùng vẫn có thể tự gửi yêu cầu API, nên kiểm soát quyền phải nằm ở backend. Với đường Data API thông thường, JWT gắn danh tính và RLS kiểm tra từng hàng. Edge dùng service role có thể bỏ qua RLS; create-stripe-checkout vì vậy xác minh JWT và kiểm tra chủ sở hữu payment_intent. Khóa public/anon không cấp quyền quản trị.', 'process_flow')
node('Trình duyệt','Public / anon key + JWT\nKhông giữ service role',.55,2.02,2.65,1.35)
node('Data API + RLS','Kiểm tra danh tính\nChỉ cho phép hàng hợp lệ',3.68,2.02,2.65,1.35)
node('Postgres','Hồ sơ, tin, giao dịch\nChính sách và ràng buộc',6.81,2.02,2.65,1.35)
line(3.2,2.7,3.68,2.7,arrow=True)
line(6.33,2.7,6.81,2.7,arrow=True)
node('Đường đặc quyền qua Edge','Xác minh người gọi + kiểm tra nghiệp vụ trước khi dùng service role.',.55,4.05,8.9,1.08,WHITE)
path([(1.87,3.37),(1.87,3.7),(5,3.7),(5,4.05)])

# 13
new('Góc nhìn phát triển có ba nhóm đầu ra riêng','03 / Góc nhìn 2 — phát triển','package.json; src/; supabase/; .github/workflows/',
    'Một repository chứa frontend Next.js, schema/policies SQL và mã Edge Functions chạy Deno. Frontend được dựng thành tệp; migration và function phải áp dụng vào Supabase theo quy trình backend riêng. tsconfig của ứng dụng loại supabase ra; workflow edge-functions.yml có deno check riêng. dotnet-messaging là backend thay thế tùy chọn, không phải một phần của export Pages.', 'three_column',layout='TITLE_ONLY')
card('Frontend','src/app, components\ncontexts, hooks, services\nNext.js + TypeScript\nĐầu ra: HTML / CSS / JS',.5,1.84,2.84,3.03)
card('Backend','supabase/migrations\nsupabase/functions\nSQL + Deno TypeScript\nĐầu ra: schema / API',3.58,1.84,2.84,3.03)
card('Công cụ và kiểm tra','scripts, tests\nDocker, Storybook\nVitest / Playwright\nWorkflow GitHub Actions',6.66,1.84,2.84,3.03)

# 14
new('Pipeline kiểm tra tệp trước khi phát hành lên Pages','03 / Góc nhìn phát triển — dựng và phát hành','package.json; .github/workflows/deploy.yml',
    'Push main kích hoạt workflow deploy. Runner cài pnpm, chạy prebuild rồi next build. Các gate kiểm tra cú pháp chunk, ngân sách tải đầu, canonical và đầu ra ghép. Storybook được ghép vào artifact. retain-previous-assets giữ tài nguyên cũ theo cửa sổ thời gian; bước này cho phép tiếp tục khi lỗi. Artifact merged-output được upload rồi deploy lên Pages. Đây là cấu hình pipeline trong mã, không phải bằng chứng một lần deploy vừa chạy.', 'process_flow',layout='TITLE_ONLY')
for x,a,b in [(.55,'Nguồn','Mã + nội dung'),(3.68,'Dựng','prebuild → next build'),(6.81,'Kiểm tra','Chunk / tải đầu / URL')]: node(a,b,x,1.94,2.65,1.16)
line(3.2,2.52,3.68,2.52,arrow=True)
line(6.33,2.52,6.81,2.52,arrow=True)
node('GitHub Pages','Nhận artifact tĩnh',.55,4.04,3.5,1.12)
node('merged-output','Ghép Storybook; giữ tài nguyên cũ',5.55,4.04,3.9,1.12)
line(8.14,3.1,8.14,4.04,arrow=True)
line(5.55,4.6,4.05,4.6,arrow=True)

# 15
new('Đăng nhập diễn ra qua API từ trình duyệt','03 / Góc nhìn 3 — tiến trình xác thực','AuthContext.tsx; lib/supabase/client.ts; auth/callback',
    'AuthContext gọi signInWithPassword hoặc theo dõi phiên từ Supabase. Luồng OAuth/link dùng callback client và PKCE, không cần máy chủ callback Next.js trong bản static export. Client có persistSession, autoRefreshToken và chọn storage theo lựa chọn ghi nhớ. Sau đăng nhập, JWT đi cùng yêu cầu dữ liệu và RLS thực thi quyền. Không nên coi trạng thái isAuthenticated trong React là rào bảo mật.', 'process_flow',layout='TITLE_ONLY')
for x,label in [(.55,'Giao diện'),(3.6,'Supabase Auth'),(6.65,'Data API / RLS')]:
    rect(x,1.82,2.8,.5,BLUE,rounded=True)
    text(label,x+.1,1.95,2.6,.27,13,WHITE,True,align='ctr')
for x in [1.95,5,8.05]: line(x,2.4,x,4.85,GREY,dashed=True,width=.8)
for y,a,b,label in [(2.7,1.95,5,'1  yêu cầu đăng nhập'),(3.3,5,1.95,'2  phiên + access token'),(3.92,1.95,8.05,'3  yêu cầu dữ liệu + JWT'),(4.62,8.05,1.95,'4  dữ liệu theo quyền')]:
    line(a,y,b,y,arrow=True)
    text(label,min(a,b)+.08,y-.31,abs(b-a)-.15,.28,11.5)
text('JWT xác định người dùng; RLS quyết định hàng dữ liệu nào được phép truy cập.',.6,5.05,8.8,.26,11,MUTED)

# 16
new('Nội dung tin nhắn được mã hóa trước khi gửi','03 / Góc nhìn tiến trình — nhắn tin trực tiếp','message-service.ts; encryption.ts; messaging/providers',
    'Sơ đồ tập trung tin nhắn trực tiếp. MessageService kiểm tra phiên và khóa, lấy thông tin hội thoại rồi dùng ECDH và AES-GCM để mã hóa trong browser. Provider chuyển ciphertext, IV và key version tới backend. Phía nhận lấy dữ liệu được phân quyền và giải mã tại browser. Realtime có thể kích hoạt lấy lại dữ liệu; không giả định mọi đường nhận tin đều chỉ dùng một cơ chế push. Metadata vẫn tồn tại ngoài nội dung được mã hóa.', 'process_flow')
node('Trình duyệt A','Nội dung rõ → mã hóa\nECDH / AES-GCM',.55,1.98,3.45,1.35)
node('Data API + Postgres','JWT / RLS; lưu ciphertext\nIV và phiên bản khóa',5.95,1.98,3.45,1.35)
line(4,2.65,5.95,2.65,arrow=True)
text('Gửi ciphertext',4.12,2.94,1.7,.36,11,BLUE,True,align='ctr')
node('Trình duyệt B','Nhận / lấy lại theo quyền → giải mã → hiển thị',.55,4.05,8.85,1.08)
path([(7.68,3.33),(7.68,3.7),(5,3.7),(5,4.05)])

# 17
new('Ngoại tuyến cần hàng đợi và chính sách đồng bộ','03 / Góc nhìn tiến trình — PWA và dữ liệu cục bộ','public/sw.js; messaging/database.ts; offline-queue-service.ts',
    'Service worker cache trang/tài nguyên theo quy tắc; nó bỏ qua request không phải GET và bỏ qua lưu lượng router _next hoặc .txt. Messaging dùng Dexie/IndexedDB cho cache và hàng đợi. Gửi offline cần có phiên, khóa và dữ liệu hội thoại khả dụng. Khi đồng bộ, UUID ổn định được dùng làm client_generated_id để chống trùng. Hàng chờ có cả nội dung rõ phục vụ UI; sync thành công xóa content và plaintext_content. Không thể nói mọi dữ liệu cục bộ đều chỉ là ciphertext.', 'three_column')
card('Service worker','Cache trang / tài nguyên\nFallback khi mất mạng\nKhông chặn mọi request\nKhông thay backend',.5,1.84,2.84,2.94)
card('IndexedDB','Cache tin đã lấy\nHàng đợi gửi\nTrạng thái và khóa\nCần dữ liệu có sẵn',3.58,1.84,2.84,2.94)
card('Khi có mạng lại','Thử lại có backoff\nUUID chống ghi trùng\nCập nhật trạng thái\nXóa nội dung rõ đã gửi',6.66,1.84,2.84,2.94)
callout('Tin đang chờ có thể chứa nội dung rõ trong IndexedDB; offline không đồng nghĩa an toàn.')

# 18
new('Webhook xác nhận thanh toán; URL trả về chỉ hỗ trợ UI','03 / Góc nhìn tiến trình — Stripe một lần','payments/stripe.ts; create-stripe-checkout; stripe-webhook',
    'Browser gửi payment_intent_id cùng JWT tới Edge. Edge xác minh chủ sở hữu, tình trạng thanh toán và session cũ trước khi tạo Stripe Checkout. Người dùng được chuyển sang URL do backend trả về. Stripe gửi webhook có chữ ký; handler kiểm tra chữ ký, chế độ test/live, claim event chống xử lý trùng rồi cập nhật dữ liệu. Browser có thể gọi verify-stripe-session khi quay lại, nhưng URL success không phải bằng chứng thanh toán có thẩm quyền.', 'process_flow',layout='TITLE_ONLY')
node('Trình duyệt','POST intent_id + JWT',.55,1.92,2.65,1.12)
node('Edge tạo checkout','Kiểm tra → tạo session',3.68,1.92,2.65,1.12)
node('Stripe Checkout','Người dùng thanh toán',6.81,1.92,2.65,1.12)
line(3.2,2.48,3.68,2.48,arrow=True)
line(6.33,2.48,6.81,2.48,arrow=True)
node('Postgres','Ghi kết quả theo event',.55,4.04,3.5,1.12)
node('Edge nhận webhook','Xác minh chữ ký; chống trùng',5.55,4.04,3.9,1.12)
line(8.14,3.04,8.14,4.04,arrow=True)
line(5.55,4.6,4.05,4.6,arrow=True)
text('Browser kiểm tra trạng thái khi quay lại; webhook xử lý xác nhận backend.',.6,5.14,8.8,.28,11,MUTED)

# 19
new('Góc nhìn vật lý tách nơi dựng khỏi nơi thực thi','03 / Góc nhìn 4 — vật lý','deploy.yml; next.config.ts; supabase/functions; Docker Compose',
    'Runner CI chạy Node/pnpm để tạo artifact rồi kết thúc. GitHub Pages giữ tệp. Thiết bị người dùng chạy React, service worker và lưu trữ browser. Supabase thực thi Auth, Data API, Postgres, Realtime, Storage và Edge; bên ngoài là nhà cung cấp thanh toán/email. Không suy ra vị trí địa lý hay cấu hình hạ tầng sản xuất từ mã này. Docker dev server cục bộ không xuất hiện trong topology production static export.', 'process_flow',layout='TITLE_ONLY')
node('Runner CI','Node / pnpm\nChỉ phục vụ bước dựng',.55,1.91,2.65,1.33)
node('GitHub Pages','Lưu artifact tĩnh\nKhông chạy next start',3.68,1.91,2.65,1.33)
node('Thiết bị người dùng','Browser + SW\nCache / IndexedDB',6.81,1.91,2.65,1.33)
line(3.2,2.58,3.68,2.58,arrow=True,dashed=True)
line(6.33,2.58,6.81,2.58,arrow=True)
node('Supabase managed','Auth / DB / Realtime / Storage / Edge',.55,4.05,4,1.08)
node('Nhà cung cấp ngoài','Stripe / PayPal / email',5.45,4.05,4,1.08)
path([(8.14,3.24),(8.14,3.65),(2.55,3.65),(2.55,4.05)])
line(4.55,4.59,5.45,4.59,arrow=True)

# 20
new('Frontend, schema và secrets có vòng đời khác nhau','03 / Góc nhìn vật lý — các đơn vị triển khai','deploy.yml; SQL migration; Edge Functions; backend.config.ts',
    'Các biến NEXT_PUBLIC được nhúng vào frontend khi build, kể cả lựa chọn provider. Đổi chúng đòi hỏi dựng và phát hành frontend phù hợp. Schema/policies phải áp dụng vào backend; mã Edge và secrets cũng có quy trình riêng. Workflow edge-functions.yml là type-check, không tự chứng minh functions đã deploy. Cần giữ tương thích giữa client, schema, Edge API và cấu hình; một lần deploy Pages không tự cập nhật tất cả.', 'table')
table(['Thành phần','Thời điểm thay đổi','Điểm cần quản lý'],[
    ['HTML / JS / CSS','Dựng và deploy Pages','URL, basePath, bản mã'],
    ['NEXT_PUBLIC_*','Được gắn lúc build','Không phải secrets'],
    ['Schema và RLS','Áp dụng migration','Tương thích dữ liệu'],
    ['Edge và secrets','Deploy backend riêng','API và quyền gọi']])
callout('Đổi biến build không tự cập nhật bundle đã phát hành trên Pages.')

# 21
new('Kịch bản kiểm tra kiến trúc qua hành vi người dùng','03 / Góc nhìn +1 — các ca sử dụng','src/app; AuthContext; messaging; payments; deploy workflow',
    'Khách đọc blog/docs là đường tĩnh tiêu biểu. Thành viên đăng nhập, gửi tin và thanh toán là các đường động. Người vận hành phát hành bản frontend mới là kịch bản chất lượng quan trọng. Bốn hành vi dùng các ranh giới khác nhau, nên tải được trang chủ không đủ để chứng minh backend, offline và payment đều hoạt động. Đây là kịch bản suy từ mã, chưa chạy nghiệm thu.', 'icon_grid')
node('Người dùng','Khách / thành viên',.5,2.63,1.95,1.15,BLUE,WHITE)
for x,y,a,b in [(3.16,1.9,'Đọc nội dung','HTML dựng sẵn'),(6.55,1.9,'Đăng nhập','Phiên và dữ liệu theo quyền'),(3.16,3.79,'Gửi tin','Mã hóa; mạng / hàng đợi'),(6.55,3.79,'Thanh toán','Edge; provider; webhook')]: node(a,b,x,y,2.95,1.22)
line(2.45,3.2,3.16,2.51,arrow=True)
line(2.45,3.2,3.16,4.4,arrow=True)
line(6.11,2.51,6.55,2.51,arrow=True)
text('Người vận hành: phát hành bản mới khi người dùng vẫn đang giữ HTML cũ.',.6,5.1,8.8,.28,11,BLUE,True)

# 22
new('Kịch bản thanh toán nối đủ bốn góc nhìn','03 / Góc nhìn +1 — truy vết','stripe.ts; create-stripe-checkout; stripe-webhook; migration',
    'Tiền điều kiện gồm phiên hợp lệ, consent, intent thuộc người gọi, cấu hình Stripe và Edge đã triển khai. Người dùng bắt đầu checkout; Edge tạo session; Stripe xử lý; webhook cập nhật backend; UI đọc kết quả. Logic xác định trách nhiệm, phát triển xác định các đơn vị mã, tiến trình xác định thứ tự bất đồng bộ, vật lý xác định nơi mã thực thi. Kết quả cần được xác nhận bằng backend, không chỉ chuyển hướng thành công.', 'table')
table(['Góc nhìn','Bằng chứng trong kịch bản'],[
    ['Logic','UI điều phối; Edge xác minh; Stripe thu tiền'],
    ['Phát triển','stripe.ts + Deno function + SQL'],
    ['Tiến trình','Request → session → webhook → trạng thái'],
    ['Vật lý','Browser ↔ Supabase ↔ Stripe']], [2.3,6.7])
callout('Kết quả mong đợi: trạng thái backend đúng, event trùng không ghi kết quả lần nữa.')

# 23
new('Độ bền phụ thuộc cache, API và cơ chế thử lại','04 / Kịch bản thuộc tính chất lượng','public/sw.js; retain-previous-assets.mjs; queue; webhook-claim',
    'Khi mất mạng, chỉ các tài nguyên và dữ liệu khả dụng cục bộ có thể dùng tiếp. Khi phát hành mới, HTML cũ có thể trỏ tới chunk đã bị xóa; pipeline giữ tài nguyên theo thời gian và ứng dụng có cơ chế phục hồi. Webhook hoặc flush queue có thể được lặp lại; mã dùng claim event và idempotency key để giới hạn tác dụng trùng. Các cơ chế không tạo bảo đảm offline toàn bộ hoặc exactly-once toàn hệ thống.', 'three_column')
card('Mất kết nối','Có cache → tiếp tục.\nTin có đủ dữ liệu → xếp hàng.\n\nAPI và dữ liệu mới\nvẫn cần mạng.',.5,1.84,2.84,3.0)
card('HTML giữ bản cũ','Giữ chunk cũ theo thời gian.\nKiểm tra artifact.\n\nCache nhiều lớp\ncần phối hợp phiên bản.',3.58,1.84,2.84,3.0)
card('Yêu cầu lặp lại','Webhook claim event.\nQueue dùng UUID ổn định.\n\nRetry không được\nlàm lặp tác dụng.',6.66,1.84,2.84,3.0)

# 24
new('Bảo mật đòi hỏi nhiều ranh giới phối hợp','04 / Bảo mật trong thiết kế','ProtectedRoute; SQL RLS; encryption.ts; Edge auth',
    'Route guard chỉ điều khiển UI. JWT, RLS và kiểm tra nghiệp vụ trong Edge bảo vệ dữ liệu. Khóa đặc quyền và Stripe secret chỉ thuộc backend. Tin nhắn mã hóa phía client bảo vệ nội dung trên đường dữ liệu, nhưng metadata vẫn có và hàng pending có thể giữ nội dung rõ. Private CryptoKey không extractable không ngăn mã độc cùng origin sử dụng khả năng của khóa. Không xem đây là chứng nhận an toàn hay kết quả audit bảo mật.', 'three_column')
card('Danh tính và quyền','UI guard: trải nghiệm.\nJWT: danh tính.\nRLS: quyền theo hàng.\nEdge: kiểm tra nghiệp vụ.',.5,1.84,2.84,2.94)
card('Bí mật backend','Public key được công khai.\nService role ở backend.\nWebhook có chữ ký.\nKhông tin URL success.',3.58,1.84,2.84,2.94)
card('Dữ liệu người dùng','Mã hóa ở browser.\nKhóa không extractable.\nCòn metadata / pending.\nVẫn phải chống XSS.',6.66,1.84,2.84,2.94)

# 25
new('Đổi provider chưa tách hết phụ thuộc backend','04 / Khả năng thay thế backend messaging','backend.config.ts; providers/index.ts; offline-queue-service.ts',
    'NEXT_PUBLIC_BACKEND_PROVIDER mặc định supabase, có nhánh dotnet. MessageService có thể nhận MessagingDataProvider; interface chuyển ciphertext và có hợp đồng quyền. Tuy nhiên offline-queue-service hiện trực tiếp tạo Supabase client rồi gọi from(messages). Vì vậy chưa thể suy ra toàn bộ luồng messaging đã độc lập nhà cung cấp chỉ từ registry. Cần kiểm tra đường offline, realtime, auth và conformance khi thay backend; nhánh .NET không thay toàn bộ Supabase của ứng dụng.', 'process_flow',layout='TITLE_ONLY')
node('MessageService','Mã hóa và điều phối',.55,1.96,2.65,1.14)
node('Chọn provider','Interface dữ liệu',3.68,1.96,2.65,1.14)
node('Supabase / .NET','Supabase là mặc định',6.81,1.96,2.65,1.14)
line(3.2,2.53,3.68,2.53,arrow=True)
line(6.33,2.53,6.81,2.53,arrow=True)
node('Đường sync ngoại tuyến hiện tại','OfflineQueueService → Supabase client → messages; còn phụ thuộc trực tiếp.',.55,4.05,8.9,1.12,WHITE)
path([(1.87,3.1),(1.87,3.62),(5,3.62),(5,4.05)],dashed=True)

# 26
new('Các quyết định chuyển trách nhiệm sang API và client','04 / Phân tích quyết định kiến trúc','next.config.ts; SQL policies; browser services; Edge Functions',
    'Đây là quyết định suy ra từ mã, không phải ADR lịch sử của tác giả. Static export bỏ runtime render production nhưng yêu cầu quản lý nội dung dựng sẵn. BaaS giảm phần tự vận hành nhưng tăng phụ thuộc API và chính sách nền tảng. Edge bảo vệ secrets nhưng tạo đường triển khai riêng. Local-first cải thiện một số tương tác khi mất mạng nhưng tăng việc quản lý dữ liệu và retry ở client.', 'table')
table(['Quyết định','Giá trị','Chi phí'],[
    ['Static export','Phân phối tệp đơn giản','Dựng lại và cache'],
    ['Supabase + RLS','Dữ liệu và quyền có sẵn','Schema / API phụ thuộc'],
    ['Edge Functions','Bí mật ở backend','Vòng đời triển khai riêng'],
    ['Hàng đợi cục bộ','Tiếp tục khi mất mạng','Retry, dữ liệu tồn lưu']])

# 27
new('Cải tiến nên củng cố các ranh giới đã có','04 / Đề xuất — chưa triển khai','Đề xuất từ mã hiện tại; không sửa ScriptHammer',
    'Ưu tiên một là xác định và giảm thời gian lưu nội dung rõ trong hàng chờ, đồng thời giữ khả năng phục hồi và hiển thị UI. Ưu tiên hai là đưa cả send lẫn sync qua interface provider và kiểm thử quyền chung. Ưu tiên ba là kiểm thử hợp đồng artifact/cache cùng tổ hợp frontend, schema và Edge cũ-mới. Repository đã có nhiều cơ chế kiểm thử và giảm thiểu; đề xuất là mở rộng phạm vi và độ nhất quán, không giả định các cơ chế đó đang hoàn toàn thiếu.', 'three_column')
card('1 / Dữ liệu pending','Chính sách lưu nội dung rõ.\nXóa đúng vòng đời.\nKiểm tra logout và retry.\nCân nhắc mã hóa cục bộ.',.5,1.84,2.84,3.05)
card('2 / Provider thống nhất','Send và sync cùng interface.\nGiữ kiểm tra quyền.\nChạy conformance chung.\nRà soát realtime / auth.',3.58,1.84,2.84,3.05)
card('3 / Hợp đồng phát hành','Kiểm tra artifact cuối.\nThử HTML cũ + chunk mới.\nGiữ tương thích schema.\nĐối chiếu cấu hình thật.',6.66,1.84,2.84,3.05)

# 28
new('Trình diễn cần thử cả frontend tĩnh và backend','05 / Gợi ý trình diễn trên lớp','docker-compose.yml; README; deploy workflow',
    'Chỉ là hướng dẫn, không phải các bước đã thực thi. Chuẩn bị môi trường và dịch vụ thử nghiệm theo tài liệu dự án. Docker Compose hiện cho phép cấp cổng host tự động; dùng docker compose port scripthammer 3000 để tìm cổng, thay vì mặc định luôn localhost:3000. Dựng production trong service builder riêng bằng docker compose run --rm builder pnpm build. Sau đó kiểm tra tệp export và các kịch bản đăng nhập, tin nhắn, mất mạng, payment test. Không cần giao dịch tiền thật để minh họa kiến trúc.', 'process_flow')
for j,(a,b) in enumerate([
    ['Chuẩn bị','Theo hướng dẫn dự án; xác nhận dịch vụ thử nghiệm.'],
    ['Dựng tĩnh','Dùng builder riêng; kiểm tra đầu ra HTML / JS / CSS.'],
    ['Theo dõi','Đăng nhập → tin nhắn → mất mạng → đồng bộ lại.'],
    ['Đối chiếu','Checkout thử nghiệm; kiểm tra webhook và dữ liệu.']]):
    y=1.85+j*.79
    rect(.5,y,.47,.5,BLUE,rounded=True)
    text(str(j+1),.63,y+.13,.23,.28,14,WHITE,True)
    text(a,1.15,y+.03,1.65,.55,14.5,BLUE,True)
    text(b,3.05,y+.03,6.3,.59,13.5)

# 29
new('Frontend tĩnh không làm mất backend hoặc độ phức tạp','05 / Kết luận','Tổng hợp phân tích ScriptHammer',
    'ScriptHammer minh họa cách tách giao diện dựng trước khỏi nghiệp vụ động. Các quyết định kiến trúc quan trọng chuyển sang API, quyền ở dữ liệu, vòng đời client, cache và phối hợp phát hành. 4+1 giúp tránh nhầm mã nguồn với tiến trình hoặc máy chủ phân phối với nơi xử lý nghiệp vụ. Câu hỏi kết luận: thay cấu hình Supabase có chỉ cần đổi biến trên máy chủ không, hay phải phát hành frontend mới? Hãy giải thích bằng góc nhìn phát triển và vật lý.',
    'big_statement',layout='MAIN_POINT',special=True)
absolute_text('GIAO DIỆN TĨNH\nNGHIỆP VỤ ĐỘNG',2.1,1.67,5.8,1.05,28,INK,True,align='ctr')
absolute_text('Ranh giới API và dữ liệu\nquyết định chất lượng hệ thống',2.0,3.0,6,1.05,21.5,BLUE,True,align='ctr')
absolute_text('Thảo luận: đổi cấu hình backend có cần phát hành lại frontend?',1.8,4.56,6.4,.45,11.5,INK,align='ctr')

# 30
new('Tài liệu gốc hỗ trợ các khái niệm kiến trúc','Phụ lục / Tham khảo','Nguồn chính thức; các liên kết có thể mở từ slide',
    'Nguồn khái niệm JAMstack là trang giải thích chính thức. Tài liệu Next.js giải thích static export; phiên bản mới nhất chỉ dùng để tham khảo khái niệm, còn cấu hình cụ thể theo mã Next.js 15.5 của repository. Tài liệu Supabase giải thích RLS và Edge Functions. Mô hình góc nhìn dựa trên Kruchten. Công cụ trình chiếu là mpuig/agent-slides. Các cơ chế ScriptHammer đều được đối chiếu với mã local.', 'content_text')
for j,(label,url) in enumerate([
    ['JAMstack — nguyên lý kiến trúc','https://jamstack.org/what-is-jamstack/'],
    ['Next.js — Static Exports','https://nextjs.org/docs/app/guides/static-exports'],
    ['Supabase — Row Level Security','https://supabase.com/docs/guides/database/postgres/row-level-security'],
    ['Supabase — Edge Functions','https://supabase.com/docs/guides/functions'],
    ['Kruchten — Mô hình 4+1 (1995)','https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf']]):
    y=1.8+j*.65
    text(label,.6,y,8.8,.3,13.3,BLUE,True,href=url)
    text(url,.6,y+.33,8.8,.26,9.8,MUTED,href=url)
text('Công cụ: github.com/mpuig/agent-slides',.6,5.14,8.8,.27,10.5,BLUE,href='https://github.com/mpuig/agent-slides')

# 31
new('Bản đồ nguồn phân biệt tài liệu với triển khai thật','Phụ lục / Phạm vi và bằng chứng','ScriptHammer; commit a2dd31ae25ea30c678d990432c7e2b60b4faeda7',
    'README và sơ đồ cũ nói tới mười hai Edge Functions, nhưng snapshot hiện tại có mười tám thư mục endpoint chứa index.ts; không dùng số cũ làm mô tả đầy đủ hệ thống. Docker Compose cũng dùng cổng host tự cấp nếu không đặt SH_PORT. Vì vậy slide ưu tiên mã hiện tại. Phân tích giới hạn ở cấu hình và đường đi đại diện; chưa build hoặc chạy ứng dụng, chưa xác nhận backend/Pages đang triển khai thế nào. Chưa sửa mã nguồn ScriptHammer.', 'table')
table(['Nhận định','Tệp đối chiếu'],[
    ['Static export','next.config.ts; deploy.yml'],
    ['Nội dung dựng sẵn','app/blog; app/docs; generateStaticParams'],
    ['Phiên và quyền','AuthContext; supabase/client; SQL RLS'],
    ['Tin nhắn / ngoại tuyến','message-service; offline-queue-service'],
    ['Thanh toán / webhook','payments/stripe; supabase/functions'],
    ['Nhánh backend tùy chọn','backend.config; messaging/providers']], [3.05,5.95])
text('Phạm vi: rà soát mã tĩnh; số liệu trong tài liệu cũ được đối chiếu lại.',.6,5.1,8.8,.27,11,MUTED)

# 32 — Trang Thanks gốc giữ dòng ghi công và liên kết.
new('Cảm ơn!','Kết thúc','Mẫu Slidesgo; mã nguồn ScriptHammer; agent-slides',
    'Mời thảo luận: thành phần nào chạy lúc build, trong trình duyệt và ở backend? Nếu API ngừng hoạt động, phần nào vẫn dùng được? Chuyển sang .NET provider đã đủ cho sync offline chưa? Các câu hỏi giúp liên kết lại mô hình 4+1. Trang này giữ bố cục Cảm ơn và các liên kết ghi công của mẫu.',
    'end_slide',layout='CUSTOM_9',special=True)
absolute_text('CẢM ƠN!',2.35,.72,5.3,.9,38,INK,True,align='ctr')
absolute_text('Câu hỏi và thảo luận',2.65,1.87,4.7,.5,20,BLUE,True,align='ctr')
absolute_text('Khi API mất kết nối, phần nào\ncủa ScriptHammer vẫn tiếp tục hoạt động?',2.1,2.75,5.8,1.1,18,INK,align='ctr')

finish()
