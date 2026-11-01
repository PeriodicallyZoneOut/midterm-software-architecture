import { validatePerson, validateVersion } from './domain.js';
import { EXCHANGE } from './mq.js';
const operations = { PersonCreated: 'created', PersonUpdated: 'updated', PersonDeleted: 'deleted' };

export function mapEvent(event) {
  const data = event.data;
  const operation = operations[event.eventType];
  if (!data || !operation || data.operation !== operation || !/^[0-9a-f-]{36}$/i.test(data.id) ||
      !Number.isSafeInteger(event.position) || !Number.isFinite(Date.parse(data.recordedAt))) throw new Error('Invalid event');
  if (operation !== 'deleted') validatePerson(data, undefined, { emailRequired: event.notifyEmail !== false });
  validateVersion(data.version);
  return { person_id: data.id, version: data.version, full_name: data.fullName,
    email: data.email ?? null, dob: data.dob, deleted: operation === 'deleted',
    recorded_at: data.recordedAt, source_position: event.position, source_event_id: event.eventId, operation };
}

export async function applyEvent(pool, event, brokerOffset) {
  const row = mapEvent(event);
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();
    await connection.execute("SELECT broker_offset FROM mq_consumer_offsets WHERE consumer_name='read-db' FOR UPDATE");
    const [[seen]] = await connection.execute("SELECT event_id FROM consumer_inbox WHERE consumer_name='read-db' AND event_id=?", [event.eventId]);
    if (!seen) {
      const [[historical]] = await connection.execute('SELECT source_event_id FROM people_history WHERE source_event_id=?', [event.eventId]);
      if (!historical) await connection.execute(`INSERT INTO people_history
        (person_id,version,operation,full_name,email,dob,recorded_at,source_stream,source_position,source_event_id,event_type,snapshot_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`, [row.person_id,row.version,row.operation,row.full_name,row.email,row.dob,
        row.recorded_at,EXCHANGE,event.position,event.eventId,event.eventType,JSON.stringify(event.data)]);
      const [[previous]] = await connection.execute('SELECT version FROM people_current WHERE person_id=? FOR UPDATE', [row.person_id]);
      if (!previous || row.version > Number(previous.version)) {
        await connection.execute(`INSERT INTO people_current
          (person_id,version,full_name,email,dob,deleted,recorded_at,source_position,source_event_id) VALUES (?,?,?,?,?,?,?,?,?)
          ON DUPLICATE KEY UPDATE version=VALUES(version),full_name=VALUES(full_name),email=VALUES(email),dob=VALUES(dob),
          deleted=VALUES(deleted),recorded_at=VALUES(recorded_at),source_position=VALUES(source_position),source_event_id=VALUES(source_event_id)`,
        [row.person_id,row.version,row.full_name,row.email,row.dob,row.deleted,row.recorded_at,event.position,event.eventId]);
      }
      await connection.execute(`INSERT INTO consumer_inbox(consumer_name,event_id,source_position,broker_offset,processed_at)
        VALUES ('read-db',?,?,?,?)`, [event.eventId,event.position,brokerOffset,new Date().toISOString()]);
    }
    const now = new Date().toISOString();
    await connection.execute(`UPDATE mq_consumer_offsets SET broker_offset=GREATEST(broker_offset,?),last_event_id=?,processed_at=? WHERE consumer_name='read-db'`, [brokerOffset,event.eventId,now]);
    await connection.execute(`UPDATE projection_checkpoints SET position=GREATEST(position,?),last_event_id=?,applied_at=?,heartbeat_at=?,last_error=NULL WHERE source_stream=?`, [event.position,event.eventId,now,now,EXCHANGE]);
    await connection.commit();
  } catch (error) { await connection.rollback(); throw error; }
  finally { connection.release(); }
}
