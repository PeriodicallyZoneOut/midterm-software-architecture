# Task list chuẩn bị vấn đáp giữa kỳ kiến trúc phần mềm

Đầu vào: yêu cầu 6 nhóm chủ đề do giảng viên cung cấp và [kết quả inspection + component mapping](INVENTORY.md). Ngày lập: 2026-11-01.

Các checkbox dưới đây là **việc chuẩn bị còn phải làm**, chưa được đánh dấu hoàn thành chỉ vì có README/source. Phạm vi lượt này là kiểm kê và lập task list; chưa thực hiện các thay đổi/deploy/load test/audit trong backlog.

## 0. Cách theo dõi và tiêu chí chung

P0 = quyết định/khôi phục nền tảng chặn demo; P1 = bắt buộc cho đề bài; P2 = tăng chiều sâu. Thứ tự: chốt scope → baseline runtime → kiến thức và mapping → thu bằng chứng → slide → diễn tập. Có thể làm nhánh slide lý thuyết song song với setup.

Mỗi task chỉ đóng khi có artifact, cách tái hiện và người trình bày giải thích được kết quả. Người phụ trách/ngày hoàn thành điền sau theo nhân sự thực tế. Ước lượng dưới đây là giờ công, chưa tính tải image lớn hay xử lý máy thiếu tài nguyên.

| Nhóm | Ước lượng ban đầu | Đầu ra |
|---|---:|---|
| A — Scope và runtime | 3–6h | Ma trận yêu cầu, inventory xác nhận, runbook khởi động |
| B — Quality Attributes | 8–14h | Slide, load report, security audit report |
| C — Representation | 5–8h | 4+1, schema, mapping, decision notes |
| D — Microservices/hạ tầng | 8–16h | Cluster/mesh/metrics demo và runbook |
| E — Micro Frontends/JAMstack | 5–9h | Hai demo, mapping, production build evidence |
| F/G — ES/CQRS/EDA | 8–14h | Xác định ES, replay tách biệt, sequence/failure evidence |
| H — Tổng hợp/diễn tập | 4–7h | Deck, speaker notes, video/ảnh dự phòng, checklist |

Ước lượng F/G có thể tăng nếu cần xây command path Event Sourcing mới. Không cần triển khai toàn bộ project để đáp ứng đề; chốt bộ demo có thể vận hành và giải thích sâu.

## A. Chốt hệ thống và xác nhận môi trường

- [ ] **A01 · P0 · Chốt ma trận đề bài → demo.** Scalability: Online Boutique/Locust; security: ScriptHammer/Codex audit; representation: Mini Shop; infrastructure: Online Boutique; MFE: fruit store; JAMstack: blog-starter-app; CQRS/EDA: People; ES: theo F01. Đầu ra `requirement-matrix.md`: mỗi yêu cầu có project, slide, kịch bản và evidence path; không để mục ES chỉ ghi “có RabbitMQ”.
- [ ] **A02 · P0 · Chụp baseline runtime.** Lưu ngày/giờ, Docker/Compose version, danh sách project/container, health, CPU/RAM/disk, tool versions và port; kiểm tra HTTP read-only các app. Phân biệt “có source”, “có build”, “đã deploy”, “đang healthy”, “đã kiểm chứng nghiệp vụ”. Không lưu env/secret/PII trong evidence.
- [ ] **A03 · P0 · Giải quyết xung đột tài nguyên.** People dùng MariaDB host port 3307; kiểm tra các dịch vụ khác trước khi khởi động. Mini Shop và ScriptHammer Kurrent web cùng mặc định 8080. Chọn port khác hoặc chạy theo lịch, kiểm tra URL/callback nếu đổi. Đầu ra bảng port + lịch demo và kiểm tra hai stack cần dùng đồng thời.
- [ ] **A04 · P0 · Chốt bản JAMstack.** So sánh `blog-starter` và `blog-starter-app`, lockfile, dependency và content; chọn bản chính, giữ bản còn lại làm tham khảo. Cập nhật tình trạng README sau khi xác minh; không xóa source/volume để “dọn”.
- [ ] **A05 · P0 · Runbook cho từng demo đã chọn.** Ghi đúng working directory, lệnh build/start/status/log/stop, URL, readiness, seed cần thiết, cách rollback, thứ tự khởi động. Sửa hướng dẫn Mini Shop đang dùng `cd lab-01` thành đúng thư mục chứa Compose. Xác nhận clean start không reset dữ liệu hiện có.
- [ ] **A06 · P1 · Xác nhận nguồn open source.** Lưu upstream URL, license, commit/tag hoặc snapshot hash, phần chỉnh sửa local của Online Boutique/ScriptHammer/MFE/blog. Nếu không có Git metadata, ghi cách tải và hash thay vì đoán commit. Đầu ra phần “system under test” trong report.
- [ ] **A07 · P1 · Tạo chỗ lưu artifact.** Đề xuất `midterm/{slides,architecture,mappings,demos,reports,evidence}/`; mỗi evidence có timestamp, project/version, command, expected/actual, giới hạn. Tách secret và dữ liệu hồ sơ/email thật khỏi tài liệu chia sẻ.

