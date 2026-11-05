# Quality Attributes

## Kiến thức và slide

- QA scenario: source, stimulus, environment, artifact, response, response measure.
- Scalability: workload, throughput, p50/p95/p99, errors, saturation, bottleneck và hiệu quả thêm replica.
- Security: trust boundaries, authentication/authorization, input/output, secret management và audit findings.
- Trade-off: availability, reliability, modifiability, observability và testability.

[Slide outline](slides/outline.md) · [Speaker notes](slides/speaker-notes.md)

## Tài liệu Hướng dẫn Setup & Kịch bản Live Demo (10 Phút)

- 📄 [**Hướng dẫn Setup & Triển khai toàn bộ (HUONG-DAN-SETUP.md)**](HUONG-DAN-SETUP.md)
- 🚀 [**Script tự động hóa 1-Click (setup-and-run.ps1)**](setup-and-run.ps1)
- ⚡ [**Cheat Sheet Lệnh Demo 1 Trang (CHEAT-SHEET-CMD.md)**](CHEAT-SHEET-CMD.md)
- 🎙️ [**Kịch bản Live Demo Vấn đáp chuẩn (KICH-BAN-DEMO-CHAT-LUONG.md)**](KICH-BAN-DEMO-CHAT-LUONG.md)

## Projects

- [Online Boutique](projects/online-boutique/README.md): Locust workload; baseline/scaled runs; bottleneck và SLO.
- [ScriptHammer](projects/scripthammer/README.md): Threat model, OAuth/session/RLS; audit findings có source evidence.
- [Mini Shop](projects/mini-shop/README.md): Timeout, idempotency, data ownership và resilience.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code.
- Demo có runbook, expected/actual result và evidence; giới hạn được ghi rõ.
