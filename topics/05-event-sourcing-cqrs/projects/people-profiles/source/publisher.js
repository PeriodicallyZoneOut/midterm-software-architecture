import http from 'node:http';
import { setTimeout as delay } from 'node:timers/promises';
import { createReadPool } from './read-db.js';
import { openMQ, EXCHANGE, publishConfirmed } from './mq.js';
import { heartbeat } from './mq-schema.js';

const pool = createReadPool();
let running = true;
let lastSuccess = 0;
let active;
const server = http.createServer((req, res) => {
  res.writeHead(Date.now() - lastSuccess < 15000 ? 200 : 503);
  res.end('publisher');
});
server.listen(3006, '0.0.0.0');
for (const signal of ['SIGINT','SIGTERM']) process.on(signal, () => { running = false; active?.connection.close().catch(() => {}); });

try {
  while (running) {
    try {
      active = await openMQ();
      while (running) {
        const connection = await pool.getConnection();
        let acquired = false;
        try {
          const [[lock]] = await connection.query("SELECT GET_LOCK('people_outbox_publisher', 0) AS acquired");
          acquired = Number(lock.acquired) === 1;
          if (!acquired) { await delay(200); continue; }
          const [[row]] = await connection.query('SELECT * FROM mq_outbox WHERE published_at IS NULL ORDER BY position LIMIT 1');
          if (row) {
            const event = { eventId: row.event_id, eventType: row.event_type,
              position: Number(row.position), stream: EXCHANGE, notifyEmail: Boolean(row.notify_email),
              data: typeof row.payload_json === 'string' ? JSON.parse(row.payload_json) : row.payload_json };
            await publishConfirmed(active.channel, event);
            await connection.execute('UPDATE mq_outbox SET published_at=?,last_error=NULL WHERE position=?', [new Date().toISOString(),row.position]);
            console.log(JSON.stringify({ publisher: 'confirmed', eventId: event.eventId, position: event.position }));
          }
          lastSuccess = Date.now();
          await heartbeat(pool, 'publisher', row ? 'publishing' : 'idle');
          if (!row) await delay(500);
        } finally {
          if (acquired) await connection.query("DO RELEASE_LOCK('people_outbox_publisher')").catch(() => {});
          connection.release();
        }
      }
    } catch (error) {
      await heartbeat(pool, 'publisher', 'retry', error.code || error.message).catch(() => {});
      await active?.connection.close().catch(() => {});
      if (running) await delay(2000);
    }
  }
} finally { server.close(); await pool.end(); }
