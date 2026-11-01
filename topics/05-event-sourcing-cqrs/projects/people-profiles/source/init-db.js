import { createReadPool } from './read-db.js';
import { migrate } from './mq-schema.js';
const pool = createReadPool();
try { await migrate(pool); console.log('MQ schema ready; existing people and history preserved.'); }
finally { await pool.end(); }
