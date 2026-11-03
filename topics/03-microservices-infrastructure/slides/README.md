# BỘ SLIDE BÁO CÁO CHUYÊN SÂU — TƯỜNG (CHỦ ĐỀ 03)

Thư mục này chứa đầy đủ **7 bộ slide độc lập** tương ứng với 7 chủ đề cốt lõi của đồ án Kiến trúc Phần mềm: **Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana, và Ứng dụng Thực nghiệm Bookinfo**.

Mỗi bộ slide được thiết kế chuẩn mực:
- **Quy chuẩn**: Định dạng Markdown tương thích **Marp CLI / Marp for VS Code**.
- **Thời lượng**: **10 phút** thuyết trình độc lập (bao gồm lý thuyết, kiến trúc, phân tích code và live demo).
- **Quy mô**: Đúng **10 trang slide** cô đọng, chuyên sâu, bám sát mã nguồn dự án thực tế.
- **Kịch bản nói (Speaker Notes)**: Kèm sẵn kịch bản chi tiết từng phút ở cuối mỗi file.

---

## Danh Mục 7 Bộ Slide Độc Lập

| STT | File Slide | Chủ Đề Trình Bày | Trọng Tâm Kiến Trúc & Mã Nguồn Đối Chiếu | Thời Lượng |
|:---:|---|---|---|:---:|
| **01** | [`01-microservices.md`](./01-microservices.md) | **Microservices Architecture** | Phân rã Monolith, Bounded Context, Polyglot (`productpage.py`, `LibertyRestEndpoint.java`), Trade-offs | 10 phút |
| **02** | [`02-docker.md`](./02-docker.md) | **Containerization với Docker** | Multi-stage build (`reviews/Dockerfile`), giảm kích thước image, non-root user, layers caching | 10 phút |
| **03** | [`03-kubernetes.md`](./03-kubernetes.md) | **Điều phối Hạ tầng Kubernetes** | Pod 2/2 ready, Deployments, ClusterIP Services, Self-healing, `platform/kube/bookinfo.yaml` | 10 phút |
| **04** | [`04-istio.md`](./04-istio.md) | **Lưới Dịch vụ Istio Service Mesh** | Control Plane vs Data Plane, iptables intercept, Gateway, VirtualService canary user `jason`, mTLS | 10 phút |
| **05** | [`05-prometheus.md`](./05-prometheus.md) | **Giám sát Số liệu với Prometheus** | Pull-based scrape `:15090`, Data model labels, 4 Metric types, PromQL thực chiến (RPS, P95, Error rate) | 10 phút |
| **06** | [`06-grafana.md`](./06-grafana.md) | **Trực quan hóa SRE với Grafana** | Tích hợp DataSource, Istio Mesh & Service Dashboards, tương quan CPU/RAM với RPS, dynamic variables | 10 phút |
| **07** | [`07-bookinfo.md`](./07-bookinfo.md) | **Ứng dụng Thực nghiệm Bookinfo** | Topo 4 microservices, `getForwardHeaders()`, 3 phiên bản reviews, quy trình demo 4 bước, Monolith vs Microservices | 10 phút |

---

## Các File Tài Liệu Tổng Hợp Khác

- [`generate/`](./generate/README.md): **Thư mục chứa nội dung tối ưu để copy-paste trực tiếp lên các công cụ AI (Gamma.app, Tome, SlidesGPT)** tạo slide tự động cho cả 7 chủ đề!
- [`slides.md`](./slides.md): Bản slide tổng hợp gộp chung (tiếng Việt).
- [`slides-en.md`](./slides-en.md): Bản slide tổng hợp gộp chung dịch hoàn toàn sang tiếng Anh.
- [`speaker-notes.md`](./speaker-notes.md): Kịch bản thuyết trình chi tiết.
- [`outline.md`](./outline.md): Đề cương cấu trúc chuyên đề.
- `assets/`: Thư mục lưu trữ hình ảnh và sơ đồ minh họa.
- `exports/`: Thư mục xuất file PDF / PPTX / HTML.

---

## Hướng Dẫn Sử Dụng & Xuất Slide (Marp)

### 1. Xem trước trực tiếp trên VS Code
1. Cài extension **Marp for VS Code** (`marp-team.marp-vscode`).
2. Mở bất kỳ file slide nào (ví dụ `04-istio.md`) và nhấn biểu tượng **Open Preview to the Side** (`Ctrl + K, V`).

### 2. Xuất ra định dạng PowerPoint (.pptx) hoặc PDF
Nếu máy đã cài Marp CLI:
```bash
# Xuất file PDF
npx @marp-team/marp-cli 04-istio.md --pdf -o exports/04-istio.pdf

# Xuất file PowerPoint
npx @marp-team/marp-cli 04-istio.md --pptx -o exports/04-istio.pptx

# Xuất file HTML trình chiếu
npx @marp-team/marp-cli 04-istio.md --html -o exports/04-istio.html
```

### 3. Nhập vào AI Slide Generator (Gamma.app, SlidesGPT, Tome)
Mỗi file `.md` đã được tối ưu hóa cấu trúc Heading (`# SLIDE X`), Markdown Bullet points và Code block chuẩn. Bạn có thể copy toàn bộ nội dung file và dán thẳng vào tính năng **"Text / Markdown to Presentation"** trên các nền tảng AI để tạo slide thuyết trình tự động chỉ trong 30 giây.
