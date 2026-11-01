# Kiểm kê demo và ánh xạ kiến trúc phục vụ vấn đáp giữa kỳ

Ngày kiểm tra: 2026-11-01. Phạm vi: mã nguồn, README, cấu hình triển khai và trạng thái Docker trong workspace. Backlog thực hiện: [TASKS.md](TASKS.md).

Đây là kết quả inspection để lập kế hoạch; chưa chạy load test, audit đầy đủ, replay hay triển khai thêm hệ thống. Các kết quả test ghi trong README cũ là bằng chứng lịch sử, chưa được chạy lại ở lượt kiểm tra này.

## 1. Hiện trạng và lựa chọn demo

| Project | Bằng chứng có trên đĩa | Runtime quan sát được | Dùng cho nội dung nào |
|---|---|---|---|
| Mini Shop (`lab-01/microservices-project-demo/README.md`) | React, Gateway, Products, Orders, Compose, C4, dataflow, báo cáo verification; có `frontend/dist` | Không có container trên Docker daemon đang kiểm tra | Microservices dễ giải thích; 4+1; schema; resilience; có thể bổ sung k6 |
| Online Boutique (`week-03/microservices-demo/README.md`) | Google microservices-demo, gRPC/protobuf, Kubernetes release, cấu hình Istio, Locust | Không có container của hệ thống trên daemon đang kiểm tra; chưa xác nhận cluster bên ngoài | Open source chính cho scalability, microservices + Kubernetes + Istio + monitoring |
| Istio source (`week-03/istio/README.md`) | Source Istio và `samples/addons` có Prometheus/Grafana/Kiali/Jaeger | Có `istioctl` trong PATH; không tìm thấy `kubectl`, `kind`, `minikube`, `k3d` trong PATH | Nguồn cấu hình/tham khảo; tải source không chứng minh control plane đã cài |
| Micro Frontend (`micro-frontend/micro-frontend-demo/README.md`) | Host Main, Products, Cart, Module Federation, PubSub, Zustand, Compose + Nginx; sơ đồ có sẵn | Không có container trên daemon đang kiểm tra | Micro-Frontends; minh họa PubSub trong browser |
| Blog starter (`week-03/jamstack/README.md`) | Hai bản `blog-starter` và `blog-starter-app`; cả hai có thư mục dependency; bản `-app` có lockfile và `.next/dev` | Chưa xác nhận server đang chạy; chưa thấy production prerender manifest ở bản `-app` | JAMstack/SSG; cần chốt một bản và build production |
| People profiles (`week-03/new-app-auth-info/README.md`) | Node API, SQL command state + outbox, RabbitMQ retained stream, publisher, hai consumer, Read DB, trang data-flow | Compose `people-kurrent`: 6 container lâu dài healthy; `init-db` exited 0 | CQRS + EDA + outbox; Event Sourcing cần kiểm chứng thêm |
| ScriptHammer (`week-03/ScriptHammer/README.md`) | Next.js, Supabase/OAuth, cấu hình static export, Compose dev và Compose đánh giá KurrentDB | Không có container trên daemon đang kiểm tra | Open source cho audit bảo mật; bổ sung JAMstack/OAuth nếu cần |

Docker chỉ liệt kê Compose project `people-kurrent` tại thời điểm kiểm tra. Điều này không loại trừ deployment đã dừng/xóa trước đó hoặc deployment trên daemon/cluster khác. Việc kiểm tra socket host bằng `ss` bị giới hạn quyền nên không kết luận các app Node/MariaDB chạy trực tiếp trên host đã dừng.

Các endpoint theo cấu hình, trừ stack People chưa được xác nhận HTTP trong lượt này:

| Demo | URL theo tài liệu/cấu hình | Điểm lưu ý |
|---|---|---|
| People | `http://localhost:3003`, `/data-flow`; RabbitMQ `http://localhost:15672` | 6 container healthy không chứng minh gửi email thành công |
| Mini Shop | `http://localhost:8080` | Có thể trùng cổng web trong Compose Kurrent của ScriptHammer |
| Micro Frontend | `http://localhost:9001` | Docker phục vụ cả host và remotes cùng origin |
| ScriptHammer dev | `http://localhost:3002` | OAuth còn phụ thuộc cấu hình Supabase/Google |
| Blog starter | Script mặc định 3000, hỗ trợ biến `PORT` | Chọn port sau khi kiểm tra thực tế |

