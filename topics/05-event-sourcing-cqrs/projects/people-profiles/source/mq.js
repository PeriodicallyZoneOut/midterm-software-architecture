import amqp from 'amqplib';
import { readFileSync } from 'node:fs';

export const EXCHANGE = process.env.MQ_EXCHANGE || 'people.events';
export const STREAM = 'people.events.retained';
export const PREVIEW = 'people.events.preview';
export const EMAIL_TO = 'gtvbeon@gmail.com';

function credentials() {
  return {
    username: process.env.MQ_USER || 'people_app',
    password: readFileSync(process.env.MQ_PASSWORD_FILE || '/run/secrets/mq_password', 'utf8').trim()
  };
}

export async function openMQ() {
  const connection = await amqp.connect({
    protocol: 'amqp', hostname: process.env.MQ_HOST || 'rabbitmq', port: 5672,
    ...credentials(), vhost: '/', heartbeat: 20
  }, { timeout: 8000 });
  connection.on('error', () => {});
  const closed = new Promise(resolve => connection.once('close', resolve));
  try {
    const channel = await connection.createConfirmChannel();
    channel.on('error', () => {});
    await channel.assertExchange(EXCHANGE, 'fanout', { durable: true });
    // Stream ACKs advance delivery credit; they never delete the retained event.
    await channel.assertQueue(STREAM, { durable: true, arguments: { 'x-queue-type': 'stream' } });
    await channel.bindQueue(STREAM, EXCHANGE, '');
    // A classic mirror lets RabbitMQ Management's Get messages show payloads.
    await channel.assertQueue(PREVIEW, { durable: true, arguments: { 'x-queue-type': 'classic' } });
    await channel.bindQueue(PREVIEW, EXCHANGE, '');
    return { connection, channel, closed };
  } catch (error) { await connection.close().catch(() => {}); throw error; }
}

export function publishConfirmed(channel, event, queue = null, headers = {}) {
  return new Promise((resolve, reject) => {
    let returned = false;
    const onReturn = msg => { if (msg.properties.messageId === event.eventId) returned = true; };
    channel.on('return', onReturn);
    const callback = error => {
      channel.off('return', onReturn);
      if (error || returned) reject(error || new Error('Message unroutable'));
      else resolve();
    };
    const options = { persistent: true, mandatory: true, contentType: 'application/json',
      messageId: event.eventId, type: event.eventType, headers };
    const body = Buffer.from(JSON.stringify(event));
    if (queue) channel.sendToQueue(queue, body, options, callback);
    else channel.publish(EXCHANGE, '', body, options, callback);
  });
}

export async function brokerStatus() {
  const auth = credentials();
  const response = await fetch('http://' + (process.env.MQ_HOST || 'rabbitmq') + ':15672/api/queues/%2F', {
    headers: { Authorization: 'Basic ' + Buffer.from(auth.username + ':' + auth.password).toString('base64') },
    signal: AbortSignal.timeout(5000)
  });
  if (!response.ok) throw new Error('RabbitMQ management HTTP ' + response.status);
  return (await response.json()).filter(q => q.name === STREAM).map(q => ({
    name: q.name, type: q.type, retained: q.messages || 0,
    ready: q.messages_ready || 0, unacked: q.messages_unacknowledged || 0,
    consumers: q.consumers || 0
  }));
}

// A short-lived, non-destructive viewer. It has no effect on business offsets.
export async function readRetained() {
  const mq = await openMQ();
  const messages = [];
  let tag;
  let idle;
  try {
    await mq.channel.prefetch(64);
    let finish;
    const done = new Promise(resolve => { finish = resolve; });
    const timeout = setTimeout(() => finish(), 1500);
    const consumer = await mq.channel.consume(STREAM, message => {
      if (!message) return finish();
      try {
        const event = JSON.parse(message.content.toString());
        messages.push({ ...event, brokerOffset: Number(message.properties.headers['x-stream-offset']) });
        if (messages.length > 20) messages.shift();
        mq.channel.ack(message);
      } catch { finish(); }
      clearTimeout(idle);
      idle = setTimeout(() => finish(), 300);
    }, { noAck: false, arguments: { 'x-stream-offset': 'first' } });
    tag = consumer.consumerTag;
    await done;
    clearTimeout(timeout);
    clearTimeout(idle);
    return messages.reverse();
  } finally {
    if (tag) await mq.channel.cancel(tag).catch(() => {});
    await mq.connection.close().catch(() => {});
  }
}
