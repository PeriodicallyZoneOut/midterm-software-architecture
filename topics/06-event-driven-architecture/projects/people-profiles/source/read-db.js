import mysql from 'mysql2/promise';
import { readFileSync } from 'node:fs';
import { AppError, ageAt } from './domain.js';

export function createReadPool() {
  return mysql.createPool({
    host: process.env.READ_DB_HOST || 'read-db',
    port: Number(process.env.READ_DB_PORT || 3306),
    database: process.env.READ_DB_NAME || 'people_read',
    user: process.env.READ_DB_USER || 'people_projector',
    password: process.env.READ_DB_PASSWORD_FILE
      ? readFileSync(process.env.READ_DB_PASSWORD_FILE, 'utf8').trim()
      : process.env.READ_DB_PASSWORD,
    connectionLimit: 5, dateStrings: true, timezone: 'Z',
    charset: 'utf8mb4', supportBigNumbers: true, bigNumberStrings: true
  });
}

export async function ensureReadSchema(pool, stream) {
  await pool.query(`CREATE TABLE IF NOT EXISTS people_current (
    person_id CHAR(36) PRIMARY KEY, version BIGINT NOT NULL,
    full_name VARCHAR(150) NOT NULL, dob DATE NOT NULL,
    deleted BOOLEAN NOT NULL, recorded_at VARCHAR(30) NOT NULL,
    source_position BIGINT NOT NULL, source_event_id CHAR(36) NOT NULL
  ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_bin`);
  await pool.query(`CREATE TABLE IF NOT EXISTS people_history (
    person_id CHAR(36) NOT NULL, version BIGINT NOT NULL,
    operation VARCHAR(12) NOT NULL, full_name VARCHAR(150) NOT NULL,
    dob DATE NOT NULL, recorded_at VARCHAR(30) NOT NULL,
    source_stream VARCHAR(255) NOT NULL, source_position BIGINT NOT NULL,
    source_event_id CHAR(36) NOT NULL, event_type VARCHAR(80) NOT NULL,
    snapshot_json JSON NOT NULL,
    PRIMARY KEY (person_id, version),
    UNIQUE KEY source_event (source_stream, source_position),
    UNIQUE KEY event_id (source_event_id)
  ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_bin`);
  await pool.query(`CREATE TABLE IF NOT EXISTS projection_checkpoints (
    source_stream VARCHAR(255) PRIMARY KEY, position BIGINT NOT NULL DEFAULT -1,
    last_event_id CHAR(36), applied_at VARCHAR(30), heartbeat_at VARCHAR(30),
    last_error TEXT
  ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_bin`);
  await pool.execute(`INSERT IGNORE INTO projection_checkpoints (source_stream, position) VALUES (?, -1)`, [stream]);
  await pool.query('ALTER TABLE people_current ADD COLUMN IF NOT EXISTS email VARCHAR(254) NULL');
  await pool.query('ALTER TABLE people_history ADD COLUMN IF NOT EXISTS email VARCHAR(254) NULL');
}

export function createReadStore(pool, stream) {
  return {
    async checkConnection() {
      await pool.query('SELECT person_id FROM people_current LIMIT 0');
    },
    async list() {
      const [rows] = await pool.query(`SELECT person_id AS id, version, full_name AS fullName, email,
        dob, recorded_at AS recordedAt FROM people_current WHERE deleted = 0
        ORDER BY recorded_at DESC, person_id`);
      return rows.map(row => ({ ...row, version: Number(row.version), age: ageAt(row.dob) }));
    },
    async history(id) {
      const [rows] = await pool.execute(`SELECT person_id AS id, version, operation, email,
        full_name AS fullName, dob, recorded_at AS recordedAt
        FROM people_history WHERE person_id = ? ORDER BY version DESC`, [id]);
      if (!rows.length) throw new AppError(404, 'Không tìm thấy hồ sơ trong Read DB; dữ liệu mới có thể đang đồng bộ.');
      return rows.map(row => ({ ...row, version: Number(row.version) }));
    },
    async position() {
      const [rows] = await pool.execute('SELECT position FROM projection_checkpoints WHERE source_stream = ?', [stream]);
      return rows.length ? Number(rows[0].position) : -1;
    },
    async diagnostics() {
      // One consistent snapshot keeps the checkpoint, trace and table preview aligned.
      const connection = await pool.getConnection();
      try {
        await connection.beginTransaction();
        const [[checkpoint]] = await connection.execute('SELECT * FROM projection_checkpoints WHERE source_stream = ?', [stream]);
        const [events] = await connection.query(`SELECT * FROM people_history ORDER BY recorded_at DESC, source_position DESC LIMIT 20`);
        const [people] = await connection.query(`SELECT * FROM people_current ORDER BY recorded_at DESC, source_position DESC LIMIT 50`);
        const [[counts]] = await connection.query(`SELECT COUNT(*) AS total,
          COALESCE(SUM(deleted = 0), 0) AS active, COALESCE(SUM(deleted = 1), 0) AS deleted FROM people_current`);
        await connection.commit();
        return {
          database: 'MariaDB', schema: process.env.READ_DB_NAME || 'people_read',
          checkpoint: { ...checkpoint, position: Number(checkpoint.position) },
          counts: Object.fromEntries(Object.entries(counts).map(([k, v]) => [k, Number(v)])),
          people: people.map(row => ({ ...row, version: Number(row.version), source_position: Number(row.source_position), deleted: Boolean(row.deleted) })),
          events: events.map(row => ({
            position: Number(row.source_position),
            eventId: row.source_event_id, eventType: row.event_type,
            stream: row.source_stream,
            source: typeof row.snapshot_json === 'string' ? JSON.parse(row.snapshot_json) : row.snapshot_json,
            target: {
              person_id: row.person_id, version: Number(row.version), full_name: row.full_name, email: row.email,
              dob: row.dob, deleted: row.operation === 'deleted', recorded_at: row.recorded_at,
              source_position: Number(row.source_position), source_event_id: row.source_event_id
            }
          }))
        };
      } catch (error) { await connection.rollback(); throw error; }
      finally { connection.release(); }
    }
  };
}