## B. Quality Attributes: kiến thức, scalability, security

### B1. Slide kiến thức

- [ ] **B01 · P1 · Viết 2 slide nền tảng QA.** Functional requirement so với quality attribute; scenario sáu phần: source, stimulus, environment, artifact, response, response measure. Cho hai scenario cụ thể của hệ thống chọn, có ngưỡng định lượng ghi rõ là mục tiêu đề xuất.
- [ ] **B02 · P1 · Viết 3–4 slide scalability/performance.** Latency percentile p50/p95/p99, throughput, error rate, saturation; concurrency/users khác RPS; vertical/horizontal scaling; stateless/stateful; bottleneck, connection pool, caching và backpressure. Liên hệ Little's Law với điều kiện đo ổn định; không suy luận tuyến tính vô hạn từ thêm replica.
- [ ] **B03 · P1 · Viết 3–4 slide security.** Authentication/authorization; confidentiality/integrity/availability; trust boundary; least privilege; input/output handling; secret/token lifecycle; dependency/container exposure. Mỗi ý gắn một vị trí code/cấu hình trong project.
- [ ] **B04 · P2 · Viết 1–2 slide QA khác và trade-off.** Availability/reliability, modifiability, observability, testability; phân biệt restart, redundancy và HA; ví dụ timeout tăng responsiveness nhưng có thể gây retry/duplicate; eventual consistency giảm coupling nhưng UI có thể đọc state cũ.

### B2. Demo scalability — phụ thuộc D02/D03 để dùng Online Boutique

- [ ] **B05 · P1 · Thiết kế workload có mục tiêu.** Dùng `src/loadgenerator/locustfile.py`; giải thích `WebsiteUser`, weighted tasks, think time và session/cart. Tách browsing với checkout; xác minh checkout thành công theo nội dung/contract, không chỉ HTTP 200. Chốt thời lượng, warm-up, users/spawn rate và resource budget trước chạy.
- [ ] **B06 · P1 · Tách tải nền.** Xác nhận loadgenerator mặc định trong manifest; tắt hoặc kiểm soát để tránh vừa chạy embedded generator vừa chạy máy phát tải ngoài. Đầu ra topology tải, resource limits và cách kiểm tra chính load generator chưa bão hòa.
- [ ] **B07 · P1 · Chạy baseline một cấu hình replica cố định.** Ví dụ các bậc 10/25/50/100 users, điều chỉnh theo máy; đo đủ cửa sổ steady state. Lưu CSV/HTML, p50/p95/p99 nếu công cụ xuất được, RPS, failures, latency theo endpoint, CPU/RAM, pod restarts và metric backend. Không hứa các bậc trên đều chịu được.
- [ ] **B08 · P1 · Scale rồi chạy lại cùng điều kiện.** Chọn service theo bottleneck đo được; ghi replica/resource trước/sau, giữ workload/dataset/tool version tương đương; lặp ít nhất 3 lượt cấu hình để nhìn biến thiên. Đo hiệu quả scale `throughput_after / throughput_before` tại cùng SLO latency/error và phân tích shared DB/Redis/network có giới hạn gì.
- [ ] **B09 · P1 · Báo cáo kết quả.** Bảng baseline/scaled, đồ thị users → p95/RPS/errors và biểu đồ tài nguyên. Mỗi kết luận có evidence, giả thuyết bottleneck và kiểm chứng. Nếu không tăng throughput phải giải thích được; tải chạy thành công chưa tự chứng minh scalability.
- [ ] **B10 · P1 · Kịch bản live 4–6 phút.** Mở app → workload → metrics → scale cấu hình đã thử → giải thích report đầy đủ đã lưu. Ghi rõ số liệu live khác run chuẩn ở điểm nào; có ảnh/video và raw report khi thời gian không đủ chờ toàn bộ test.

