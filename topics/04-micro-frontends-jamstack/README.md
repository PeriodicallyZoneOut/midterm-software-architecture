# Micro-Frontends và JAMstack

**Phần Toàn:** [Bắt đầu ôn tập](EXAM-GUIDE.md) · [Ma trận yêu cầu](requirement-matrix.md) · [20 câu vấn đáp](oral-questions.md) · [Hai bộ slide](slides/README.md).

Demo chính là `micro-frontend-demo` và `ScriptHammer` ở workspace theo chỉ dẫn Toàn. Không chạy lại app trong lượt tạo tài liệu; source và kết quả QA slide được phân biệt với evidence runtime của phiên Toàn đã chạy.

## Kiến thức và slide

- MFE host/remotes, Module Federation, shared dependencies và deploy boundaries.
- State ownership, PubSub, localStorage, failure isolation và remote trust.
- JAMstack: build time/request time, JavaScript/APIs/Markup; CSR/SSR/SSG/ISR.
- Markdown → JSON → static export của ScriptHammer; production evidence, rebuild/cache và hosting thực tế.

[Slide outline](slides/outline.md) · [Speaker notes](slides/speaker-notes.md)

## Projects

- [Micro Frontend Fruit Store](projects/micro-frontend-demo/README.md): Host/Products/Cart; remote loading và event → Zustand → UI.
- [ScriptHammer](projects/scripthammer/README.md): Markdown → generate:blog → JSON → generateStaticParams/markdownProcessor → HTML/assets export; browser gọi Supabase/Edge APIs.

[Blog Starter](projects/blog-starter/README.md) được giữ làm lịch sử, không nằm trong bài demo của Toàn.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code.
- Demo có runbook, expected/actual result và evidence; giới hạn được ghi rõ.
