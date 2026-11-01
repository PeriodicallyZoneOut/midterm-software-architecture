import { openMQ, PREVIEW, STREAM, readRetained, publishConfirmed } from './mq.js';

// Copy existing retained messages to the UI-only mirror, never to the exchange.
// This does not rerun either business consumer or send another email.
const mq = await openMQ();
try {
  const events = (await readRetained()).sort((a,b) => a.brokerOffset - b.brokerOffset);
  for (const { brokerOffset, ...event } of events) {
    await publishConfirmed(mq.channel, event, PREVIEW, {
      'original-stream': STREAM, 'original-offset': brokerOffset
    });
  }
  console.log(JSON.stringify({ previewQueue: PREVIEW, copied: events.length, originalStreamPreserved: true }));
} finally { await mq.connection.close(); }
