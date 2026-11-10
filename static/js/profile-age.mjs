// La fecha central de la cédula usa DDMMAA; no verifica identidad ni vigencia.
// Referencia del código de fecha: https://www.pgr.gob.ni/PDF/2024/GACETA/GACETA_18_01_2024.pdf (art. 31).
export function nicaraguaToday(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en', {
    timeZone: 'America/Managua', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(now);
  return Object.fromEntries(parts.filter(({ type }) => ['year', 'month', 'day'].includes(type))
    .map(({ type, value }) => [type, Number(value)]));
}

export function ageFromCedula(value, today = nicaraguaToday(), recordedBirthDate = '') {
  const match = /^\d{3}-(\d{2})(\d{2})(\d{2})-\d{4}[A-Z]$/i.exec(value.trim());
  if (!match) return null;
  const [, dd, mm, yy] = match;
  const day = Number(dd);
  const month = Number(mm);
  // Si existe una fecha registrada coincidente, conserva su siglo.
  const recorded = /^(\d{4})-(\d{2})-(\d{2})$/.exec(recordedBirthDate);
  const useRecordedYear = recorded && recorded[1].slice(-2) === yy && recorded[2] === mm && recorded[3] === dd;
  let year = useRecordedYear ? Number(recorded[1]) : Math.floor(today.year / 100) * 100 + Number(yy);
  if (!useRecordedYear && year > today.year) year -= 100;
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
  const birthdayPending = today.month < month || (today.month === month && today.day < day);
  const age = today.year - year - Number(birthdayPending);
  if (age < 0) return null;
  return { age, year, inferredCentury: !useRecordedYear };
}
