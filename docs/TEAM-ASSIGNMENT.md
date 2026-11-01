# Phân công: Nhật Anh, Thế Anh, Tường, Toàn, Tú

Mỗi bạn tự phụ trách kiến thức, slide, thuyết trình, deploy, demo và vấn đáp của phần được giao. Không có một người thuyết trình thay toàn nhóm. Mỗi bạn phải chạy thành công demo của mình trên môi trường riêng, kể cả khi dùng cùng project với bạn khác.

## 1. Phân công chính

| Thành viên | Nội dung đề bài | Project chính | Kết quả phải chứng minh |
|---|---|---|---|
| **Nhật Anh** | 1. Quality Attributes: Scalability và Security | Online Boutique + ScriptHammer | Load test có số liệu trước/sau scale; audit bảo mật có scope, code evidence, phân tích và giới hạn |
| **Thế Anh** | 2. Architecture Representation | Online Boutique (open source đã có) | Tái dựng kiến trúc từ source/runtime; 4+1 Views + schema/data model, component mapping và diễn giải bằng chữ |
| **Tường** | 3. Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana | Online Boutique + Istio/addons | Cluster, services, mesh, metrics và dashboard thực hoạt động; demo traffic/failure/recovery |
| **Toàn** | 4. Micro-Frontends và JAMstack | Fruit Store + Next.js Blog Starter | Runtime composition và state flow; production prerender/build/rebuild và hosting đúng thực tế |
| **Tú** | 5. Event Sourcing/CQRS và 6. EDA | People Profiles | Command/query, event source/replay, outbox/inbox, hai consumer độc lập và failure semantics |

Tú nhận hai mục vì cùng project và có phần kiến thức/triển khai giao nhau. Không yêu cầu xây hai ứng dụng nghiệp vụ khác nhau, nhưng phải có hai kịch bản và có thể deploy hai stack riêng để kiểm chứng từng chủ đề. Độ khó Event Sourcing còn chưa rõ nên cần kiểm tra sớm, không coi đây là phần nhẹ.

## 2. Chủ đề 2 có cần thêm project không?

**Không cần phát triển hoặc tải thêm một hệ thống mới.** Đề cho phép Claude Code auto mode, Arm Metis **hoặc một open source tự chọn**. Online Boutique đã có source và nguồn GitHub được ghi trong [REPOSITORIES.md](../REPOSITORIES.md), nên có thể dùng cho cả mục 1, 2 và 3 với ba deployment và mục tiêu giải thích khác nhau.

Thế Anh cần có bản source làm việc và deployment riêng phục vụ mục 2. Có thể copy source Online Boutique vào `topics/02-architecture-representation/projects/online-boutique/source/` khi triển khai; **slot này chưa được tạo/copy ở lần phân công này**. Source có sẵn ở `topics/03-microservices-infrastructure/projects/online-boutique/source/` hoặc slot Quality Attributes. Các thư mục runtime Docker cũ không phải điều kiện để deploy; phải dựng runtime mới trên môi trường của Thế Anh.

Slot Mini Shop đã có ở chủ đề 2 được giữ làm tài liệu/ví dụ phụ. Chưa xác nhận nguồn open source của Mini Shop nên không chọn làm hệ thống chính cho yêu cầu “một open source tự chọn”. Không cần làm cả Mini Shop và Online Boutique thành hai bài trình bày đầy đủ.

Không nên thêm Claude Code auto mode/Arm Metis chỉ để tăng số project: tăng thời gian tìm bằng chứng và học domain mà không trực tiếp cải thiện độ đầy đủ của 4+1, schema hay mapping. Chỉ đổi hệ thống nếu người phụ trách không thể deploy/hiểu đủ Online Boutique hoặc giảng viên có yêu cầu bổ sung.

## 3. Cân bằng workload

Ngân sách ban đầu: **24 giờ công/người**, không phải cam kết mọi môi trường sẽ hoàn thành trong đúng thời gian này. Sau 4–6 giờ đầu phải rà lại phần setup và replay; nếu chênh lệch, giảm mở rộng ngoài yêu cầu hoặc điều chuyển việc tài liệu/review. Không bỏ tiêu chí bắt buộc để giữ số giờ đẹp.

| Người | Kiến thức + slide | Đọc code + mapping/sơ đồ | Deploy + demo | Report/evidence | Ôn + diễn tập | Tổng |
|---|---:|---:|---:|---:|---:|---:|
| Nhật Anh | 4h | 4h | 10h | 2h | 4h | 24h |
| Thế Anh | 4h | 8h | 6h | 2h | 4h | 24h |
| Tường | 4h | 4h | 10h | 2h | 4h | 24h |
| Toàn | 4h | 4h | 10h | 2h | 4h | 24h |
| Tú | 4h | 5h | 9h | 2h | 4h | 24h |

