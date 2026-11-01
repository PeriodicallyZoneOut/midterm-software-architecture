import { ensureReadSchema } from './read-db.js';
import { EXCHANGE } from './mq.js';

export async function migrate(pool) {
  await ensureReadSchema(pool, EXCHANGE);
  await pool.query(`CREATE TABLE IF NOT EXISTS people_commands (
    person_id CHAR(36) PRIMARY KEY, version BIGINT NOT NULL,
    full_name VARCHAR(150) NOT NULL, email VARCHAR(254), dob DATE NOT NULL,
    deleted BOOLEAN NOT NULL, recorded_at VARCHAR(30) NOT NULL
  ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_bin`);
  // Bootstrap existing people without publishing old history or sending old emails.
  await pool.query(`INSERT IGNORE INTO people_commands
    (person_id, version, full_name, email, dob, deleted, recorded_at)
    SELECT person_id, version, full_name, email, dob, deleted, recorded_at FROM people_current`);
  await pool.query(`CREATE TABLE IF NOT EXISTS mq_outbox (
    position BIGINT AUTO_INCREMENT PRIMARY KEY, event_id CHAR(36) NOT NULL UNIQUE,
    event_type VARCHAR(80) NOT NULL, payload_json JSON NOT NULL,
    created_at VARCHAR(30) NOT NULL, published_at VARCHAR(30), last_error TEXT,
    notify_email BOOLEAN NOT NULL DEFAULT 1
  ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_bin`);
  await pool.query(`INSERT IGNORE INTO mq_outbox(event_id,event_type,payload_json,created_at,notify_email)
    SELECT source_event_id,event_type,snapshot_json,recorded_at,0 FROM people_history
    WHERE source_stream='people-profiles' ORDER BY source_position`);
  await pool.query(`CREATE TABLE IF NOT EXISTS consumer_inbox (
    consumer_name VARCHAR(40) NOT NULL, event_id CHAR(36) NOT NULL,
    source_position BIGINT NOT NULL, broker_offset BIGINT NOT NULL, processed_at VARCHAR(30) NOT NULL,
    PRIMARY KEY(consumer_name, event_id)
  ) ENGINE=InnoDB`);
  await pool.query(`CREATE TABLE IF NOT EXISTS mq_consumer_offsets (
    consumer_name VARCHAR(40) PRIMARY KEY, broker_offset BIGINT NOT NULL DEFAULT -1,
    last_event_id CHAR(36), processed_at VARCHAR(30)
  ) ENGINE=InnoDB`);
  await pool.query(`CREATE TABLE IF NOT EXISTS worker_status (
    name VARCHAR(40) PRIMARY KEY, state VARCHAR(40) NOT NULL,
    heartbeat_at VARCHAR(30), last_error TEXT, detail_json JSON
  ) ENGINE=InnoDB`);
  await pool.query(`CREATE TABLE IF NOT EXISTS email_deliveries (
    event_id CHAR(36) PRIMARY KEY, source_position BIGINT NOT NULL, broker_offset BIGINT NOT NULL,
    recipient VARCHAR(254) NOT NULL, status VARCHAR(40) NOT NULL,
    attempts INT NOT NULL DEFAULT 0, last_error TEXT, sent_at VARCHAR(30),
    message_id VARCHAR(255), payload_json JSON NOT NULL
  ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_bin`);
  for (const name of ['publisher', 'read-db', 'email']) {
    await pool.execute("INSERT IGNORE INTO worker_status(name, state) VALUES (?, 'starting')", [name]);
  }
  for (const name of ['read-db', 'email']) {
    await pool.execute('INSERT IGNORE INTO mq_consumer_offsets(consumer_name) VALUES (?)', [name]);
  }
}

export async function heartbeat(pool, name, state, error = null, detail = {}) {
  await pool.execute(`UPDATE worker_status SET state = ?, last_error = ?,
    heartbeat_at = ?, detail_json = ? WHERE name = ?`,
  [state, error, new Date().toISOString(), JSON.stringify(detail), name]);
}