### B3. Demo security audit open source

- [ ] **B11 · P1 · Chốt scope audit ScriptHammer.** Đọc auth/OAuth callbacks, session/token storage, Supabase RLS/migrations, output rendering, public config và Docker/static hosting. Threat model có actors/assets/entry points/trust boundaries. Codex audit code phù hợp đề bài; scanner online không bắt buộc.
- [ ] **B12 · P1 · Audit theo luồng dữ liệu.** Truy từ input → validation → authorization → DB/query → output; xem redirect allowlist, client-vs-server enforcement, XSS, IDOR/RLS, public env chứa secret, privileged key và CORS/security headers. Mỗi phát hiện ghi file:line, điều kiện khai thác và tác động; không kết luận lỗ hổng chỉ từ tên API.
- [ ] **B13 · P1 · Bổ sung kiểm tra dependency/image nếu khả dụng.** Chọn công cụ theo lockfile/image thực tế, lưu version/database date và kết quả raw đã lọc secret. Advisory không tự là lỗi khai thác được; đánh giá reachability, cấu hình và false positive. Ghi phần scanner không bao phủ được business authorization.
- [ ] **B14 · P1 · Tái hiện các finding quan trọng bằng ca local tối thiểu.** Tách confirmed/suspected/false positive/accepted demo limitation. Không đăng nhập hộ, gửi thư hay tấn công dịch vụ bên ngoài. Đầu ra report: ID, severity + lý do, source, reproduction, evidence, remediation, retest/status.
- [ ] **B15 · P1 · Viết slide kết quả audit.** Trình bày finding đã xác nhận, control đang làm tốt và giới hạn audit; nếu không tìm được finding thì báo scope/coverage trung thực. Không biến “không có auth” trong demo local thành kết luận toàn bộ project production bị tấn công được.
- [ ] **B16 · P2 · Đối chiếu kiểm soát truy cập trong ScriptHammer.** Truy từ OAuth/session tới Supabase RLS; phân biệt kiểm tra UI với quyền ở backend. Chứng minh các role không đọc được dữ liệu ngoài phạm vi bằng ca kiểm tra local hoặc môi trường test riêng.

## C. Architecture Representation — Mini Shop

