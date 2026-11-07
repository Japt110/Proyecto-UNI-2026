import test from 'node:test';
import assert from 'node:assert/strict';
import { ageFromCedula, nicaraguaToday } from '../static/js/profile-age.mjs';

const today = { year: 2026, month: 11, day: 6 };
test('calcula años cumplidos antes, durante y después del cumpleaños', () => {
  assert.equal(ageFromCedula('001-071100-0001A', today).age, 25);
  assert.equal(ageFromCedula('001-061100-0001A', today).age, 26);
  assert.equal(ageFromCedula('001-051100-0001A', today).age, 26);
});
test('interpreta años del siglo anterior y admite espacios y letra minúscula', () => {
  assert.equal(ageFromCedula(' 001-010199-0001a ', today).age, 27);
});
test('no calcula edades para cédulas incompletas, fechas imposibles ni fechas futuras', () => {
  for (const value of ['', '001-010100', '001-310200-0001A', '001-290201-0001A', '001-011300-0001A', '001-071126-0001A']) {
    assert.equal(ageFromCedula(value, today), null, value);
  }
});
test('respeta años bisiestos y el cumpleaños del 29 de febrero', () => {
  assert.equal(ageFromCedula('001-290200-0001A', { year: 2025, month: 2, day: 28 }).age, 24);
  assert.equal(ageFromCedula('001-290200-0001A', { year: 2025, month: 3, day: 1 }).age, 25);
});
test('usa una fecha registrada coincidente para resolver la ambigüedad de siglo', () => {
  assert.deepEqual(ageFromCedula('001-010100-0001A', today, '1900-01-01'), { age: 126, year: 1900, inferredCentury: false });
  assert.equal(ageFromCedula('001-290200-0001A', today, '1900-02-29'), null);
  assert.equal(ageFromCedula('001-010100-0001A', today, '1999-01-01').age, 26);
});
test('usa la fecha de Nicaragua aunque UTC ya esté en el siguiente día', () => {
  assert.deepEqual(nicaraguaToday(new Date('2026-11-07T02:00:00Z')), today);
});
