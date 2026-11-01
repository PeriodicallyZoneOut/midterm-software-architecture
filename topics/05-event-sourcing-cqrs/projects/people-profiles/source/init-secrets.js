import { mkdirSync, existsSync, writeFileSync, chmodSync, readFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';

// The host directory is private; mounted secret files must also be readable by
// MariaDB's container UID and the Node container UID. Compose mounts only the
// specific secrets listed on each service, and they never enter the image.
mkdirSync('.secrets', { recursive: true, mode: 0o700 });
chmodSync('.secrets', 0o700);
for (const name of ['read-db-root-password', 'read-db-password', 'mq-password']) {
  const path = '.secrets/' + name;
  if (!existsSync(path)) writeFileSync(path, randomBytes(32).toString('base64url'), { mode: 0o444, flag: 'wx' });
  chmodSync(path, 0o444);
}
if (!existsSync('.secrets/rabbitmq.conf')) writeFileSync('.secrets/rabbitmq.conf',
  'default_user = people_app\ndefault_pass = ' + readFileSync('.secrets/mq-password', 'utf8').trim() +
  '\ndefault_user_tags.administrator = true\n', { mode: 0o444 });
chmodSync('.secrets/rabbitmq.conf', 0o444);
if (!existsSync('.env.smtp')) {
  writeFileSync('.env.smtp', readFileSync('.env.smtp.example'), { mode: 0o600 });
}
console.log('Docker secrets đã sẵn sàng. Giá trị không được in ra.');
