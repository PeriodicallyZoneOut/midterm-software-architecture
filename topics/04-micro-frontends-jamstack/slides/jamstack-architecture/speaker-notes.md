# Ghi chú thuyết trình

Thời lượng dự kiến: 25–30 phút, chưa gồm thảo luận.

## 01. Kiến trúc JAMstack — ScriptHammer

Bài trình bày đi từ nguyên lý JAMstack đến cách ScriptHammer triển khai chúng. Trọng tâm là ranh giới giữa dựng trước, phục vụ tệp, thực thi ở trình duyệt và backend API. Dùng mô hình 4+1 để tách trách nhiệm, mã nguồn, luồng thực thi và hạ tầng. Phân tích dựa trên mã nguồn trong workspace; chưa chạy ứng dụng, gọi backend hoặc xác minh bản triển khai trực tuyến.

Nguồn: ScriptHammer; mẫu Technology Consulting by Slidesgo

## 02. JAMstack tách giao diện dựng sẵn khỏi API

Hai nguyên lý cốt lõi là dựng trước giao diện và tách giao diện khỏi các dịch vụ nghiệp vụ. HTML cùng tài nguyên được phục vụ như tệp; JavaScript gọi API khi cần dữ liệu hoặc thao tác cá nhân hóa. Đây là cách phân chia trách nhiệm của kiến trúc, không phải tên một framework cụ thể.

Nguồn: jamstack.org/what-is-jamstack

## 03. Luồng dựng và luồng sử dụng diễn ra khác lúc

Hàng trên là luồng tạo và phát hành tài nguyên. Hàng dưới là luồng người dùng sử dụng ứng dụng. Tệp tĩnh không tự thay đổi mỗi khi dữ liệu nghiệp vụ thay đổi. API cung cấp dữ liệu theo phiên người dùng. Mũi tên xuống từ kho tệp đến trình duyệt biểu diễn phân phối tài nguyên; hai luồng không phải một chuỗi xử lý HTTP duy nhất.

Nguồn: Sơ đồ minh họa kiến trúc JAMstack

## 04. JAM không giới hạn ứng dụng ở nội dung tĩnh

JavaScript tạo tương tác, API cung cấp năng lực động, còn markup tạo nền giao diện được dựng trước. Một ứng dụng có thể có đăng nhập, thanh toán và trò chuyện nhưng vẫn phân phối frontend tĩnh. Không có runtime máy chủ Next.js không có nghĩa là không có backend: các dịch vụ API vẫn thực thi trên máy chủ.

Nguồn: Tổng hợp khái niệm; cấu trúc ScriptHammer

## 05. Dựng sẵn đổi chi phí máy chủ thành chi phí tích hợp

Phân phối tệp giảm nhu cầu vận hành máy chủ render theo từng yêu cầu. Đổi lại, nội dung dựng sẵn cần phát hành lại, dịch vụ động phụ thuộc API và cấu hình phiên bản phải đồng bộ. CDN không tự giải quyết truy vấn cơ sở dữ liệu, quyền truy cập hay gửi tiền. Những lợi ích dưới đây là kỳ vọng kiến trúc, không phải kết quả benchmark ScriptHammer.

Nguồn: Phân tích định tính; không phải số đo hiệu năng

## 06. Từ JAMstack đến ScriptHammer

ScriptHammer là một nền tảng Next.js với xác thực, thanh toán, nhắn tin mã hóa, giao diện quản trị và PWA. Chọn ba miền auth, messaging và payments làm kịch bản đại diện cho kiến trúc. Những tính năng khác như blog, bản đồ và 3D vẫn nằm trong frontend nhưng không được phân tích chi tiết từng mô-đun. Kiến trúc chính theo cấu hình Supabase mặc định.

Nguồn: Mã nguồn ScriptHammer trong workspace

## 07. ScriptHammer ghép nội dung với nghiệp vụ động

