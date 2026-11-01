import nodemailer from 'nodemailer';
import { parseEnv } from 'node:util';
import { readFileSync } from 'node:fs';
import { createReadPool } from './read-db.js';
import { runConsumer } from './consumer.js';
import { EMAIL_TO } from './mq.js';

const pool = createReadPool();
function config() {
  try { return parseEnv(readFileSync(process.env.SMTP_CONFIG_FILE || '/run/secrets/smtp_config', 'utf8')); }
  catch { return {}; }
}
function details() {
  const c = config();
  return { recipient: EMAIL_TO, smtpConfigured: Boolean(c.SMTP_USER && c.SMTP_PASS) };
}

async function handle(event, offset) {
  if (event.notifyEmail === false) {
    await pool.execute(`INSERT IGNORE INTO email_deliveries(event_id,source_position,broker_offset,recipient,status,payload_json)
      VALUES (?,?,?,?,'skipped-history',?)`, [event.eventId,event.position,offset,EMAIL_TO,JSON.stringify(event)]);
    await pool.execute("UPDATE mq_consumer_offsets SET broker_offset=GREATEST(broker_offset,?),last_event_id=?,processed_at=? WHERE consumer_name='email'", [offset,event.eventId,new Date().toISOString()]);
    return;
  }
  const [[existing]] = await pool.execute('SELECT status FROM email_deliveries WHERE event_id=?', [event.eventId]);
  if (existing?.status !== 'sent') {
    await pool.execute(`INSERT IGNORE INTO email_deliveries
      (event_id,source_position,broker_offset,recipient,status,payload_json) VALUES (?,?,?,?,'pending',?)`,
    [event.eventId,event.position,offset,EMAIL_TO,JSON.stringify(event)]);
    const c = config();
    if (!c.SMTP_USER || !c.SMTP_PASS) {
      await pool.execute("UPDATE email_deliveries SET status='awaiting-config',last_error='SMTP_NOT_CONFIGURED' WHERE event_id=?", [event.eventId]);
      throw Object.assign(new Error('SMTP_NOT_CONFIGURED'), { code: 'SMTP_NOT_CONFIGURED' });
    }
    const transport = nodemailer.createTransport({
      host: c.SMTP_HOST || 'smtp.gmail.com', port: Number(c.SMTP_PORT || 465),
      secure: c.SMTP_SECURE !== 'false', auth: { user: c.SMTP_USER, pass: c.SMTP_PASS },
      connectionTimeout: 15000, greetingTimeout: 15000, socketTimeout: 30000
    });
    const labels = { PersonCreated: 'Thêm hồ sơ', PersonUpdated: 'Sửa hồ sơ', PersonDeleted: 'Xóa hồ sơ' };
    const data = event.data;
    const messageId = '<' + event.eventId + '@people.local>';
    await pool.execute("UPDATE email_deliveries SET status='sending',attempts=attempts+1,last_error=NULL WHERE event_id=?", [event.eventId]);
    try {
      const result = await transport.sendMail({
        from: c.SMTP_FROM || c.SMTP_USER, to: EMAIL_TO, messageId,
        subject: '[Hồ sơ] ' + (labels[event.eventType] || event.eventType) + ' — ' + data.fullName,
        text: [labels[event.eventType] || event.eventType, '', 'Họ tên: ' + data.fullName,
          'Email hồ sơ: ' + (data.email || '(chưa có)'), 'Ngày sinh: ' + data.dob,
          'Phiên bản: ' + data.version, 'Thời gian: ' + data.recordedAt,
          '', 'MQ event ID: ' + event.eventId, 'MQ offset: ' + offset].join('\n')
      });
      if (!result.accepted?.some(address => address.toLowerCase() === EMAIL_TO)) throw Object.assign(new Error('Recipient rejected'), { code: 'RECIPIENT_REJECTED' });
      await pool.execute("UPDATE email_deliveries SET status='sent',sent_at=?,message_id=?,last_error=NULL WHERE event_id=?", [new Date().toISOString(),result.messageId,event.eventId]);
    } catch (error) {
      const safe = (error.code || 'SMTP_ERROR') + (error.responseCode ? ' HTTP/SMTP ' + error.responseCode : '');
      await pool.execute("UPDATE email_deliveries SET status='retry',last_error=? WHERE event_id=?", [safe,event.eventId]);
      throw Object.assign(new Error(safe), { code: safe });
    } finally { transport.close(); }
  }
  await pool.execute(`UPDATE mq_consumer_offsets SET broker_offset=GREATEST(broker_offset,?),last_event_id=?,processed_at=? WHERE consumer_name='email'`,
    [offset,event.eventId,new Date().toISOString()]);
}

await runConsumer({ name: 'email', port: 3005, pool, handler: handle, details });
