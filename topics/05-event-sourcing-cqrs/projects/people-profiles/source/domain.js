export class AppError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export function validatePerson(input, today = new Date().toISOString().slice(0, 10), { emailRequired = true } = {}) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throw new AppError(400, 'Dữ liệu không hợp lệ.');
  }
  const fullName = typeof input.fullName === 'string' ? input.fullName.trim() : '';
  if (!fullName || [...fullName].length > 150 || /[\u0000-\u001f]/u.test(fullName)) {
    throw new AppError(400, 'Họ tên cần có từ 1 đến 150 ký tự.');
  }
  const dob = input.dob;
  if (typeof dob !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(dob)) {
    throw new AppError(400, 'Ngày sinh cần có định dạng YYYY-MM-DD.');
  }
  const date = new Date(`${dob}T00:00:00Z`);
  if (Number.isNaN(date.getTime()) || date.toISOString().slice(0, 10) !== dob || dob < '1900-01-01' || dob > today) {
    throw new AppError(400, 'Ngày sinh phải là ngày có thật, từ năm 1900 đến hôm nay.');
  }
  const email = typeof input.email === 'string' ? input.email.trim().toLowerCase() : '';
  if ((emailRequired && !email) || (email && (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || /[\r\n]/.test(email)))) {
    throw new AppError(400, 'Email không hợp lệ.');
  }
  return { fullName, dob, email: email || null };
}

export function validateVersion(value) {
  if (!Number.isSafeInteger(value) || value < 1 || value >= 4294967295) {
    throw new AppError(400, 'Phiên bản không hợp lệ.');
  }
  return value;
}

export function ageAt(dob, today = new Date().toISOString().slice(0, 10)) {
  const age = Number(today.slice(0, 4)) - Number(dob.slice(0, 4));
  return age - (today.slice(5) < dob.slice(5) ? 1 : 0);
}