Đề xuất bộ demo chính: **Online Boutique** cho mục 1 scalability và mục 3; **ScriptHammer** cho security audit open source; **Mini Shop** cho mục 2; **Micro Frontend** và **blog-starter-app** cho mục 4; **People** cho mục 5–6 với giới hạn Event Sourcing được nêu rõ. Việc chọn lại project phải ghi vào ma trận yêu cầu để không bỏ sót nội dung đề bài.

## 2. Những khoảng trống cần xử lý trước

1. Chưa có số liệu load test trước/sau scale trong phần đã kiểm tra. Locust source có sẵn không phải kết quả scalability.
2. Chưa có báo cáo audit bảo mật mới với vị trí code, bằng chứng và phân loại false positive. SSR là ví dụ phụ; chọn ScriptHammer/Online Boutique để đáp ứng yêu cầu audit open source.
3. Chưa xác nhận Kubernetes, Istio control/data plane, Prometheus và Grafana đang vận hành. Không dùng ảnh source/manifests để thay thế bằng chứng runtime.
4. C4 Mini Shop có sẵn nhưng cần kiểm tra đủ mối quan tâm 4+1, schema, security/concurrency. Bốn cấp C4 không đồng nghĩa bốn views.
5. README JAMstack nói chưa tải/chưa cài, trong khi source/dependency đã tồn tại. `.next/dev` không chứng minh build SSG production thành công.
6. People hiện ghi `people_commands` bằng UPDATE và ghi outbox cùng transaction. Có event log/retained stream và CQRS, nhưng command path chưa thể hiện phục hồi aggregate bằng fold event. Cần quyết định demo trung thực kiến trúc hiện tại hay bổ sung Event Sourcing đầy đủ.
7. Tên `people-kurrent` là tên Compose giữ volume, không có nghĩa KurrentDB đang làm event store. `docker-compose.kurrent.yml` của ScriptHammer ghi rõ app còn cần adapter để dùng KurrentDB.
8. `schema.sql` trong People là schema append-only cũ (`person_events`); schema đang dùng phải đọc `mq-schema.js` và `read-db.js`, đối chiếu migration `init-db`.

## 3. Mini Shop: component, cơ chế hoạt động và vị trí trong project

Đường dẫn dưới đây tương đối với lab-01/microservices-project-demo (`lab-01/microservices-project-demo/README.md`).

| Component kiến trúc | File/cấu hình | Hoạt động cần giải thích |
|---|---|---|
| Browser SPA | `frontend/src/` | Render React; giữ giỏ hàng/pending idempotency key phía client; gọi API qua cùng origin |
| Web/reverse proxy | `frontend/nginx.conf`, `frontend/Dockerfile` | Serve static build; proxy `/api` đến Gateway; publish duy nhất cổng web |
| API Gateway | `services/gateway/src/index.ts`, `http.ts` | Route tới Products/Orders; truyền request ID và idempotency key; timeout upstream 8 giây; giới hạn route public |
| Products service | `services/products/src/index.ts` | CRUD sản phẩm; `/internal/products/resolve` trả dữ liệu để Orders chốt snapshot; schema/seed bootstrap |
| Products persistence | `services/products/src/db.ts`, `compose.yaml` | Pool SQL; DB user riêng; database/volume/network `products-data` |
| Orders service | `services/orders/src/index.ts` | Validate order; replay request đã xử lý; resolve sản phẩm với timeout 3 giây; ghi order/items trong transaction |
| Domain logic | `services/orders/src/domain.ts` | `requestHash()` chuẩn hóa thứ tự items trước khi hash; `priceOrder()` tính giá từ sản phẩm đã resolve |
| Orders persistence | `services/orders/src/db.ts`, schema trong `index.ts` | `orders.idempotency_key` unique; `request_hash` phát hiện cùng key nhưng body khác; `order_items` giữ tên/giá snapshot |
| Deployment boundary | `compose.yaml`, backend `Dockerfile` | Sáu container; backend network chung và hai DB network internal; hai volume độc lập |
| Bằng chứng sẵn có | `docs/C4-MODELS.md`, `docs/DATAFLOWS.md`, `docs/VERIFICATION.md` | Tái sử dụng sau đối chiếu code; không trình bày kết quả cũ như vừa chạy |

