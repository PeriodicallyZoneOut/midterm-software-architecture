# Event Sourcing và CQRS

## Kiến thức và slide

- Event Sourcing: nguồn sự thật, immutable events, aggregate, expected version, fold/replay và snapshots.
- CQRS: command/query models, projection, eventual consistency và read-your-writes.
- State + outbox hiện tại khác command path event-sourced đầy đủ; nêu giới hạn.
- Replay vào projection mới; version conflict; dedupe và schema evolution.

[Slide outline](slides/outline.md) · [Speaker notes](slides/speaker-notes.md)

## Projects

- [People Profiles](projects/people-profiles/README.md): Command/read paths, SQL models, retained events; quyết định mức đáp ứng ES và chứng minh replay.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code.
- Demo có runbook, expected/actual result và evidence; giới hạn được ghi rõ.