- [ ] **C01 · P1 · Viết 2 slide về view/model/notation.** View là mối quan tâm của stakeholder; UML model là cách biểu diễn; package/component/deployment/artifact không tương ứng máy móc với 4 views. C4 là mức zoom, không thay thế mọi runtime/security/schema concern.
- [ ] **C02 · P1 · Lập stakeholder/concern matrix.** Customer, admin, developer, operator, quản lý; concern correctness, scale, deploy độc lập, data ownership, failure và cost. Chọn Boxes and Arrows + 4+1 Views, tận dụng C4 có sẵn như lớp bổ sung; mọi sơ đồ có diễn giải chữ.
- [ ] **C03 · P1 · Logical view.** Browser, gateway, Products, Orders và DB; trách nhiệm/contract/domain ownership; schema entity relationships là phần bổ sung. Đối chiếu `docs/C4-MODELS.md` với code và sửa chỗ không đúng thực tế.
- [ ] **C04 · P1 · Development view.** Workspace/frontend/service packages, Docker build target, dependency direction, ownership; phân biệt module trong source với process deploy. Đầu ra sơ đồ module + bảng folder/package → component.
- [ ] **C05 · P1 · Process view.** Sequence checkout bình thường, replay cùng idempotency key và Products timeout; thể hiện sync HTTP, timeout 8s/3s, transaction boundaries, pool/locks. Đầu ra ít nhất 3 sequence có response/error path và mô tả bằng chữ.
- [ ] **C06 · P1 · Physical/deployment view.** Browser/host, 6 containers, networks, published/internal ports và volumes; ghi mọi container hiện cùng máy. Mở Compose chỉ ra từng node/edge; không mô tả internal network là cơ chế auth đầy đủ.
- [ ] **C07 · P1 · +1 scenarios.** Chọn duyệt sản phẩm, tạo đơn, đổi giá xem lại đơn, mất Products, retry request; mỗi scenario link đủ các view liên quan. Đầu ra bảng scenario → component → code → evidence.
- [ ] **C08 · P1 · Database schema.** Vẽ products DB và orders/order_items DB từ DDL thật; PK/FK/unique, snapshot fields, idempotency key/hash và indexes. Không vẽ FK xuyên service; giải thích transaction cục bộ và vì sao đơn cũ giữ nguyên giá.
- [ ] **C09 · P1 · Security và concurrency view.** Trust boundary browser/public API/internal resolve/DB; auth hiện thiếu; hai request cùng key, unique constraint, rollback, stale state. Trình bày control có thật và đề xuất bổ sung bằng ký hiệu riêng.
- [ ] **C10 · P1 · Hoàn thiện component cards.** Dùng bảng mapping trong inspection; mỗi component có responsibility, input/output, state, dependency/protocol, failure, source symbol và deployment. Với Gateway/Orders phải đi được từ hộp trên sơ đồ đến handler đang chạy.
- [ ] **C11 · P2 · Ghi quyết định kiến trúc.** Vì sao database-per-service, HTTP sync, snapshot, local transaction, idempotency; alternative, QA được cải thiện và cost. Không gọi hệ thống là Saga/Event Sourcing khi code chưa có.

## D. Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana

- [ ] **D01 · P1 · Viết 3–4 slide microservices + Docker.** Service theo capability, ownership, contract, independent deployment; so sánh monolith/modular monolith; container/image/volume/network, multi-stage build. Dùng Mini Shop đơn giản để giải thích rồi chuyển Online Boutique cho cluster.
- [ ] **D02 · P0 · Chuẩn bị cluster tái hiện được.** Chốt cluster local hoặc cluster đã có theo tài nguyên; cài tool còn thiếu; lưu version, node capacity, context, namespace và kế hoạch dừng. Kiểm tra CRD/API compatibility trước apply manifest; không mặc định đã có cluster vì source Kubernetes tồn tại.
- [ ] **D03 · P1 · Deploy Online Boutique bản đã chọn.** Dùng release/Kustomize phù hợp local cluster; xác nhận Deployment/Service/probes/resources/endpoints, Redis và frontend truy cập được. Lưu manifests đã áp dụng, pod readiness và một giao dịch mẫu; liệt kê services tùy chọn thực sự bật.
- [ ] **D04 · P1 · Mapping toàn bộ service nghiệp vụ.** Với mỗi dòng bảng Online Boutique trong inspection: API proto → server handler → client gọi → state/dependency → Deployment/Service/port/env. Deep dive frontend/cart/checkout/product catalog; payment/shipping/email ghi rõ mock.
- [ ] **D05 · P1 · Viết 2–3 slide orchestration.** Pod/Deployment/ReplicaSet/Service/DNS, desired state/reconciliation, readiness/liveness/startup, requests/limits, rolling update, scaling; nếu demo HPA cần metrics source và requests hợp lệ. Không đồng nhất restart với HA dữ liệu.
- [ ] **D06 · P1 · Demo lifecycle Kubernetes.** Scale một deployment, quan sát endpoints/pod count; xóa một pod để controller tạo lại; rolling update một thay đổi có thể rollback. Lưu trước/sau và tác động client. Khôi phục trạng thái baseline sau demo.
- [ ] **D07 · P0 · Chốt và cài Istio mode/version.** Chọn sidecar hoặc ambient phù hợp tài nguyên; xác nhận `istiod` và data plane workload; ghi namespace labels/injection hoặc enrollment. `istioctl` tồn tại không đủ tiêu chí hoàn thành.
- [ ] **D08 · P1 · Demo ingress/routing.** Đối chiếu Gateway API Gateway/HTTPRoute với Istio VirtualService/ServiceEntry trong source; chọn một luồng vào rõ ràng. Nếu muốn weighted routing cần hai version có dấu nhận biết; lưu config và thống kê request trước/sau thay vì chỉ chụp YAML.
- [ ] **D09 · P1 · Demo mesh security và traffic control.** Xác nhận mTLS mode/chứng cứ proxy hoặc telemetry; thử policy allow/deny có kết quả client; giải thích timeout/retry và nguy cơ nhân request. Tách các tính năng mới bổ sung khỏi manifest upstream mặc định.
- [ ] **D10 · P1 · Deploy Prometheus/Grafana.** Dùng addons làm điểm xuất phát, kiểm tra version phù hợp; cấu hình scrape, datasource và dashboard. Đầu ra target UP + query có dữ liệu + panel khớp. Nếu chỉ có mesh metric thì không tuyên bố đã có business metric/app CPU.
- [ ] **D11 · P1 · Viết 2–3 slide observability.** Metrics/logs/traces khác nhau; counter/gauge/histogram; request rate, error ratio, latency histogram, label cardinality; dùng metric thực có và kiểm tra label trước viết PromQL. Một panel phải truy về được query và target nguồn.
- [ ] **D12 · P1 · Demo end-to-end.** Browser → gateway/proxy → frontend → checkout/cart/catalog → Redis/dependency, đối chiếu log/metric; dùng request correlation/tracing nếu đã có, không giả định bật sẵn. Nối các bước với B07–B09 để giải thích bottleneck và scale.