Luồng cần truy vết: browser → Nginx → Gateway → Orders → Products resolve → Orders DB transaction → response. Luồng đọc đơn cũ không cần Products; thay đổi giá sản phẩm không sửa snapshot của đơn đã tạo. Snapshot này là dữ liệu đơn hàng, không phải bằng chứng Event Sourcing.

## 4. Online Boutique và hạ tầng

Đường dẫn tương đối với week-03/microservices-demo (`week-03/microservices-demo/README.md`). README gọi hệ thống là 11 microservices, có tính cả loadgenerator; Redis là dependency lưu giỏ hàng. Phải đối chiếu manifest đã deploy để xác định tập service thực tế, vì source còn có thành phần tùy chọn.

| Component | Source | Cơ chế cần trình bày |
|---|---|---|
| Frontend | `src/frontend/` | HTTP/HTML phía người dùng; session; gọi các backend bằng gRPC |
| Product catalog | `src/productcatalogservice/server.go`, `product_catalog.go`, `products.json` | List/get/search trên dữ liệu catalog JSON; không giả định có SQL DB riêng |
| Cart | `src/cartservice/src/services/CartService.cs`, `src/cartservice/src/cartstore/RedisCartStore.cs` | gRPC cart API; lưu giỏ hàng vào Redis ở cấu hình mặc định; có adapter store khác nhưng không mặc định đã bật |
| Checkout orchestrator | `src/checkoutservice/main.go` | `PlaceOrder()` phối hợp lấy cart, chuẩn bị items/quote, charge, ship, email, empty cart; chỉ rõ thứ tự/error path bằng code |
| Currency | `src/currencyservice/server.js` | Chuyển đổi tiền tệ; được gọi nhiều trong luồng hiển thị/checkout |
| Payment | `src/paymentservice/` | Charge mô phỏng; không mô tả như cổng thanh toán thật |
| Shipping | `src/shippingservice/` | Quote và shipping mô phỏng |
| Email | `src/emailservice/` | Xác nhận đơn mô phỏng; khác SMTP thật trong People |
| Recommendation / ads | `src/recommendationservice/`, `src/adservice/` | Dịch vụ phụ trợ; phân tích khi lỗi có làm hỏng chức năng chính không bằng thực nghiệm |
| API contract | `protos/demo.proto` | Service/RPC/message; generated client/server tương ứng ở từng ngôn ngữ |
| Load generator | `src/loadgenerator/locustfile.py` | `WebsiteUser`, weighted tasks, wait time 1–10 giây; browse/cart/checkout; cần kiểm tra business success ngoài HTTP status |
| Kubernetes workload | `release/kubernetes-manifests.yaml`, `kustomize/` | Deployment, Service, env endpoint, resource request/limit và probes theo manifest thật |
| Mesh ingress/routing | `release/istio-manifests.yaml`, `kustomize/components/service-mesh-istio/` | Có Gateway API Gateway/HTTPRoute, ServiceEntry và VirtualService; phân biệt API group và chọn cơ chế phù hợp bản cài |

Ánh xạ hạ tầng cần hoàn thành sau khi cài: image → container → Pod → Deployment/ReplicaSet → Service → gateway/route → browser. Control plane `istiod` cấu hình proxy; data plane thực thi traffic/security. Chốt dùng sidecar hay ambient rồi vẽ đúng mode thực tế; không trộn Envoy sidecar và ztunnel vào cùng luồng mà không giải thích.

Prometheus/Grafana hiện có manifest ở week-03/istio/samples/addons (`week-03/istio/samples/addons/README.md`). Khi demo phải ánh xạ scrape target → metric/label → PromQL → panel. Phân biệt metric từ ứng dụng, proxy và Kubernetes; có manifest Grafana không bảo đảm dashboard đã có datasource/dữ liệu.

## 5. Micro Frontend

Đường dẫn tương đối với micro-frontend/micro-frontend-demo (`micro-frontend/micro-frontend-demo/README.md`).

