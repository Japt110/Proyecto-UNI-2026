import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateRegistrationField as validate } from '../static/js/registration-validation.mjs';

test('all registration fields are required', () => {
  for (const field of ['registerNames', 'registerSurnames', 'registerSex', 'registerCode', 'registerIdentity', 'registerEmail', 'registerPassword']) {
    assert.notEqual(validate(field, ''), '', field);
  }
});

test('names accept accents and compound names, and reject digits and markup', () => {
  for (const value of ['María José', 'Nuñez', 'Mun\u0303oz', "O'Connor", 'D’Ávila', 'Pérez-García']) {
    assert.equal(validate('registerNames', value), '', value);
    assert.equal(validate('registerSurnames', value), '', value);
  }
  for (const value of ['   ', 'Ana123', '<script>', 'Ana\nMaría', 'A'.repeat(76)]) {
    assert.notEqual(validate('registerNames', value), '', value);
  }
});

test('person code accepts existing alphanumeric/hyphen formats with a length limit', () => {
  for (const value of ['8k4B7UP5', 'NUP-2026-101', '2021-12345']) {
    assert.equal(validate('registerCode', value), '', value);
  }
  for (const value of ['A B', '--ABC', 'ABC-', 'Ñ123', '<ABC>', 'X'.repeat(21)]) {
    assert.notEqual(validate('registerCode', value), '', value);
  }
});

test('identity validates format and calendar dates without claiming authenticity', () => {
  for (const value of ['001-120503-1004A', '001-290200-1004a']) {
    assert.equal(validate('registerIdentity', value), '', value);
  }
  for (const value of ['001-310299-1004A', '001-290201-1004A', '001-001303-1004A', '001-120503-1004', '001-120503-1004AA']) {
    assert.notEqual(validate('registerIdentity', value), '', value);
  }
});

test('Outlook email accepts standard ASCII address characters and + tags', () => {
  for (const value of ['ana@outlook.com', 'ANA.PEREZ@OUTLOOK.COM', 'ana_perez-2@outlook.com', 'ana+uni@outlook.com']) {
    assert.equal(validate('registerEmail', value), '', value);
  }
});

test('email rejects lookalike domains, non-ASCII input, whitespace and malformed dots', () => {
  for (const value of [
    'ana@gmail.com', 'ana@outlook.com.evil.test', 'ana@eviloutlook.com', 'ana@outlоok.com',
    'aná@outlook.com', 'ana perez@outlook.com', 'ana@outlook.com ', 'ana\n@outlook.com',
    '.ana@outlook.com', 'ana.@outlook.com', 'ana..perez@outlook.com', 'ana@@outlook.com',
    '<ana>@outlook.com', 'ana"@outlook.com', `${'a'.repeat(65)}@outlook.com`,
  ]) {
    assert.notEqual(validate('registerEmail', value), '', value);
  }
});

test('password accepts the eight-character boundary and requires an ASCII symbol', () => {
  for (const value of ['abcdefg!', '1234567@', 'Cláveñ12#', 'mi frase larga!', `${'a'.repeat(127)}!`]) {
    assert.equal(validate('registerPassword', value), '');
  }
  for (const value of ['abcdef!', 'abcdefgh', 'abcdefg😀', 'abcd\n123!', 'abcd\u200B123!', `${'a'.repeat(128)}!`]) {
    assert.notEqual(validate('registerPassword', value), '');
  }
});
