// Edición local únicamente: este módulo no envía ni guarda datos del perfil.
import { ageFromCedula } from './profile-age.mjs';
(() => {
  'use strict';
  const form = document.getElementById('perfil-form');
  const editButton = document.getElementById('perfil-editar');
  const department = document.getElementById('perfil-departamento');
  const municipality = document.getElementById('perfil-municipio');
  const municipalities = JSON.parse(document.getElementById('perfil-municipios-data').textContent);
  const municipalityOptions = document.getElementById('perfil-municipio-options');
  const identity = document.getElementById('perfil-cedula');
  const age = document.getElementById('perfil-edad');
  const ageHelp = document.getElementById('perfil-edad-help');
  const recordedBirthDate = document.getElementById('perfil-nacimiento').value;

  const updateAge = () => {
    const result = ageFromCedula(identity.value, undefined, recordedBirthDate);
    age.value = result === null ? '' : String(result.age);
    ageHelp.textContent = result === null
      ? 'Completa una cédula con fecha válida para calcular la edad.'
      : `Calculada a partir de la cédula.${result.inferredCentury ? ` Año de nacimiento interpretado: ${result.year}.` : ''}`;
  };
  identity.addEventListener('input', updateAge);
  updateAge();

  form.addEventListener('submit', (event) => event.preventDefault());
  editButton.addEventListener('click', () => {
    document.body.classList.replace('mode-reading', 'mode-editing');
    form.querySelectorAll('[data-profile-editable]').forEach((field) => {
      if (field instanceof HTMLSelectElement) {
        field.disabled = false;
      } else {
        field.readOnly = false;
      }
    });
    editButton.querySelector('span').textContent = 'Edición habilitada';
    editButton.disabled = true;
    document.getElementById('perfil-nombres').focus();
  });

  const updateMunicipalityOptions = () => {
    municipalityOptions.replaceChildren();
    municipalities.filter((item) => !department.value || String(item.id_departamento) === department.value)
      .forEach((item) => municipalityOptions.append(new Option(item.nombre, item.nombre)));
  };
  department.addEventListener('change', () => {
    municipality.value = '';
    updateMunicipalityOptions();
  });
  updateMunicipalityOptions();

  const photoInput = document.getElementById('perfil-foto');
  const photoStatus = document.getElementById('perfil-foto-status');
  document.getElementById('perfil-cambiar-foto').addEventListener('click', () => photoInput.click());
  photoInput.addEventListener('change', () => {
    const file = photoInput.files[0];
    if (!file) return;
    photoStatus.hidden = false;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
      photoStatus.textContent = 'Selecciona una imagen JPG, PNG o WebP de hasta 5 MB.';
      photoInput.value = '';
      return;
    }
    const url = URL.createObjectURL(file);
    const preview = new Image();
    preview.alt = 'Vista previa de tu foto de perfil';
    preview.onload = () => {
      document.querySelector('.perfil-avatar-circle').replaceChildren(preview);
      URL.revokeObjectURL(url);
      photoStatus.textContent = 'Vista previa local. La fotografía aún no se guarda.';
    };
    preview.onerror = () => {
      URL.revokeObjectURL(url);
      photoInput.value = '';
      photoStatus.textContent = 'No se pudo abrir la imagen seleccionada.';
    };
    preview.src = url;
  });
})();