## E. Micro-Frontends và JAMstack

### E1. Micro-Frontends

- [ ] **E01 · P1 · Viết 2–3 slide MFE.** Domain/team boundary, build/deploy/runtime composition; Module Federation host/remote/exposes/shared; so sánh component library và monolithic SPA. Trade-off bundle/version/shared dependency, UX/CSS consistency, failure isolation và trust remote code.
- [ ] **E02 · P1 · Khôi phục demo cổng 9001.** Build/start đúng Compose, kiểm tra host/checkout và hai `remoteEntry.js`, asset paths/deep links. Lưu DevTools Network minh họa remote tải ở runtime; ghi local Compose hiện gộp build và deploy.
- [ ] **E03 · P1 · Vẽ sequence load remote và mapping.** Main → `RemoteComponent` → `loadComponent` → script `remoteEntry` → share scope/container init → module factory → React render. Mỗi bước chỉ đúng file/symbol trong inspection và webpack expose tương ứng.
- [ ] **E04 · P1 · Vẽ sequence add-to-cart.** ProductCard → `window.fsEvents` topic `addItem` → Cart Zustand → publish `cart` → ProductCard/count + localStorage. Giải thích owner state, payload contract, subscribe/unsubscribe, refresh và giới hạn pubsub trong một browser.
- [ ] **E05 · P1 · Demo độc lập và failure.** Thay URL remote sang một build riêng hoặc đổi remote UI có kiểm soát; ghi host có cần rebuild không. Mô phỏng remote unavailable, quan sát actual ErrorBoundary/fallback và phần UI còn hoạt động. Không tuyên bố production deploy độc lập chỉ từ cấu trúc folder.

### E2. JAMstack

- [ ] **E06 · P1 · Viết 2–3 slide JAMstack.** JavaScript–APIs–Markup, build time/request time, prerender/CDN, headless content, cache invalidation và rebuild; so sánh CSR/SSR/SSG/ISR, đánh dấu mode thực sự có trong blog. Không coi mọi Next.js app là JAMstack.
- [ ] **E07 · P0 · Build production bản blog đã chốt ở A04.** Dùng lockfile, ghi version Node/Next và build log; xử lý font/network theo cấu hình thật. Xác minh output route và HTML/prerender metadata, start production rồi kiểm tra HTTP; `.next/dev` không đạt tiêu chí.
- [ ] **E08 · P1 · Mapping content pipeline.** `_posts/*.md` → filesystem/gray-matter (`api.ts`) → `generateStaticParams` → remark → page/post-body → generated HTML/assets → hosting → browser. Giải thích `api.ts` là local library, chưa có backend HTTP API riêng.
- [ ] **E09 · P1 · Demo vòng đời nội dung.** Chọn bài mẫu → xem source HTML → sửa Markdown → chứng minh production cũ chưa đổi → rebuild/restart → bài mới xuất hiện. Lưu timestamp/artifact; so sánh với nguyên lý SSR tạo HTML theo từng request; ghi rõ đây là đối chiếu lý thuyết nếu chưa có demo SSR khác.
- [ ] **E10 · P1 · Mô tả hosting đúng triển khai.** Nếu giữ `next start`, ghi Node server đang serve prerendered pages và runtime features. Nếu chọn static export, bổ sung config/image strategy trên bản phù hợp rồi chứng minh file export serve bằng static server. CDN thực tế chưa có thì vẽ là phương án dự kiến.
- [ ] **E11 · P2 · Đối chiếu ScriptHammer.** Chỉ `output: 'export'` và luồng client gọi Supabase, tách static delivery khỏi backend API/Auth. Chỉ dùng làm demo phụ khi build/export và cấu hình API đã xác nhận.