Blog và docs có nội dung đọc khi dựng; các trang React tăng cường hành vi trên trình duyệt. Auth dùng Supabase, messaging có mã hóa và hàng đợi ngoại tuyến, payments dùng Edge Functions với Stripe hoặc PayPal. Kho mã còn có giao diện admin và các tính năng bản đồ, 3D. Sự hiện diện của mã không chứng minh mọi dịch vụ đều đang được cấu hình hoặc hoạt động ở bản triển khai thật.

Nguồn: src/app; src/services; src/lib/payments; public/sw.js

## 08. Trình duyệt kết nối frontend tĩnh với backend

Đây là sơ đồ thành phần cho cấu hình mặc định. Pages phân phối HTML/CSS/JS; trình duyệt mới là nơi gọi Supabase qua HTTPS và kết nối Realtime. Edge Functions xử lý việc cần bí mật và tích hợp dịch vụ thanh toán/email. Edge có thể đọc, ghi dữ liệu backend. Cache Storage và IndexedDB là lưu trữ của trình duyệt. Không có Next.js application server trong luồng production static export.

Nguồn: next.config.ts; layout.tsx; Supabase client; Edge Functions

## 09. Cấu hình và mã xác nhận frontend được xuất tĩnh

next.config.ts đặt output: export, trailingSlash và images.unoptimized. Blog đọc JSON qua fs khi dựng; tuyến slug có generateStaticParams. Workflow dựng và xuất bản tài nguyên tĩnh. Các thao tác động gọi Supabase hoặc Edge Functions từ browser. Server Component vẫn có thể chạy trong lúc build; vì vậy không nên nói toàn bộ logic của dự án chỉ chạy ở trình duyệt.

Nguồn: next.config.ts; blog/page.tsx; deploy.yml; stripe.ts

## 10. Bốn chế độ khác nhau ở thời điểm tạo HTML

CSR dựng phần giao diện động ở browser từ JavaScript và API. SSR tạo HTML theo từng request trên server. SSG sinh HTML lúc build. ISR tái tạo trang trên hạ tầng runtime hỗ trợ sau lần build. ScriptHammer dùng SSG/static export cho frontend và CSR cho dữ liệu theo phiên. GitHub Pages chỉ phục vụ tệp; cấu hình output export không hỗ trợ Next.js SSR theo request hay ISR. Server Component có thể chạy lúc build. Các chế độ SSR và ISR ở đây là đối chiếu lý thuyết, không phải tính năng đã chạy trong demo.

Nguồn: next.config.ts; blog/[slug]/page.tsx; Supabase client

## 11. Blog đi qua JSON trước khi sinh HTML tĩnh