Thế Anh có workload sơ đồ/mapping lớn hơn, dù không cần mesh/monitoring. Tường không phải làm thêm load report/audit như Nhật Anh. Nhật Anh không bắt buộc triển khai Istio/Grafana nếu không cần cho thí nghiệm. Tú dùng chung phần giải thích domain/schema giữa hai chủ đề, tránh nhân đôi slide. Không cân bằng bằng số slide hoặc số project đơn thuần.

## 4. Nhật Anh — Quality Attributes

**Đã có:** source Online Boutique, manifests Kubernetes và Locust; source ScriptHammer/Next.js/Supabase và cấu hình Docker. Có source/dependency copy không chứng minh bản deploy mới đã chạy.

**Phải tự deploy:** một Online Boutique của Nhật Anh với load generator kiểm soát được; một bản ScriptHammer local/test đủ để tái hiện các luồng audit đã chọn. Chỉ cấu hình Supabase/OAuth riêng nếu kết luận audit/demo phụ thuộc chúng; không nhận kết quả đăng nhập của người khác làm bằng chứng.

- [ ] Viết QA scenarios có response measure; giải thích latency percentiles, throughput, errors, saturation, scalability và trade-off.
- [ ] Tự dựng Boutique, kiểm tra catalog/cart/checkout; ghi replica/resources/version và xác nhận generator không tự thành bottleneck.
- [ ] Chạy Locust ở baseline và sau scale trong điều kiện so sánh được; kiểm soát loadgenerator nền; lưu raw report và phân tích cả kết quả không cải thiện.
- [ ] Audit ScriptHammer bằng Codex/Claude Code/Copilot hoặc công cụ phù hợp; ghi scope, file:line, điều kiện, impact, false positive và remediation. Không bắt buộc tìm ra một số lượng lỗ hổng cố định.
- [ ] Tái hiện findings trên bản local/test; phân biệt nhận định từ code với điều đã kiểm chứng runtime.
- [ ] Demo thành công khi tự mở app, phát tải, giải thích bảng/biểu đồ và chứng minh ít nhất luồng kiểm tra bảo mật đã chọn; không chỉ hiển thị prompt audit.

**Phân biệt với Tường:** Nhật Anh chịu trách nhiệm thí nghiệm và kết luận QA, không trình bày đầy đủ mesh/orchestration.

## 5. Thế Anh — Architecture Representation

**Đã có:** Online Boutique có source đa ngôn ngữ, protobuf, manifests và sơ đồ upstream. Mini Shop có bộ C4 nhưng chỉ là tài liệu tham khảo cho cách tổ chức hình và lời giải thích.

**Phải tự deploy:** Online Boutique riêng, không cần Istio/Prometheus/Grafana cho mục 2. Tạo slot source riêng theo mục 2 trước khi chỉnh sửa. Không dùng URL, cluster hay screenshot của Nhật Anh/Tường thay cho deployment của mình.

- [ ] Ghi nguồn/version, stakeholder và concern; chọn Boxes and Arrows + 4+1, bổ sung C4 khi cần. Không coi bốn UML diagrams là bốn views.
- [ ] Logical view: frontend, catalog, cart, checkout, currency, payment/shipping/email và dependency; nêu mock vs thật.
- [ ] Development view: source packages/ngôn ngữ, proto/generated clients, Docker build và dependency direction.
- [ ] Process view: sequence browse/add-cart/checkout; lấy thứ tự gọi và error behavior từ handler thực tế.
- [ ] Deployment view: image → container → Pod/Deployment → Service → frontend ingress/access; ports, configuration, Redis và tài nguyên theo cấu hình của Thế Anh.
- [ ] +1 scenarios: tối thiểu browse, cart, checkout và một failure/recovery; dùng chúng nối các views.
- [ ] Data schema/model: mô tả Redis cart keys/value/serialization từ code, catalog JSON và protobuf contracts. Nêu rõ baseline không có relational DB schema; không vẽ SQL tables không tồn tại. Nếu dùng store khác phải deploy và mô tả schema thật của cấu hình đó. Kiểm tra với giảng viên nếu yêu cầu “Database Schema” được hiểu bắt buộc là ERD quan hệ.
- [ ] Bổ sung security/concurrency concern khi liên quan; với mỗi hộp có trách nhiệm, contract, state, source symbol và runtime mapping, kèm diễn giải chữ.
- [ ] Demo thành công khi tự chạy được browse/cart/checkout, chỉ đúng handler/proto/manifest từ sơ đồ và đối chiếu một tình huống lỗi. Sơ đồ upstream đơn lẻ chưa đủ.

