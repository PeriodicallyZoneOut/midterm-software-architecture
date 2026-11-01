# Event-Driven Architecture

## Kiến thức và slide

- Producer/broker/consumer; event vs command; pubsub vs work queue.
- Exchange/retained stream/preview queue; contracts và offsets của từng consumer.
- Outbox, confirm, inbox, ACK, delivery semantics, ordering và retries.
- Hai consumer độc lập; lag/poison message; SMTP duplicate window và recovery.

[Slide outline](slides/outline.md) · [Speaker notes](slides/speaker-notes.md)

## Projects

- [People Profiles](projects/people-profiles/README.md): Publisher → RabbitMQ → Read DB/email; consumer offsets, inbox, retry và side effect semantics.

## Hoàn thành khi

- Có kiến thức, sơ đồ giải thích bằng chữ và mapping tới code.
- Demo có runbook, expected/actual result và evidence; giới hạn được ghi rõ.
