import { readFileSync } from 'node:fs';

if (process.env.DB_NAME !== 'people_append_only' || process.env.DB_USER !== 'people_append_app') {
  throw new Error('Setup dùng DB_NAME=people_append_only và DB_USER=people_append_app.');
}
const password = process.env.DB_PASSWORD;
if (!password || password === 'replace_me' || !/^[a-zA-Z0-9_-]{20,128}$/.test(password)) {
  throw new Error('DB_PASSWORD cần 20–128 ký tự chữ, số, _ hoặc -. Xóa .env mẫu để setup tự sinh.');
}
let sql = readFileSync(new URL('./schema.sql', import.meta.url), 'utf8');
for (const host of ['localhost', '127.0.0.1']) {
  const account = `'people_append_app'@'${host}'`;
  sql += `\nCREATE USER IF NOT EXISTS ${account} IDENTIFIED BY '${password}';\n`;
  sql += `ALTER USER ${account} IDENTIFIED BY '${password}';\n`;
  sql += `REVOKE ALL PRIVILEGES, GRANT OPTION FROM ${account};\n`;
  sql += `GRANT SELECT, INSERT ON people_append_only.person_events TO ${account};\n`;
}
process.stdout.write(sql);