## F. Event Sourcing và CQRS — People

- [ ] **F01 · P0 · Quyết định mức đáp ứng Event Sourcing.** Đối chiếu `store.js`: command state + outbox hiện là cơ chế chính. Viết ADR chọn (a) nâng cấp event log thành nguồn sự thật với append/version check và fold/rebuild, hoặc (b) thêm demo event-sourced đã học có tích hợp thật. Không dùng standalone KurrentDB của ScriptHammer khi chưa có adapter; không gọi đọc history là replay đầy đủ.
- [ ] **F02 · P1 · Viết 3–4 slide Event Sourcing.** Event bất biến, aggregate/stream, command → invariant → event append, expected version, fold/replay, snapshot để tối ưu, schema evolution/upcaster và dữ liệu nhạy cảm. Phân biệt event log, audit log, message broker và nguồn sự thật; nêu rõ snapshot People/order khác nhau về ý nghĩa.
- [ ] **F03 · P1 · Viết 2–3 slide CQRS.** Command/query responsibilities; model logic khác model vật lý; projection/materialized view; eventual consistency/read-your-writes; CQRS không bắt buộc ES và ES không bắt buộc microservices. Ánh xạ write model/read model trong cùng MariaDB của People.
- [ ] **F04 · P1 · Vẽ command/query sequences hiện tại.** Command → validate/version lock → state + outbox SQL COMMIT → publish confirmed → read projection → query. Thể hiện response `projected:false` khi quá thời gian chờ và UI xử lý pending; không vẽ transaction bao trùm SQL + broker.
- [ ] **F05 · P1 · Vẽ schema đang chạy.** Dựa `mq-schema.js` + `read-db.js`: people_commands, mq_outbox, people_current/history, consumer_inbox, offsets/checkpoints, worker_status, email_deliveries; ownership, PK/unique và transaction scope. Gắn nhãn `schema.sql`/person_events là legacy nếu không được migration hiện tại dùng.
- [ ] **F06 · P1 · Demo CRUD/version conflict.** Dữ liệu giả: tạo v1, sửa v2, sửa bằng v1 bị 409, xóa v3; đối chiếu event/current/history và age tính ở server. Lưu request/response đã ẩn thông tin thật. Mọi demo tạo command cần cấu hình email sandbox trước để không gửi thư thật ngoài ý muốn.
- [ ] **F07 · P1 · Xây replay an toàn trên môi trường tách biệt.** DB/projection tables và consumer identity mới, offset bắt đầu phù hợp; email disabled/test transport. Chỉ rõ nguồn event, reducer, ordering và dedupe. Không reset inbox/offset hoặc truncate DB demo đang dùng để minh họa.
- [ ] **F08 · P1 · Chứng minh rebuild.** Dùng history sự kiện đã biết → dựng lại projection rỗng → so sánh current/history/versions bằng query/hash có kiểm soát; duplicate event không nhân bản effect. Nếu chọn ES đầy đủ, chứng minh command state cũng có thể phục hồi và invariant/expected version vẫn đúng sau rebuild.
- [ ] **F09 · P1 · Kiểm thử fail/recover.** Dừng read consumer trong sandbox, commit command, quan sát lag/pending, bật lại để catch up. Dừng broker, quan sát outbox tồn và publish sau recovery; ghi rõ API có thể đợi projection rồi timeout. Đảm bảo khôi phục mọi service.
- [ ] **F10 · P1 · Kiểm tra tính đúng của bộ test hiện tại.** Test domain/database có dấu vết schema/logic đời trước; đối chiếu fixture/migration với code MQ hiện tại rồi chọn regression test có ý nghĩa. Không lấy test pass của store cũ để chứng minh retained stream/replay mới.

