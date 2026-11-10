// Reglas de formato para la vista de registro. No comprueban identidad ni titularidad.
const namePattern = /^[\p{L}\p{M}]+(?:[ '’\-]+[\p{L}\p{M}]+)*$/u;
const codePattern = /^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/;
const emailPattern = /^[A-Za-z0-9._+\-]+@outlook\.com$/i;

function validateName(value, label) {
  if (!value) return `Ingresa tus ${label}.`;
  if (value.length > 75) return `Los ${label} deben tener como máximo 75 caracteres.`;
  return namePattern.test(value) ? '' : 'Usa letras, espacios, guiones o apóstrofos; sin números.';
}

function validateIdentity(value) {
  if (!value) return 'Ingresa tu cédula nicaragüense.';
  const match = /^(\d{3})-(\d{2})(\d{2})(\d{2})-(\d{4})([A-Z])$/i.exec(value);
  if (!match) return 'Usa el formato 000-DDMMAA-0000A, incluidos los guiones y la letra final.';
  const day = Number(match[2]);
  const month = Number(match[3]);
  const year = 2000 + Number(match[4]);
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) {
    return 'La fecha incluida en la cédula no es una fecha válida.';
  }
  return '';
}

function validateEmail(value) {
  if (!value) return 'Ingresa tu correo de Outlook.';
  if (!emailPattern.test(value)) {
    return 'Usa un correo @outlook.com con letras sin tildes, números, puntos, guiones, _ o +.';
  }
  const local = value.slice(0, value.indexOf('@'));
  if (local.length > 64 || value.length > 254 || local.startsWith('.') || local.endsWith('.') || local.includes('..')) {
    return 'Revisa el correo: máximo 64 caracteres antes de @, sin puntos seguidos, iniciales o finales.';
  }
  return '';
}

function validatePassword(value) {
  if (!value) return 'Ingresa una contraseña.';
  const characters = Array.from(value);
  if (characters.length < 8 || characters.length > 128) return 'La contraseña debe tener entre 8 y 128 caracteres.';
  if (/[\p{Cc}\p{Cf}]/u.test(value)) return 'La contraseña no puede incluir caracteres de control o invisibles.';
  // Puntuación ASCII: incluye ! @ # $ % & * y los demás símbolos estándar.
  const hasSymbol = characters.some(character => {
    const code = character.codePointAt(0);
    return (code >= 33 && code <= 47) || (code >= 58 && code <= 64) ||
      (code >= 91 && code <= 96) || (code >= 123 && code <= 126);
  });
  return hasSymbol ? '' : 'Incluye al menos un símbolo estándar, por ejemplo ! @ # $ % & *.';
}

export function validateRegistrationField(fieldId, rawValue) {
  // Las contraseñas se validan exactamente como se escriben, sin recortarlas.
  const value = fieldId === 'registerPassword' ? rawValue : rawValue.trim().normalize('NFC');
  switch (fieldId) {
    case 'registerNames': return validateName(value, 'nombres');
    case 'registerSurnames': return validateName(value, 'apellidos');
    case 'registerSex':
      return ['Femenino', 'Masculino'].includes(value) ? '' : 'Selecciona una opción para el sexo.';
    case 'registerCode':
      if (!value) return 'Ingresa tu código único de persona.';
      return value.length <= 20 && codePattern.test(value) ? '' : 'Usa hasta 20 letras o números, separados opcionalmente por guiones.';
    case 'registerIdentity': return validateIdentity(value);
    case 'registerEmail': return validateEmail(rawValue);
    case 'registerPassword': return validatePassword(value);
    default: throw new Error('Campo de registro desconocido.');
  }
}
