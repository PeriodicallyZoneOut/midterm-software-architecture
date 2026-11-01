import http from 'node:http';
import { setTimeout as delay } from 'node:timers/promises';
import { openMQ, STREAM } from './mq.js';
import { heartbeat } from './mq-schema.js';

// Two named business consumers independently read the retained stream.
export async function runConsumer({ name, port, pool, handler, details = () => ({}) }) {
  let running = true;
  let active;
  let tag;
  let task = Promise.resolve();
  let state = 'connecting';
  let errorText = null;
  let connected = false;
  const server = http.createServer((req, res) => {
    res.writeHead(connected ? 200 : 503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ consumer: name, connected, state, ...details() }));
  });
  server.listen(port, '0.0.0.0');
  const beat = () => heartbeat(pool, name, state, errorText, details()).catch(() => {});
  const timer = setInterval(beat, 5000);
  for (const signal of ['SIGINT','SIGTERM']) process.on(signal, async () => {
    running = false;
    if (tag) await active?.channel.cancel(tag).catch(() => {});
    // Stop waiting on retries; an unacknowledged message is retained for restart.
    await active?.connection.close().catch(() => {});
  });
  try {
    while (running) {
      try {
        active = await openMQ();
        connected = true;
        await active.channel.prefetch(1);
        const [[offset]] = await pool.execute('SELECT broker_offset FROM mq_consumer_offsets WHERE consumer_name=?', [name]);
        state = 'listening';
        errorText = null;
        await beat();
        const consumer = await active.channel.consume(STREAM, message => {
          if (!message) return;
          task = (async () => {
            let complete = false;
            while (running && connected && !complete) {
              try {
                state = 'processing';
                const event = JSON.parse(message.content.toString());
                const brokerOffset = Number(message.properties.headers['x-stream-offset']);
                if (!Number.isSafeInteger(brokerOffset)) throw new Error('Missing stream offset');
                await handler(event, brokerOffset);
                active.channel.ack(message);
                complete = true;
                state = 'listening'; errorText = null;
                console.log(JSON.stringify({ consumer: name, eventId: event.eventId, brokerOffset, status: 'processed' }));
              } catch (error) {
                state = error.code === 'SMTP_NOT_CONFIGURED' ? 'awaiting-smtp' : 'retry';
                errorText = error.code || error.message;
                await beat();
                for (let n = 0; n < 30 && running && connected; n++) await delay(1000);
              }
            }
            await beat();
          })();
          task.catch(() => {});
        }, { noAck: false, consumerTag: 'people-' + name,
          arguments: { 'x-stream-offset': Number(offset.broker_offset) + 1 } });
        tag = consumer.consumerTag;
        await active.closed;
        connected = false;
        await task;
      } catch (error) {
        connected = false; state = 'retry'; errorText = error.code || error.message;
        await beat();
        await active?.connection.close().catch(() => {});
      }
      if (running) await delay(2000);
    }
  } finally { clearInterval(timer); server.close(); await task; await pool.end(); }
}
