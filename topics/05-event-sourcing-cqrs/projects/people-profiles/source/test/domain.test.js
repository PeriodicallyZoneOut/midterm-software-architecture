import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validatePerson, validateVersion, ageAt } from '../domain.js';

test('accepts a real leap day, trims Unicode names, and does not trust browser age', () => {
  assert.deepEqual(validatePerson({ fullName: '  Nguyễn An  ', dob: '2000-02-29', age: 999 }, '2026-10-22'), {
    fullName: 'Nguyễn An', dob: '2000-02-29'
  });
});

test('rejects impossible dates, future DOBs, missing names, and malformed input', () => {
  for (const input of [
    null, [], {}, { fullName: ' ', dob: '2000-01-01' },
    { fullName: 'An', dob: '2025-02-29' }, { fullName: 'An', dob: '2024-04-31' },
    { fullName: 'An', dob: '2026-10-23' }, { fullName: 'An', dob: '1899-12-31' },
    { fullName: 'An', dob: 'not-a-date' }, { fullName: 'x'.repeat(151), dob: '2000-01-01' }
  ]) assert.throws(() => validatePerson(input, '2026-10-22'), { status: 400 });
});

test('age changes on birthday and handles the year boundary', () => {
  assert.equal(ageAt('2000-10-23', '2026-10-22'), 25);
  assert.equal(ageAt('2000-10-22', '2026-10-22'), 26);
  assert.equal(ageAt('2000-12-31', '2026-01-01'), 25);
});

test('requires a valid integer version to prevent stale/blind edits', () => {
  assert.equal(validateVersion(3), 3);
  for (const value of [undefined, null, 0, -1, '1', 1.5, 4294967295]) {
    assert.throws(() => validateVersion(value), { status: 400 });
  }
});
