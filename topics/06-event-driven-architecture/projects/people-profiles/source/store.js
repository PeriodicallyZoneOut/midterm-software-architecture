import { randomUUID } from 'node:crypto';
import { AppError, ageAt } from './domain.js';

const types = { created: 'PersonCreated', updated: 'PersonUpdated', deleted: 'PersonDeleted' };
const conflict = () => new AppError(409, 'Dữ liệu đã thay đổi hoặc đã bị xóa. Hãy tải lại danh sách.');

// State and outbox commit atomically. RabbitMQ can be offline without losing a write.
export function createStore(pool) {
  async function commit(id, version, operation, person) {
    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();
      const [[previous]] = await connection.execute('SELECT * FROM people_commands WHERE person_id = ? FOR UPDATE', [id]);
      if (operation !== 'created' && (!previous || previous.deleted || Number(previous.version) !== version)) throw conflict();
      const data = {
        id, version: operation === 'created' ? 1 : version + 1, operation,
        fullName: operation === 'deleted' ? previous.full_name : person.fullName,
        dob: operation === 'deleted' ? previous.dob : person.dob,
        email: operation === 'deleted' ? previous.email : person.email,
        recordedAt: new Date().toISOString()
      };
      if (operation === 'created') {
        await connection.execute(`INSERT INTO people_commands
          (person_id, version, full_name, email, dob, deleted, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [id, data.version, data.fullName, data.email, data.dob, false, data.recordedAt]);
      } else {
        await connection.execute(`UPDATE people_commands SET version=?, full_name=?, email=?, dob=?, deleted=?, recorded_at=? WHERE person_id=?`,
        [data.version, data.fullName, data.email, data.dob, operation === 'deleted', data.recordedAt, id]);
      }
      const eventId = randomUUID();
      const [result] = await connection.execute(`INSERT INTO mq_outbox(event_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)`,
        [eventId, types[operation], JSON.stringify(data), data.recordedAt]);
      await connection.commit();
      return { ...data, age: ageAt(data.dob), eventId, sourcePosition: Number(result.insertId) };
    } catch (error) { await connection.rollback(); throw error; }
    finally { connection.release(); }
  }
  return {
    async checkConnection() { await pool.query('SELECT position FROM mq_outbox LIMIT 0'); },
    create(person) { return commit(randomUUID(), 0, 'created', person); },
    append(id, version, operation, person) {
      if (!['updated', 'deleted'].includes(operation)) throw new AppError(400, 'Thao tác không hợp lệ.');
      return commit(id, version, operation, person);
    }
  };
}