| Component | Source | Hoạt động cần giải thích |
|---|---|---|
| Main host / shell | `main/src/App.tsx`, `bootstrap.tsx`, `context/remotes.tsx` | Điều hướng, cấu hình URL remote, khởi tạo các dịch vụ dùng chung |
| Remote loader | `main/src/utils/index.ts` | `fetchRemote()` inject script; `loadComponent()` init Webpack share scope, init container, `get()` module rồi gọi factory |
| Remote rendering | `main/src/components/RemoteComponent/index.tsx`, `ErrorBoundary/` | React lazy/Suspense/loading/error boundary bao quanh remote |
| Module contracts | `main/webpack.config.js`, `products/webpack.config.js`, `cart/webpack.config.js` | Container name, `remoteEntry.js`, exposes, shared React/ReactDOM singleton |
| Products remote | `products/src/components/ProductsList/`, `ProductCard/`, `products.ts` | Hiển thị sản phẩm; publish thao tác add/remove và nhận cập nhật cart |
| Event bus | `main/src/services/pubsub.ts` | In-process PubSub qua `window.fsEvents`; topic, subscribe ID, unsubscribe và retained last message ở topic cấu hình |
| Cart state | `cart/src/store/index.ts` | Subscribe `addItem`/`removeItem`; Zustand cập nhật state; publish `cart`; persist localStorage |
| Checkout | `cart/src/features/checkout/index.tsx` | Tái sử dụng product component; giá từ dữ liệu import lúc build; không có backend thanh toán |
| Local deployment | `compose.yaml`, `docker/nginx.conf` | Một Nginx serve ba bundle tại `/`, `/products/`, `/cart/`; Docker local build chung |

Ranh giới cần nói rõ: độc lập module/build có thể hỗ trợ deploy riêng, nhưng deployment Compose hiện tại gộp ba app vào một web container. Event bus browser không có durability/offset/ACK như RabbitMQ. Remote code chạy trong cùng browser context; URL remote là trust boundary cần audit.

## 6. JAMstack và ScriptHammer

| Component | Source | Giải thích và bằng chứng cần có |
|---|---|---|
| Content | `week-03/jamstack/blog-starter-app/_posts/*.md` | Markdown + front matter làm dữ liệu build |
| Content access | `src/lib/api.ts` trong bản blog đã chọn | `getPostSlugs()`, `getPostBySlug()`, `getAllPosts()` đọc filesystem, parse và sort |
| Markdown pipeline | `src/lib/markdownToHtml.ts` | remark + remark-html tạo HTML; xem trust/sanitization của nội dung |
| Static routes | `src/app/posts/[slug]/page.tsx` | `generateStaticParams()` liệt kê slug; page render nội dung; cần production build log/HTML làm bằng chứng |
| Rendering boundary | `src/app/_components/post-body.tsx`, `layout.tsx` | HTML injection cho Markdown, assets/font/image và client interaction |
| Production hosting | `package.json` bản blog đã chọn | `next build` + `next start`; chưa thấy config static export, không tuyên bố đã deploy toàn bộ lên CDN |
| Static export bổ sung | `week-03/ScriptHammer/next.config.ts` | `output: 'export'`, trailingSlash, images unoptimized; cần artifact build mới chứng minh |
| OAuth/security đối chiếu | `week-03/ScriptHammer/src/lib/supabase/client.ts`, `src/app/auth/callback/page.tsx` | Browser → Supabase → Google → callback → session; audit token/redirect/RLS theo code thực |

Tên `api.ts` trong blog là thư viện đọc file nội bộ, không tự chứng minh có remote HTTP API/headless CMS. Slide phải thể hiện phần nào của JavaScript–APIs–Markup có thật; bổ sung API chỉ nếu kịch bản cần và ghi rõ là phần mở rộng.

## 7. People: CQRS, EDA và giới hạn Event Sourcing

Đường dẫn tương đối với week-03/new-app-auth-info (`week-03/new-app-auth-info/README.md`).

