# Architecture Representation

## Kiến thức và slide

- Stakeholders, concerns; view khác notation/UML diagram và C4 zoom level.
- 4+1: logical, development, process, physical/deployment và scenarios.
- Database schema; security/concurrency view theo QA.
- Mapping: một hộp sơ đồ → source symbol → runtime component → evidence.

[Slide outline (Online Boutique)](projects/online-boutique/slides/outline.md) · [Speaker notes (Online Boutique)](projects/online-boutique/slides/speaker-notes.md) · [Slide exports (Online Boutique)](projects/online-boutique/slides/exports/)
[Slide outline (Mini Shop)](slides/outline.md) · [Speaker notes (Mini Shop)](slides/speaker-notes.md)

## Projects

- [Online Boutique](projects/online-boutique/README.md) (**Project chính theo `docs/TEAM-ASSIGNMENT.md`**): Tái dựng 4+1 Views, C4 Model (L1–L4), Redis/JSON/Protobuf Data Model, Security/Concurrency View và Component Mapping từ source đa ngôn ngữ + Kubernetes runtime.
- [Mini Shop](projects/mini-shop/README.md) (Tài liệu/ví dụ phụ): Tái dựng 4+1, Relational SQL Schema, C4 bổ sung; checkout/retry/failure sequence.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code.
- Demo có runbook, expected/actual result và evidence; giới hạn được ghi rõ.
