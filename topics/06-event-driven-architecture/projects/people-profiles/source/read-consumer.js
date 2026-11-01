import { createReadPool } from './read-db.js';
import { applyEvent } from './adapter.js';
import { runConsumer } from './consumer.js';
const pool = createReadPool();
await runConsumer({ name: 'read-db', port: 3004, pool,
  handler: (event, offset) => applyEvent(pool, event, offset) });
