const $ = selector => document.querySelector(selector);
let people = [];
let editing = null;
let busy = false;
let historyId = null;
// Construct local ISO date explicitly; do not rely on browser locale formatting.
const now = new Date();
const localDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
$('#dob').max = localDate;

function notice(message = '', error = false) {
  $('#notice').textContent = message;
  $('#notice').classList.toggle('error', error);
}

async function api(path, method = 'GET', data) {
  const response = await fetch(path, { method, ...(data ? {
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
  } : {}) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Yêu cầu thất bại.');
  return result;
}

function age(dob) {
  if (!dob) return '';
  return now.getFullYear() - Number(dob.slice(0, 4)) - (localDate.slice(5) < dob.slice(5) ? 1 : 0);
}
$('#dob').addEventListener('input', () => { $('#age').value = age($('#dob').value); });

function reset() {
  editing = null;
  $('#person-form').reset();
  $('#age').value = '';
  $('#form-title').textContent = 'Thêm hồ sơ';
  $('#version').textContent = 'Mới';
  $('#save').textContent = 'Lưu hồ sơ';
  $('#cancel').hidden = true;
}

function edit(person) {
  if (busy) return;
  editing = { ...person };
  $('#full-name').value = person.fullName;
  $('#dob').value = person.dob;
  $('#email').value = person.email || ''; 
  $('#age').value = age(person.dob);
  $('#form-title').textContent = 'Sửa hồ sơ';
  $('#version').textContent = `Phiên bản ${person.version}`;
  $('#save').textContent = 'Lưu phiên bản mới';
  $('#cancel').hidden = false;
  $('#full-name').focus();
}

function cell(text) {
  const td = document.createElement('td');
  td.textContent = text;
  return td;
}

async function load() {
  people = await api('/api/people');
  $('#count').textContent = `${people.length} hồ sơ đang hiển thị`;
  $('#empty').hidden = people.length > 0;
  $('#people').replaceChildren();
  for (const person of people) {
    const row = document.createElement('tr');
    row.append(cell(person.fullName), cell(person.email || 'Chưa có'), cell(person.dob.split('-').reverse().join('/')), cell(age(person.dob)));
    const actions = document.createElement('td');
    const buttons = document.createElement('div');
    buttons.className = 'row-actions';
    for (const [label, className, callback] of [
      ['Sửa', 'secondary', () => edit(person)],
      ['Lịch sử', 'secondary', () => showHistory(person.id)],
      ['Xóa', 'danger', () => remove(person)]
    ]) {
      const button = document.createElement('button');
      button.type = 'button'; button.textContent = label; button.className = className;
      button.setAttribute('aria-label', `${label}: ${person.fullName}`);
      button.disabled = busy;
      button.addEventListener('click', callback);
      buttons.append(button);
    }
    actions.append(buttons); row.append(actions); $('#people').append(row);
  }
}

async function showHistory(id) {
  try {
    const rows = await api(`/api/people/${id}/history`);
    historyId = id;
    $('#history-title').textContent = `Lịch sử · ${rows[0].fullName}`;
    $('#history').replaceChildren();
    const names = { created: 'Tạo', updated: 'Sửa', deleted: 'Xóa' };
    for (const row of rows) {
      const item = document.createElement('article'); item.className = 'history-item';
      const title = document.createElement('strong');
      title.textContent = `Phiên bản ${row.version} · ${names[row.operation]}`;
      const detail = document.createElement('p'); detail.textContent = `${row.fullName} · ${row.email || 'Chưa có email'} · Ngày sinh ${row.dob}`;
      const date = document.createElement('p'); date.textContent = row.recordedAt;
      item.append(title, detail, date); $('#history').append(item);
    }
    $('#history-panel').hidden = false;
  } catch (error) { notice(error.message, true); }
}

async function mutate(action, success) {
  if (busy) return;
  busy = true;
  document.querySelectorAll('button, #person-form input').forEach(el => { el.disabled = true; });
  try {
    const result = await action();
    reset();
    const message = result.projected === false
      ? `${success} Đã lưu vào outbox để gửi MQ; Read DB đang chờ đồng bộ. Hãy chờ rồi nhấn Tải lại.`
      : success;
    notice(message);
    try {
      await load();
      if (historyId) await showHistory(historyId);
    } catch {
      notice(`${success} Không tải lại được danh sách; hãy nhấn Tải lại.`, true);
    }
  } catch (error) { notice(error.message, true); }
  finally {
    busy = false;
    document.querySelectorAll('button, #person-form input').forEach(el => { el.disabled = false; });
  }
}

function remove(person) {
  if (!confirm(`Xóa hồ sơ “${person.fullName}” khỏi danh sách? Lịch sử vẫn được giữ lại.`)) return;
  return mutate(() => api(`/api/people/${person.id}`, 'DELETE', { version: person.version }), 'Đã thêm dấu xóa. Hồ sơ cũ vẫn còn trong lịch sử.');
}

$('#person-form').addEventListener('submit', event => {
  event.preventDefault();
  const data = { fullName: $('#full-name').value.trim(), dob: $('#dob').value, email: $('#email').value.trim() };
  const selected = editing;
  mutate(() => selected
    ? api(`/api/people/${selected.id}`, 'PUT', { ...data, version: selected.version })
    : api('/api/people', 'POST', data), selected ? 'Đã lưu phiên bản mới.' : 'Đã thêm hồ sơ.');
});
$('#cancel').addEventListener('click', reset);
$('#refresh').addEventListener('click', async () => { try { await load(); notice('Đã tải lại danh sách.'); } catch (error) { notice(error.message, true); } });
$('#close-history').addEventListener('click', () => { historyId = null; $('#history-panel').hidden = true; });
load().catch(error => { $('#count').textContent = 'Chưa tải được dữ liệu'; notice(error.message, true); });
