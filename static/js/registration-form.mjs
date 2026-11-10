import { validateRegistrationField } from './registration-validation.mjs';

const form = document.getElementById('registerForm');
const fields = Array.from(form.querySelectorAll('input, select'));
const touched = new Set();
const submitButton = document.getElementById('registerSubmit');
const backButton = document.getElementById('showLogin');
const status = document.getElementById('authStatus');
const payloadFields = {
  registerNames: 'nombres', registerSurnames: 'apellidos', registerSex: 'sexo',
  registerCode: 'numero_unico', registerIdentity: 'cedula', registerEmail: 'email', registerPassword: 'password',
};
let submitting = false;

function showStatus(message, state = 'error') {
  status.textContent = message;
  status.dataset.state = state;
  status.hidden = false;
}

function validateField(input) {
  const message = validateRegistrationField(input.id, input.value);
  const error = document.getElementById(`${input.id}Error`);
  input.setCustomValidity(message);
  input.setAttribute('aria-invalid', String(Boolean(message)));
  error.textContent = message;
  error.hidden = !message;
  return !message;
}

fields.forEach(input => {
  input.addEventListener('blur', () => {
    touched.add(input.id);
    validateField(input);
  });
  input.addEventListener('input', () => {
    if (touched.has(input.id)) validateField(input);
  });
  input.addEventListener('change', () => {
    touched.add(input.id);
    validateField(input);
  });
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  if (submitting) return;
  let firstInvalid = null;
  fields.forEach(input => {
    touched.add(input.id);
    if (!validateField(input) && !firstInvalid) firstInvalid = input;
  });
  if (firstInvalid) {
    showStatus('Revisa los campos indicados antes de crear tu cuenta.');
    firstInvalid.focus();
    return;
  }
  const payload = Object.fromEntries(fields.map(input => [payloadFields[input.id], input.value]));
  submitting = true;
  submitButton.disabled = true;
  backButton.disabled = true;
  form.setAttribute('aria-busy', 'true');
  submitButton.textContent = 'Creando cuenta…';
  showStatus('Guardando tu cuenta…', 'pending');
  try {
    const csrfResponse = await fetch('/api/auth/registration-csrf', { credentials: 'same-origin', cache: 'no-store' });
    if (!csrfResponse.ok) throw new Error('No se pudo preparar el registro. Inténtalo de nuevo.');
    const { csrf_token } = await csrfResponse.json();
    const response = await fetch('/api/auth/register', {
      method: 'POST', credentials: 'same-origin', cache: 'no-store',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf_token },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok || !result.success) {
      for (const input of fields) {
        const message = result.errors?.[payloadFields[input.id]];
        if (typeof message === 'string') {
          const error = document.getElementById(`${input.id}Error`);
          input.setCustomValidity(message);
          input.setAttribute('aria-invalid', 'true');
          error.textContent = message;
          error.hidden = false;
        }
      }
      showStatus(result.message || 'No se pudo crear la cuenta. Inténtalo de nuevo.');
      return;
    }
    form.reset();
    backButton.disabled = false;
    backButton.click();
    document.getElementById('userCode').value = payload.numero_unico.trim();
    document.getElementById('userPassword').focus();
    showStatus(result.message, 'success');
  } catch (_) {
    showStatus('No se pudo confirmar el registro. Comprueba tu conexión. Si ya enviaste tus datos, intenta iniciar sesión antes de repetir el registro.');
  } finally {
    // No conservar contraseñas tras el intento, tampoco en mensajes o almacenamiento local.
    document.getElementById('registerPassword').value = '';
    delete payload.password;
    submitting = false;
    submitButton.disabled = false;
    backButton.disabled = false;
    form.removeAttribute('aria-busy');
    submitButton.textContent = 'Crear cuenta';
  }
});

// El botón solo se habilita cuando el módulo y sus validaciones están cargados.
submitButton.disabled = false;

form.addEventListener('registration:reset-validation', () => {
  touched.clear();
  fields.forEach(input => {
    input.setCustomValidity('');
    input.removeAttribute('aria-invalid');
    const error = document.getElementById(`${input.id}Error`);
    error.textContent = '';
    error.hidden = true;
  });
});
