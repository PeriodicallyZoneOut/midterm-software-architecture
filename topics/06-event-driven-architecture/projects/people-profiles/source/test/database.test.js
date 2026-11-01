import { test } from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { createStore } from '../store.js';

test('real KurrentDB: CRUD, paging, concurrent writes, preserved history and tombstones', async () => {
  // An isolated stream keeps integration fixtures out of the live people list.
  const store = createStore({ stream: 'people-test-' + randomUUID(), pageSize: 2 });
  await store.checkConnection();
  assert.deepEqual(await store.list(), []);
  await assert.rejects(store.history(randomUUID()), { status: 404 });

  const person = await store.create({ fullName: 'Integration test', dob: '2000-01-01' });
  assert.ok((await store.list()).some(row => row.id === person.id));
  const original = (await store.history(person.id))[0];
  await store.append(person.id, 1, 'updated', { fullName: 'Version two', dob: '2001-01-01' });
  const races = await Promise.allSettled([
    store.append(person.id, 2, 'updated', { fullName: 'Writer A', dob: '2002-01-01' }),
    store.append(person.id, 2, 'updated', { fullName: 'Writer B', dob: '2003-01-01' })
  ]);
  assert.equal(races.filter(r => r.status === 'fulfilled').length, 1);
  assert.equal(races.find(r => r.status === 'rejected').reason.status, 409);
  await store.append(person.id, 3, 'deleted');
  assert.ok(!(await store.list()).some(row => row.id === person.id));
  const history = await store.history(person.id);
  assert.deepEqual(history.map(row => row.version), [4, 3, 2, 1]);
  assert.equal(history[0].operation, 'deleted');
  assert.equal(history[0].fullName, history[1].fullName);
  assert.deepEqual(history[3], original);
  await assert.rejects(store.append(person.id, 4, 'updated', {
    fullName: 'Restore forbidden', dob: '2000-01-01'
  }), { status: 409 });

  // Different people can retry stream collisions without rejecting good versions.
  const created = await Promise.all([
    store.create({ fullName: 'Independent A', dob: '2000-01-01' }),
    store.create({ fullName: 'Independent B', dob: '2001-01-01' })
  ]);
  await Promise.all(created.map(row => store.append(row.id, 1, 'updated', {
    fullName: row.fullName + ' edited', dob: row.dob
  })));
  const list = await store.list();
  assert.equal(list.length, 2);
  assert.ok(list.every(row => row.version === 2 && Number.isInteger(row.age)));
  for (const row of created) await store.append(row.id, 2, 'deleted');
  assert.deepEqual(await store.list(), []);
  assert.deepEqual((await store.history(person.id))[3], original);
});