## 6. Tường — Microservices và hạ tầng

**Đã có:** source Boutique, Dockerfiles/manifests; source Istio với addons Prometheus/Grafana. Trạng thái kiểm kê trước đây chưa xác nhận cluster/mesh/monitoring vận hành.

**Phải tự deploy:** cluster riêng của Tường, Boutique, Istio theo mode/version đã chốt, Prometheus và Grafana. Tường tự cấu hình datasource/dashboard và thu metric của deployment này.

- [ ] Giải thích service boundary, ownership, gRPC contract và luồng checkout; map từng dịch vụ được bật vào source và Deployment/Service.
- [ ] Deploy Boutique, xác nhận readiness và giao dịch mẫu; ghi requests/limits và dependency Redis.
- [ ] Demo Pod self-heal hoặc rolling update, scale một workload và xác nhận client còn hoạt động; biết rollback/recovery.
- [ ] Deploy mesh, phân biệt control/data plane và sidecar/ambient; kiểm chứng routing và một control như mTLS/policy/timeout bằng hành vi thực tế.
- [ ] Deploy Prometheus/Grafana, có scrape target UP, datasource hoạt động, query/panel có dữ liệu khớp traffic do mình tạo.
- [ ] Demo thành công khi đi được browser → services/proxies → dependency và giải thích metric nguồn nào, cảnh nào là lỗi/recovery. Không chỉ đưa manifest hoặc dashboard rỗng.

**Phân biệt với Nhật Anh:** không phải lặp lại full load benchmark/security audit; traffic chỉ cần đủ chứng minh routing/metrics và hành vi hệ thống.

## 7. Toàn — Micro-Frontends và JAMstack

**Đã có:** Fruit Store Main/Products/Cart, Module Federation, PubSub, Zustand, Compose/Nginx; Blog Starter source/lockfile. Production prerender của bản blog chưa được xác nhận khi kiểm kê.

**Phải tự deploy:** Fruit Store và Blog Starter của Toàn. Có thể chọn Docker/static hosting phù hợp; phải có production build thật của blog, không dùng dev server để kết luận SSG.

- [ ] Slide MFE: host/remote/exposes/shared, runtime load, state ownership, failure và remote trust. Chỉ `remoteEntry.js`, loader, event bus và Cart store trong code.
- [ ] Deploy Fruit Store; demo add/remove cart, refresh/persistence và Network tải remote; giải thích luồng ProductCard → event → Zustand → cart update.
- [ ] Demo remote unavailable/fallback; nếu trình bày deploy độc lập thì tự có build/URL remote thay được mà host không rebuild. Ghi rõ Compose mặc định gộp ba bundles vào một Nginx.
- [ ] Slide JAMstack: build/request time, CSR/SSR/SSG/ISR, content pipeline và cache/rebuild; phân biệt tính năng thực có với kiến thức mở rộng.
- [ ] Build production blog; chỉ `_posts` → parser → `generateStaticParams` → HTML/assets. Chứng minh cập nhật Markdown cần rebuild để đổi bản production.
- [ ] Nêu hosting thật: `next start` hay static export; không gọi local Node server là CDN. Nếu chọn export phải cấu hình và serve export thành công.
- [ ] Demo thành công khi chạy độc lập được cả hai project và chỉ rõ component/code của từng kiểu kiến trúc; không chỉ mở giao diện.

## 8. Tú — Event Sourcing/CQRS và EDA

**Đã có:** hai bản copy People ở chủ đề 5/6, API, SQL command state/outbox, RabbitMQ stream, publisher, hai consumers, Read DB và data-flow UI. Stack gốc từng được xác nhận healthy; bản copy mới vẫn phải tự deploy.

**Phải tự deploy:** People riêng; nên tách `tu-es-cqrs` và `tu-eda` với DB/volumes/ports riêng để từng kịch bản chạy độc lập. Dùng email sandbox/test transport. Không dùng dữ liệu/volume hay consumer offsets của stack gốc.

