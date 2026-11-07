/* Alternancia visual; el envío del registro se gestiona en registration-form.mjs. */
(() => {
  const card = document.getElementById('authCard');
  const title = document.getElementById('authTitle');
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const loginLinks = document.getElementById('loginLinks');
  // Impedir el envío nativo (GET) incluso si el módulo de registro no carga.
  registerForm.addEventListener('submit', event => event.preventDefault());

  function showRegistration(show) {
    document.getElementById('authStatus').hidden = true;
    card.classList.toggle('is-register', show);
    loginForm.hidden = show;
    registerForm.hidden = !show;
    loginLinks.hidden = show;
    title.textContent = show ? 'Crear cuenta' : 'Sistema Académico';
    document.title = show ? 'Registro - Sistema Académico UNI' : 'Login - Sistema Académico UNI';
    // No conservar contraseñas en el formulario oculto.
    const hiddenForm = show ? loginForm : registerForm;
    hiddenForm.querySelectorAll('input[autocomplete$="-password"]').forEach(input => { input.value = ''; });
    registerForm.dispatchEvent(new Event('registration:reset-validation'));
    document.getElementById(show ? 'registerNames' : 'userCode').focus();
  }

  document.getElementById('showRegister').addEventListener('click', () => showRegistration(true));
  document.getElementById('showLogin').addEventListener('click', () => showRegistration(false));
})();