## G. Event-Driven Architecture — cùng People, góc nhìn khác CQRS

- [ ] **G01 · P1 · Viết 3 slide EDA.** Producer/broker/consumer, event vs command, pub/sub vs work queue, orchestration/choreography, temporal coupling; at-most/at-least/exactly-once trong phạm vi nào; ordering, retry, poison messages, DLQ và backpressure. Đánh dấu DLQ là đề xuất nếu code hiện chưa có.
- [ ] **G02 · P1 · Sơ đồ topology và contract.** Exchange fanout → retained stream + preview queue; hai consumer cùng stream nhưng offset riêng. Liệt kê PersonCreated/Updated/Deleted với eventId/eventType/position/data/version/recordedAt/notifyEmail; phân biệt domain version với broker offset và outbox position.
- [ ] **G03 · P1 · Deep dive publisher/inbox.** Giải thích transaction state+outbox, advisory lock một publisher, confirm-before-mark, duplicate window; consumer transaction projection+inbox+offset rồi ACK. Chỉ từng đoạn `store.js`, `publisher.js`, `consumer.js`, `adapter.js` và failure window.
- [ ] **G04 · P1 · Demo hai consumer độc lập.** Trên stack sandbox dừng email consumer/test transport, tạo event giả, Read DB vẫn cập nhật; bật lại để catch up. Một message poison/SMTP lỗi có thể chặn các message sau của consumer đó vì prefetch 1/retry tại chỗ; đo lag riêng, không chỉ nhìn container healthy.
- [ ] **G05 · P1 · Demo retained stream.** So payload broker với SQL projection qua eventId; xác nhận message còn sau ACK. Trang MQ viewer tạo reader tạm không đổi business offsets; preview queue là bản sao và cách xem không xóa. Không gọi thao tác “Đọc lại MQ” là rebuild DB.
- [ ] **G06 · P1 · Giải thích giới hạn side effect email.** SMTP accepted khác inbox delivery; crash sau SMTP accept trước commit có thể duplicate. Chứng minh bằng timeline/failure analysis hoặc test transport, không phát hàng loạt thư thật. Ghi Message-ID chỉ hỗ trợ trace, không cam kết nhà cung cấp dedupe.
- [ ] **G07 · P2 · Đề xuất vận hành dài hạn.** Retention/storage growth, schema versioning, PII access, dead letter/parking stream, retry policy, monitoring backlog/age, checkpoint backup/recovery. Nêu hiện trạng và phương án mở rộng ở cột khác nhau; không trình bày như đã cài.

## H. Tổ chức slide, câu hỏi và diễn tập

Dàn deck đề xuất 40–55 slide chính, điều chỉnh theo thời lượng giảng viên; phần code/manifests/raw report dài đưa appendix. Mỗi nhóm lý thuyết cần ví dụ lấy ngay từ demo và speaker notes, tránh chỉ chép định nghĩa.

| Phần deck | Nội dung bắt buộc | Artifact gắn kèm |
|---|---|---|
| Mở đầu · 2 slide | Mục tiêu, ma trận 6 yêu cầu, hệ thống đã chọn và hiện trạng | A01/A02 |
| Quality Attributes · 9–12 slide | Scenario, tactics, workload, số liệu trước/sau scale, security method/findings/limits | B01–B15 |
| Architecture Representation · 7–9 slide | View vs notation, 4+1, schema, security/concurrency, component mapping | C01–C10 |
| Microservices + infrastructure · 8–11 slide | Boundary/contract, Docker/K8s, mesh, monitoring, luồng checkout/failure | D01–D12 |
| MFE + JAMstack · 6–8 slide | Host/remotes/state, static pipeline, SSR comparison, build/deploy evidence | E01–E10 |
| ES + CQRS + EDA · 8–11 slide | Nguồn sự thật, replay, read model, outbox/inbox, offsets, failure windows | F01–G06 |
| Appendix | Lệnh demo, manifests, full schema, component cards, raw reports, glossary | Toàn bộ |