Nguồn là public/blog/*.md, không phải _posts của Blog Starter. Lệnh pnpm run generate:blog dùng gray-matter đọc frontmatter và nội dung rồi ghi src/lib/blog/blog-data.json. Trang danh sách đọc JSON; generateStaticParams lấy slug từ JSON. Trang chi tiết dùng markdownProcessor.process để tạo nội dung HTML trong lần build/export. prebuild và deploy.yml hiện không gọi generate:blog, nên phải chạy bước sinh JSON rõ ràng khi cập nhật Markdown. Chỉ sửa Markdown rồi next build có thể vẫn lấy JSON cũ. Sơ đồ mô tả mã, chưa chạy build ứng dụng trong lượt này.

Nguồn: generate-blog-data.js; blog-data.json; blog/[slug]/page.tsx

## 12. Nội dung mới cần sinh dữ liệu và phát hành lại

Kịch bản ôn thi: bản A đang được phục vụ; thay Markdown nguồn chưa đổi HTML của bản A. Sinh lại JSON, build/export bản B rồi xuất bản artifact thì hosting mới có HTML B. Browser vẫn có thể thấy cache hoặc service worker cũ, vì vậy cần đối chiếu artifact và phiên sạch với phiên cũ. Build gọi strip-css-script-tags và stamp-sw-version; workflow giữ assets cũ để giảm lỗi chunk cho client còn mở. API cập nhật dữ liệu theo phiên mà không cần rebuild blog. Đây là hướng dẫn expected result, không phải nhật ký chạy hoặc bằng chứng CDN thật.

Nguồn: package.json; deploy.yml; stamp-sw-version.mjs; public/sw.js

## 13. Mô hình 4+1 tách năm câu hỏi về hệ thống

Logic giải thích các năng lực nghiệp vụ; phát triển giải thích tổ chức mã và đơn vị dựng; tiến trình giải thích sự kiện và tương tác lúc chạy; vật lý giải thích nơi đặt tài nguyên và dịch vụ. Kịch bản nối bốn góc nhìn. Trong JAMstack, việc phân biệt bước dựng với runtime đặc biệt quan trọng để tránh nhầm runner CI thành máy chủ ứng dụng.

Nguồn: Philippe Kruchten, mô hình 4+1, 1995

## 14. Góc nhìn logic phân chia giao diện và nghiệp vụ

Routes và các thành phần dựng giao diện. Contexts và hooks kết nối trạng thái UI với dịch vụ. AuthContext điều phối phiên; MessageService điều phối mã hóa và lấy/gửi tin; thư viện payments điều phối checkout và kết quả. Backend sở hữu xác thực, lưu dữ liệu và thao tác đặc quyền. Các nhóm trách nhiệm là mô-đun trong một frontend, không phải các micro-frontend phát hành độc lập.

Nguồn: src/app; contexts/AuthContext; services/messaging; lib/payments

## 15. Quyền truy cập được thực thi ở backend

ProtectedRoute kiểm soát trải nghiệm hiển thị trên client. Người dùng vẫn có thể tự gửi yêu cầu API, nên kiểm soát quyền phải nằm ở backend. Với đường Data API thông thường, JWT gắn danh tính và RLS kiểm tra từng hàng. Edge dùng service role có thể bỏ qua RLS; create-stripe-checkout vì vậy xác minh JWT và kiểm tra chủ sở hữu payment_intent. Khóa public/anon không cấp quyền quản trị.

Nguồn: ProtectedRoute; SQL migration; create-stripe-checkout

## 16. Góc nhìn phát triển có ba nhóm đầu ra riêng

Một repository chứa frontend Next.js, schema/policies SQL và mã Edge Functions chạy Deno. Frontend được dựng thành tệp; migration và function phải áp dụng vào Supabase theo quy trình backend riêng. tsconfig của ứng dụng loại supabase ra; workflow edge-functions.yml có deno check riêng. dotnet-messaging là backend thay thế tùy chọn, không phải một phần của export Pages.

Nguồn: package.json; src/; supabase/; .github/workflows/

## 17. Pipeline kiểm tra tệp trước khi phát hành lên Pages

Push main kích hoạt workflow deploy. Runner cài pnpm, chạy prebuild rồi next build. Các gate kiểm tra cú pháp chunk, ngân sách tải đầu, canonical và đầu ra ghép. Storybook được ghép vào artifact. retain-previous-assets giữ tài nguyên cũ theo cửa sổ thời gian; bước này cho phép tiếp tục khi lỗi. Artifact merged-output được upload rồi deploy lên Pages. Đây là cấu hình pipeline trong mã, không phải bằng chứng một lần deploy vừa chạy.

Nguồn: package.json; .github/workflows/deploy.yml

## 18. Đăng nhập diễn ra qua API từ trình duyệt

AuthContext gọi signInWithPassword hoặc theo dõi phiên từ Supabase. Luồng OAuth/link dùng callback client và PKCE, không cần máy chủ callback Next.js trong bản static export. Client có persistSession, autoRefreshToken và chọn storage theo lựa chọn ghi nhớ. Sau đăng nhập, JWT đi cùng yêu cầu dữ liệu và RLS thực thi quyền. Không nên coi trạng thái isAuthenticated trong React là rào bảo mật.

Nguồn: AuthContext.tsx; lib/supabase/client.ts; auth/callback

## 19. Nội dung tin nhắn được mã hóa trước khi gửi

Sơ đồ tập trung tin nhắn trực tiếp. MessageService kiểm tra phiên và khóa, lấy thông tin hội thoại rồi dùng ECDH và AES-GCM để mã hóa trong browser. Provider chuyển ciphertext, IV và key version tới backend. Phía nhận lấy dữ liệu được phân quyền và giải mã tại browser. Realtime có thể kích hoạt lấy lại dữ liệu; không giả định mọi đường nhận tin đều chỉ dùng một cơ chế push. Metadata vẫn tồn tại ngoài nội dung được mã hóa.

Nguồn: message-service.ts; encryption.ts; messaging/providers

## 20. Ngoại tuyến cần hàng đợi và chính sách đồng bộ

Service worker cache trang/tài nguyên theo quy tắc; nó bỏ qua request không phải GET và bỏ qua lưu lượng router _next hoặc .txt. Messaging dùng Dexie/IndexedDB cho cache và hàng đợi. Gửi offline cần có phiên, khóa và dữ liệu hội thoại khả dụng. Khi đồng bộ, UUID ổn định được dùng làm client_generated_id để chống trùng. Hàng chờ có cả nội dung rõ phục vụ UI; sync thành công xóa content và plaintext_content. Không thể nói mọi dữ liệu cục bộ đều chỉ là ciphertext.

Nguồn: public/sw.js; messaging/database.ts; offline-queue-service.ts

## 21. Webhook xác nhận thanh toán; URL trả về chỉ hỗ trợ UI

Browser gửi payment_intent_id cùng JWT tới Edge. Edge xác minh chủ sở hữu, tình trạng thanh toán và session cũ trước khi tạo Stripe Checkout. Người dùng được chuyển sang URL do backend trả về. Stripe gửi webhook có chữ ký; handler kiểm tra chữ ký, chế độ test/live, claim event chống xử lý trùng rồi cập nhật dữ liệu. Browser có thể gọi verify-stripe-session khi quay lại, nhưng URL success không phải bằng chứng thanh toán có thẩm quyền.

Nguồn: payments/stripe.ts; create-stripe-checkout; stripe-webhook

## 22. Góc nhìn vật lý tách nơi dựng khỏi nơi thực thi

Runner CI chạy Node/pnpm để tạo artifact rồi kết thúc. GitHub Pages giữ tệp. Thiết bị người dùng chạy React, service worker và lưu trữ browser. Supabase thực thi Auth, Data API, Postgres, Realtime, Storage và Edge; bên ngoài là nhà cung cấp thanh toán/email. Không suy ra vị trí địa lý hay cấu hình hạ tầng sản xuất từ mã này. Docker dev server cục bộ không xuất hiện trong topology production static export.

Nguồn: deploy.yml; next.config.ts; supabase/functions; Docker Compose

## 23. Frontend, schema và secrets có vòng đời khác nhau

Các biến NEXT_PUBLIC được nhúng vào frontend khi build, kể cả lựa chọn provider. Đổi chúng đòi hỏi dựng và phát hành frontend phù hợp. Schema/policies phải áp dụng vào backend; mã Edge và secrets cũng có quy trình riêng. Workflow edge-functions.yml là type-check, không tự chứng minh functions đã deploy. Cần giữ tương thích giữa client, schema, Edge API và cấu hình; một lần deploy Pages không tự cập nhật tất cả.

Nguồn: deploy.yml; SQL migration; Edge Functions; backend.config.ts

## 24. Kịch bản kiểm tra kiến trúc qua hành vi người dùng

Khách đọc blog/docs là đường tĩnh tiêu biểu. Thành viên đăng nhập, gửi tin và thanh toán là các đường động. Người vận hành phát hành bản frontend mới là kịch bản chất lượng quan trọng. Bốn hành vi dùng các ranh giới khác nhau, nên tải được trang chủ không đủ để chứng minh backend, offline và payment đều hoạt động. Đây là kịch bản suy từ mã, chưa chạy nghiệm thu.

Nguồn: src/app; AuthContext; messaging; payments; deploy workflow

## 25. Kịch bản thanh toán nối đủ bốn góc nhìn

Tiền điều kiện gồm phiên hợp lệ, consent, intent thuộc người gọi, cấu hình Stripe và Edge đã triển khai. Người dùng bắt đầu checkout; Edge tạo session; Stripe xử lý; webhook cập nhật backend; UI đọc kết quả. Logic xác định trách nhiệm, phát triển xác định các đơn vị mã, tiến trình xác định thứ tự bất đồng bộ, vật lý xác định nơi mã thực thi. Kết quả cần được xác nhận bằng backend, không chỉ chuyển hướng thành công.

Nguồn: stripe.ts; create-stripe-checkout; stripe-webhook; migration

## 26. Độ bền phụ thuộc cache, API và cơ chế thử lại

Khi mất mạng, chỉ các tài nguyên và dữ liệu khả dụng cục bộ có thể dùng tiếp. Khi phát hành mới, HTML cũ có thể trỏ tới chunk đã bị xóa; pipeline giữ tài nguyên theo thời gian và ứng dụng có cơ chế phục hồi. Webhook hoặc flush queue có thể được lặp lại; mã dùng claim event và idempotency key để giới hạn tác dụng trùng. Các cơ chế không tạo bảo đảm offline toàn bộ hoặc exactly-once toàn hệ thống.

Nguồn: public/sw.js; retain-previous-assets.mjs; queue; webhook-claim

## 27. Bảo mật đòi hỏi nhiều ranh giới phối hợp

Route guard chỉ điều khiển UI. JWT, RLS và kiểm tra nghiệp vụ trong Edge bảo vệ dữ liệu. Khóa đặc quyền và Stripe secret chỉ thuộc backend. Tin nhắn mã hóa phía client bảo vệ nội dung trên đường dữ liệu, nhưng metadata vẫn có và hàng pending có thể giữ nội dung rõ. Private CryptoKey không extractable không ngăn mã độc cùng origin sử dụng khả năng của khóa. Không xem đây là chứng nhận an toàn hay kết quả audit bảo mật.

Nguồn: ProtectedRoute; SQL RLS; encryption.ts; Edge auth

## 28. Đổi provider chưa tách hết phụ thuộc backend

NEXT_PUBLIC_BACKEND_PROVIDER mặc định supabase, có nhánh dotnet. MessageService có thể nhận MessagingDataProvider; interface chuyển ciphertext và có hợp đồng quyền. Tuy nhiên offline-queue-service hiện trực tiếp tạo Supabase client rồi gọi from(messages). Vì vậy chưa thể suy ra toàn bộ luồng messaging đã độc lập nhà cung cấp chỉ từ registry. Cần kiểm tra đường offline, realtime, auth và conformance khi thay backend; nhánh .NET không thay toàn bộ Supabase của ứng dụng.

Nguồn: backend.config.ts; providers/index.ts; offline-queue-service.ts

## 29. Các quyết định chuyển trách nhiệm sang API và client

Đây là quyết định suy ra từ mã, không phải ADR lịch sử của tác giả. Static export bỏ runtime render production nhưng yêu cầu quản lý nội dung dựng sẵn. BaaS giảm phần tự vận hành nhưng tăng phụ thuộc API và chính sách nền tảng. Edge bảo vệ secrets nhưng tạo đường triển khai riêng. Local-first cải thiện một số tương tác khi mất mạng nhưng tăng việc quản lý dữ liệu và retry ở client.

Nguồn: next.config.ts; SQL policies; browser services; Edge Functions

## 30. Cải tiến nên củng cố các ranh giới đã có

Ưu tiên một là xác định và giảm thời gian lưu nội dung rõ trong hàng chờ, đồng thời giữ khả năng phục hồi và hiển thị UI. Ưu tiên hai là đưa cả send lẫn sync qua interface provider và kiểm thử quyền chung. Ưu tiên ba là kiểm thử hợp đồng artifact/cache cùng tổ hợp frontend, schema và Edge cũ-mới. Repository đã có nhiều cơ chế kiểm thử và giảm thiểu; đề xuất là mở rộng phạm vi và độ nhất quán, không giả định các cơ chế đó đang hoàn toàn thiếu.

Nguồn: Đề xuất từ mã hiện tại; không sửa ScriptHammer

## 31. Trình diễn cần thử cả frontend tĩnh và backend

Chỉ là hướng dẫn, không phải các bước đã thực thi. Chuẩn bị môi trường và dịch vụ thử nghiệm theo tài liệu dự án. Docker Compose hiện cho phép cấp cổng host tự động; dùng docker compose port scripthammer 3000 để tìm cổng, thay vì mặc định luôn localhost:3000. Dựng production trong service builder riêng bằng docker compose run --rm builder pnpm build. Sau đó kiểm tra tệp export và các kịch bản đăng nhập, tin nhắn, mất mạng, payment test. Không cần giao dịch tiền thật để minh họa kiến trúc.

Nguồn: docker-compose.yml; README; deploy workflow

## 32. Frontend tĩnh không làm mất backend hoặc độ phức tạp

ScriptHammer minh họa cách tách giao diện dựng trước khỏi nghiệp vụ động. Các quyết định kiến trúc quan trọng chuyển sang API, quyền ở dữ liệu, vòng đời client, cache và phối hợp phát hành. 4+1 giúp tránh nhầm mã nguồn với tiến trình hoặc máy chủ phân phối với nơi xử lý nghiệp vụ. Câu hỏi kết luận: thay cấu hình Supabase có chỉ cần đổi biến trên máy chủ không, hay phải phát hành frontend mới? Hãy giải thích bằng góc nhìn phát triển và vật lý.

Nguồn: Tổng hợp phân tích ScriptHammer

## 33. Tài liệu gốc hỗ trợ các khái niệm kiến trúc

Nguồn khái niệm JAMstack là trang giải thích chính thức. Tài liệu Next.js giải thích static export; phiên bản mới nhất chỉ dùng để tham khảo khái niệm, còn cấu hình cụ thể theo mã Next.js 15.5 của repository. Tài liệu Supabase giải thích RLS và Edge Functions. Mô hình góc nhìn dựa trên Kruchten. Công cụ trình chiếu là mpuig/agent-slides. Các cơ chế ScriptHammer đều được đối chiếu với mã local.

Nguồn: Nguồn chính thức; các liên kết có thể mở từ slide

## 34. Bản đồ nguồn phân biệt tài liệu với triển khai thật

README và sơ đồ cũ nói tới mười hai Edge Functions, nhưng snapshot hiện tại có mười tám thư mục endpoint chứa index.ts; không dùng số cũ làm mô tả đầy đủ hệ thống. Docker Compose cũng dùng cổng host tự cấp nếu không đặt SH_PORT. Vì vậy slide ưu tiên mã hiện tại. Phân tích giới hạn ở cấu hình và đường đi đại diện; chưa build hoặc chạy ứng dụng, chưa xác nhận backend/Pages đang triển khai thế nào. Chưa sửa mã nguồn ScriptHammer.

Nguồn: ScriptHammer; commit a2dd31ae25ea30c678d990432c7e2b60b4faeda7

## 35. Cảm ơn!

Mời thảo luận: thành phần nào chạy lúc build, trong trình duyệt và ở backend? Nếu API ngừng hoạt động, phần nào vẫn dùng được? Chuyển sang .NET provider đã đủ cho sync offline chưa? Các câu hỏi giúp liên kết lại mô hình 4+1. Trang này giữ bố cục Cảm ơn và các liên kết ghi công của mẫu.

Nguồn: Mẫu Slidesgo; mã nguồn ScriptHammer; agent-slides