| Component | Source | Cơ chế/ánh xạ dữ liệu |
|---|---|---|
| UI / quan sát | `public/app.js`, `public/data-flow.*` | Form command; query danh sách/lịch sử; hiển thị source, projection lag, worker và email |
| API boundary | `server.js` | POST/PUT/DELETE command; GET `/api/people`, history, projection, MQ viewer; chờ projection tối đa khoảng 3 giây rồi trả `projected` |
| Domain validation | `domain.js` | Validate tên/email/ngày sinh/version; tính tuổi phía server |
| Command store | `store.js` | `createStore().commit()`: lock state, kiểm tra version, INSERT/UPDATE `people_commands`, INSERT `mq_outbox`, COMMIT cùng transaction |
| Outbox publisher | `publisher.js` | SQL advisory lock đảm bảo một publisher làm việc; lấy unpublished theo position, publish confirm rồi ghi `published_at`; crash gap có thể phát trùng |
| Broker topology | `mq.js` | Fanout exchange `people.events` → stream `people.events.retained` và classic queue `people.events.preview`; consumer nghiệp vụ đọc stream |
| Consumer runtime | `consumer.js` | Offset riêng trong SQL, `x-stream-offset`, prefetch 1, handler xong mới ACK, reconnect/retry; một message lỗi có thể chặn consumer đó |
| Read projection | `read-consumer.js`, `adapter.js` | `mapEvent()`, `applyEvent()`; inbox event ID, history, current state theo version, offset/checkpoint commit cùng SQL transaction |
| Query model | `read-db.js` | List/history/diagnostics từ MariaDB projection; không đọc MQ cho mỗi query |
| Email subscriber | `email-consumer.js` | SMTP side effect; `email_deliveries` theo event ID; retry; crash sau SMTP accept trước SQL commit vẫn có thể gửi trùng |
| Schema/migration | `mq-schema.js`, `read-db.js`, `init-db.js` | Command/outbox/current/history/inbox/offset/checkpoint/worker/email tables; hiện cùng MariaDB instance, tách model về logic |
| Deployment | `compose.yaml` | app, publisher, read-consumer, email-consumer, rabbitmq, read-db; init-db là job migration thoát thành công |

Các phân biệt bắt buộc trong phần vấn đáp:

- **CQRS:** write model và query model khác đường đi/trách nhiệm; không bắt buộc phải hai máy DB. Command validation dựa `people_commands`, không dựa projection có thể trễ.
- **EDA:** publisher và hai subscriber giao tiếp qua event; mỗi consumer có tiến độ riêng. Stream giữ event sau ACK; queue preview phục vụ quan sát, không phải nguồn consumer nghiệp vụ.
- **Event Sourcing:** cần event history đủ để dựng lại state và được xác định là nguồn sự thật. Code hiện tại lấy state SQL để quyết định command; có history/outbox không tự đủ kết luận hệ thống đã event-sourced đầy đủ.
- **Delivery:** xử lý lại có thể xảy ra; inbox giúp idempotent SQL effects, không biến SMTP thành exactly-once. Confirm không có nghĩa mọi consumer đã hoàn tất.
- **Ordering:** phân biệt `mq_outbox.position`, RabbitMQ broker offset và `person.version`; không dùng thay thế nhau khi giải thích checkpoint/conflict.
- **Replay:** đọc MQ trên trang quan sát không phải rebuild projection; replay thật cần projection/consumer identity mới và tuyệt đối tách side effect email.

## 8. Quy cách cho mỗi component đưa vào slide

Mỗi component cần một thẻ giải thích: trách nhiệm → đầu vào/đầu ra và contract → state sở hữu → thuật toán/luồng chính → dependency/giao thức → failure/retry/concurrency → file và symbol nguồn → container/service/DB tương ứng → bằng chứng demo → trade-off.

Mỗi sơ đồ phải kèm đoạn giải thích bằng chữ, legend và nhãn giao thức/hướng gọi. Đánh dấu rõ phần đang có, phần dự kiến bổ sung và external service. Dùng bảng mapping để người nghe đi được từ một hộp trong hình tới file code và runtime thực tế.

Cập nhật cấu trúc: AnonBlog đã được xóa theo yêu cầu. Repo tài liệu mới: midterm-software-architecture (`midterm-software-architecture/README.md`).

Các đường dẫn source trong tài liệu là tương đối với workspace đã kiểm tra, là nguồn gốc trước khi copy. Bản copy hiện nằm trong `topics/<topic>/projects/<project>/source/`.