- [ ] **H01 · P1 · Viết speaker notes cho từng sơ đồ.** 60–90 giây: vấn đề → luồng → component/state/protocol → file → runtime evidence → trade-off. Kiểm tra mọi mũi tên có người gọi/người nhận và sync/async rõ ràng.
- [ ] **H02 · P1 · Bộ câu hỏi vấn đáp.** Tối thiểu 5 câu mỗi nhóm: “tăng users khác scale thế nào?”, “vì sao thêm replica chưa nhanh?”, “4 views khác 4 UML diagrams?”, “mesh khác gateway?”, “remote chết thì gì xảy ra?”, “SSG đổi bài lúc nào?”, “CQRS không ES có được không?”, “ACK xóa stream không?”, “email exactly-once được không?”. Mỗi đáp án có bằng chứng code/demo.
- [ ] **H03 · P1 · Runbook trình bày có timestamp.** Mỗi demo ghi prerequisites, lệnh, URL, thao tác, expected output, ý nghĩa, recovery và evidence fallback. Chốt thời lượng tổng với người học; không bắt live load test dài hoặc cài cluster ngay trong buổi vấn đáp.
- [ ] **H04 · P1 · Thu ảnh/video dự phòng.** Startup healthy, checkout, view-source SSG, remoteEntry network, scale/mesh/dashboard, replay comparison, audit finding đã ẩn dữ liệu. Ghi cấu hình/ngày chạy và giữ raw evidence, không chỉ screenshot đẹp.
- [ ] **H05 · P1 · Diễn tập từ trạng thái trước buổi thi.** Mở lại máy/stack theo runbook, kiểm tra cổng, secrets đã cấu hình, tài nguyên, datasource, offline font/image/cache. Không reset DB hiện có; xác nhận email sandbox và restore sau fault demo.
- [ ] **H06 · P1 · Review chéo lời nói với thực tế.** Tìm các khẳng định quá mức: HA, exactly-once, event-sourced, deployed CDN, independent deploy, auth an toàn, test pass. Mỗi khẳng định phải có evidence hoặc đổi thành giới hạn/đề xuất.
- [ ] **H07 · P1 · Chốt bộ bàn giao.** Slide export PDF + bản gốc, component mapping, sơ đồ có chú giải chữ, source/runbook, load report/raw data, security report, replay/failure evidence và câu hỏi. Chạy rà link/file và mở thử toàn bộ trước khi đóng checklist.

## Điều kiện sẵn sàng vấn đáp

- [ ] Mỗi mục trong đề có kiến thức, sơ đồ giải thích chữ, demo có thể lặp lại và ánh xạ tới source/runtime.
- [ ] Scalability có workload kiểm soát + kết quả trước/sau scale + phân tích bottleneck; security có audit scope + bằng chứng + giới hạn.
- [ ] Representation bao phủ 4+1 và schema; Microservices có Docker/Kubernetes/Istio/Prometheus/Grafana thực hoạt động hoặc công cụ tương đương được giải thích rõ.
- [ ] MFE có runtime composition/state flow; JAMstack có build production/prerender evidence và mô tả hosting đúng thực tế.
- [ ] Event Sourcing có nguồn sự thật và replay đã chứng minh; CQRS có write/read path; EDA có producer/broker/subscribers, delivery semantics và failure behavior.
- [ ] Người trình bày mở được file chứa từng component quan trọng, đọc được luồng xử lý và giải thích được một tình huống lỗi mà không dựa hoàn toàn vào slide.

## Phân công và lựa chọn hệ thống cập nhật

Áp dụng [TEAM-ASSIGNMENT.md](TEAM-ASSIGNMENT.md): chủ đề 2 ưu tiên Online Boutique đã có nguồn open source thay cho Mini Shop làm demo chính; các task C vẫn áp dụng về 4+1/mapping nhưng phải thay domain, data model và sequences theo source Boutique. Mini Shop là ví dụ phụ. Mỗi người tự deploy và thu evidence riêng, kể cả project trùng nhau.