- [ ] Chốt sớm Event Sourcing: code hiện tại ghi state + outbox; xác định nguồn sự thật và bổ sung/chọn đường append/version/fold phù hợp để đáp ứng ES. Retained stream/history chưa tự chứng minh event-sourced đầy đủ.
- [ ] Slide ES/CQRS: aggregate/events, expected version, replay/snapshot, write/read models, projection, eventual consistency và giới hạn hệ thống thật.
- [ ] Demo tạo/sửa/xóa và stale-version conflict; chỉ command state, event, current/history và query path.
- [ ] Replay vào DB/projection mới từ event source; so sánh state/version, kiểm tra duplicate không nhân effect. Nếu tuyên bố command side event-sourced, phải phục hồi được state đó từ events.
- [ ] Slide EDA: producer/broker/consumer, event vs command, pubsub/queue, delivery/ordering/retry. Map source: API/store → publisher → exchange/stream → read consumer/email consumer.
- [ ] Demo consumer dừng rồi catch up, hai consumer độc lập, retained event sau ACK và outbox phát lại sau broker phục hồi trong sandbox.
- [ ] Giải thích SQL transaction/inbox/offset, confirm-vs-processed, SMTP accept-vs-delivered và duplicate window; không cam kết exactly-once end-to-end.
- [ ] Demo thành công khi replay có kết quả so sánh và EDA có evidence failure/recovery, không chỉ xem lại payload trên UI.

## 9. Quy tắc deployment độc lập

1. Mỗi người chuẩn bị môi trường từ source và runbook của mình. Có thể dùng cùng máy vật lý theo lịch nhưng phải có namespace/cluster hoặc Compose project, volumes và cấu hình riêng.
2. Ví dụ tên: `nhatanh-qa`, `theanh-architecture`, `tuong-microservices`, `toan-mfe`, `toan-jamstack`, `tu-es-cqrs`, `tu-eda`. Với Kubernetes nên dùng context/cluster riêng khi cần thử policy/mesh; namespace riêng chưa cách ly mọi tài nguyên cluster-wide.
3. Chọn port theo bảng cá nhân; không copy cứng port nếu trùng. Compose People có `name: people-kurrent`, image tag dùng chung và nhiều port RabbitMQ cố định: phải chỉnh/override các giá trị liên quan, app origin và URL trước khi chạy hai stack trên cùng máy. Chỉ thêm `-p` không giải quyết xung đột host port/image/config.
4. Không dùng `.local-demo/runtime` đã copy như runtime có thể mang sang máy khác. Dựng cluster/daemon mới; không cần khởi chạy daemon Docker riêng chỉ vì có thư mục này.
5. Bỏ dependency vào đường dẫn tuyệt đối cũ; cài/build theo phiên bản/lockfile phù hợp máy hiện tại. `node_modules` copy không bảo đảm portable.
6. Mỗi người lưu log build/start/health và giao dịch thành công của **chính môi trường mình**. Có thể trao đổi kiến thức/script chung nhưng không dùng deployment/evidence của nhau để thay tiêu chí cá nhân.
7. Không bắt buộc cả năm bộ demo chạy đồng thời trên một máy. Lịch trình phải đủ RAM/disk/CPU và khôi phục sau fault demo.

## 10. Bộ bàn giao và nghiệm thu cá nhân

Mỗi bạn nộp trong thư mục chủ đề mình phụ trách:

- [ ] Slide bản gốc + PDF; speaker notes; sơ đồ có mô tả thành phần bằng chữ.
- [ ] `project-knowledge-application-implementation/`: concepts, component mapping, implementation sequences và verification/trade-off.
- [ ] `demo/runbook.md`: working directory, dependencies, env mẫu, ports, build/start/readiness, thao tác, expected result, recovery và stop giữ dữ liệu.
- [ ] `evidence/`: source/version, ngày chạy, config, raw report/log và ảnh/video dự phòng đã lọc dữ liệu nhạy cảm.
- [ ] 8–10 câu hỏi/chủ đề với đáp án có code/evidence; Tú chuẩn bị riêng câu hỏi ES/CQRS và EDA.
- [ ] Tự thuyết trình và demo từ đầu theo runbook; giải thích được một luồng chính, một lỗi và một trade-off.

Checkpoint 1: sau 4–6h, mọi người phải có baseline deploy hoặc blocker cụ thể và phương án xử lý; Tú chốt ES ngay ở checkpoint này. Checkpoint 2: demo có evidence và slide nháp. Checkpoint 3: diễn tập chéo, người khác đặt câu hỏi và kiểm tra mapping. Deadline cụ thể điền theo lịch thi, không suy đoán từ ngày tạo tài liệu.

Thành công cá nhân không phụ thuộc việc một thành viên khác có mặt để bật cluster, chạy lệnh, mở tài khoản hoặc giải thích phần code thay mình.
