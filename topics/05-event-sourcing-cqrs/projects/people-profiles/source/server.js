import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { AppError, validatePerson, validateVersion } from './domain.js';
import { createStore } from './store.js';
import { createReadPool, createReadStore } from './read-db.js';
import { EXCHANGE, STREAM, EMAIL_TO, brokerStatus, readRetained } from './mq.js';
import { setTimeout as delay } from 'node:timers/promises';

const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 3003);
const origin = `http://${host}:${port}`;
const allowedOrigins = new Set([
  process.env.APP_ORIGIN || `http://localhost:${port}`,
  `http://localhost:${port}`,
  `http://127.0.0.1:${port}`
]);
const readPool = createReadPool();
const store = createStore(readPool);
const readStore = createReadStore(readPool, EXCHANGE);
const assets = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/style.css', ['style.css', 'text/css; charset=utf-8']],
  ['/data-flow', ['data-flow.html', 'text/html; charset=utf-8']],
  ['/data-flow.js', ['data-flow.js', 'text/javascript; charset=utf-8']]
]);

// A confirmed source write stays successful even when the read side is delayed.
async function receipt(result) {
  let readPosition = null;
  try {
    const until = Date.now() + 3000;
    do {
      readPosition = await readStore.position();
      const [[seen]] = await readPool.execute("SELECT event_id FROM consumer_inbox WHERE consumer_name='read-db' AND event_id=?", [result.eventId]);
      if (seen) return { ...result, projected: true, readPosition };
      await delay(50);
    } while (Date.now() < until);
  } catch { /* The committed event will be projected when the worker recovers. */ }
  return { ...result, projected: false, readPosition };
}

async function readJson(req) {
  if (!req.headers['content-type']?.startsWith('application/json')) {
    throw new AppError(415, 'Cần gửi dữ liệu JSON.');
  }
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 8192) throw new AppError(413, 'Dữ liệu quá lớn.');
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { throw new AppError(400, 'JSON không hợp lệ.'); }
}

function json(res, status, value) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(value));
}

const server = http.createServer(async (req, res) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
  try {
    const path = new URL(req.url, origin).pathname;
    if (req.method === 'GET' && path === '/health') {
      await store.checkConnection();
      await readStore.checkConnection();
      return json(res, 200, { status: 'ok', broker: 'rabbitmq-stream', readDatabase: 'mariadb' });
    }
    if (req.method === 'GET' && assets.has(path)) {
      const [name, type] = assets.get(path);
      const body = await readFile(new URL(`./public/${name}`, import.meta.url));
      res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-cache' });
      return res.end(body);
    }
    if (req.method === 'GET' && path === '/api/people') return json(res, 200, await readStore.list());
    if (req.method === 'GET' && path === '/api/mq/events') {
      return json(res, 200, { stream: STREAM, nonDestructive: true, events: await readRetained() });
    }
    if (req.method === 'GET' && path === '/api/projection') {
      const target = await readStore.diagnostics();
      let queues = [];
      let brokerError = null;
      try { queues = await brokerStatus(); } catch (error) { brokerError = error.message; }
      const [workers] = await readPool.query(`SELECT w.*,o.broker_offset,o.last_event_id,o.processed_at
        FROM worker_status w LEFT JOIN mq_consumer_offsets o ON o.consumer_name=w.name`);
      const [[outbox]] = await readPool.query(`SELECT COUNT(*) AS total,COALESCE(MAX(position),0) AS head,
        COALESCE(SUM(published_at IS NULL),0) AS unpublished FROM mq_outbox`);
      const [[pending]] = await readPool.query(`SELECT
        (SELECT COUNT(*) FROM mq_outbox o WHERE NOT EXISTS(SELECT 1 FROM consumer_inbox i WHERE i.consumer_name='read-db' AND i.event_id=o.event_id)) AS readPending,
        (SELECT COUNT(*) FROM mq_outbox o WHERE o.notify_email=1 AND NOT EXISTS(SELECT 1 FROM email_deliveries e WHERE e.event_id=o.event_id AND e.status='sent')) AS emailPending`);
      const [deliveries] = await readPool.query('SELECT * FROM email_deliveries ORDER BY source_position DESC LIMIT 20');
      return json(res, 200, {
        source: { database: 'RabbitMQ Stream', stream: STREAM, exchange: EXCHANGE,
          retained: true, head: Number(outbox.head), error: brokerError, queues,
          outbox: { total: Number(outbox.total), unpublished: Number(outbox.unpublished) } },
        adapter: { name: 'mq-to-mariadb', lag: Number(pending.readPending),
          status: brokerError ? 'source-unavailable' : Number(pending.readPending) ? 'catching-up' : 'caught-up' },
        consumers: workers.map(worker => ({ ...worker,
          broker_offset: worker.broker_offset === null ? null : Number(worker.broker_offset),
          alive: Number.isFinite(Date.parse(worker.heartbeat_at)) && Date.now()-Date.parse(worker.heartbeat_at)<15000,
          detail: typeof worker.detail_json==='string' ? JSON.parse(worker.detail_json) : worker.detail_json })),
        email: { recipient: EMAIL_TO, pending: Number(pending.emailPending), deliveries }, target
      });
    }
    const match = path.match(/^\/api\/people\/([0-9a-f-]{36})(\/history)?$/i);
    if (req.method === 'GET' && match?.[2]) return json(res, 200, await readStore.history(match[1]));
    if (['POST', 'PUT', 'DELETE'].includes(req.method)) {
      // Only local UI requests. This demo has no authentication.
      if (req.headers.origin && !allowedOrigins.has(req.headers.origin)) {
        throw new AppError(403, 'Origin không được phép.');
      }
      const input = await readJson(req);
      if (req.method === 'POST' && path === '/api/people') {
        return json(res, 201, await receipt(await store.create(validatePerson(input))));
      }
      if (match && !match[2]) {
        const version = validateVersion(input?.version);
        if (req.method === 'PUT') {
          return json(res, 200, await receipt(await store.append(match[1], version, 'updated', validatePerson(input))));
        }
        if (req.method === 'DELETE') {
          return json(res, 200, await receipt(await store.append(match[1], version, 'deleted')));
        }
      }
    }
    throw new AppError(404, 'Không tìm thấy đường dẫn.');
  } catch (error) {
    if (!error.status) console.error('Request failed:', error.code || error.message);
    if (!res.headersSent && !res.destroyed) {
      json(res, error.status || 503, { error: error.status ? error.message : 'Không kết nối được database hoặc database đang bận.' });
    }
  }
});

try {
  await store.checkConnection();
  await readStore.checkConnection();
  server.listen(port, host, () => console.log(`Local: ${process.env.APP_ORIGIN || origin} (RabbitMQ + 2 consumers)`));
  server.on('error', error => { console.error('Không mở được server:', error.code); process.exitCode = 1; });
} catch (error) {
  console.error(`Không kết nối được database (${error.code || error.message}). Kiểm tra read-db và init-db.`);
  process.exitCode = 1;
}

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => server.close(() => readPool.end()));
}
