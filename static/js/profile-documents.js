// Selección temporal en memoria. No envía archivos ni utiliza almacenamiento persistente.
(() => {
  'use strict';
  const tabs = Array.from(document.querySelectorAll('.perfil-view-tab'));
  const editButton = document.getElementById('perfil-editar');
  const selectTab = (selected) => {
    tabs.forEach((tab) => {
      const active = tab === selected;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
    });
    editButton.hidden = selected.id !== 'perfil-tab-personal';
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', (event) => {
      let next;
      if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'ArrowLeft') next = tabs[(index + tabs.length - 1) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (!next) return;
      event.preventDefault();
      selectTab(next);
      next.focus();
    });
  });

  const allowedExtensions = new Set(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'webp']);
  const maxFileBytes = 10 * 1024 * 1024;
  const maxFiles = 10;
  const formatSize = (size) => size < 1024 * 1024
    ? `${Math.max(1, Math.ceil(size / 1024))} KB` : `${(size / (1024 * 1024)).toFixed(1)} MB`;

  document.querySelectorAll('[data-document-category]').forEach((card) => {
    const input = card.querySelector('input[type="file"]');
    const addButton = card.querySelector('.perfil-document-add');
    const list = card.querySelector('.perfil-document-list');
    const count = card.querySelector('.perfil-document-count');
    const error = card.querySelector('.perfil-document-error');
    const files = new Map();

    const render = () => {
      list.replaceChildren();
      list.hidden = files.size === 0;
      count.textContent = files.size === 0 ? 'Sin archivos seleccionados.'
        : `${files.size} ${files.size === 1 ? 'archivo seleccionado' : 'archivos seleccionados'}.`;
      files.forEach((file, key) => {
        const item = document.createElement('li');
        const details = document.createElement('span');
        details.className = 'perfil-document-details';
        const name = document.createElement('span');
        name.className = 'perfil-document-name';
        name.textContent = file.name;
        const size = document.createElement('small');
        size.textContent = formatSize(file.size);
        details.append(name, size);
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'perfil-document-remove';
        remove.textContent = 'Quitar';
        remove.setAttribute('aria-label', `Quitar ${file.name}`);
        remove.addEventListener('click', () => {
          files.delete(key);
          error.hidden = true;
          render();
          addButton.focus();
        });
        item.append(details, remove);
        list.append(item);
      });
    };

    addButton.addEventListener('click', () => input.click());
    input.addEventListener('change', () => {
      if (!input.files.length) return;
      const errors = [];
      for (const file of input.files) {
        const extension = file.name.split('.').pop().toLowerCase();
        if (!allowedExtensions.has(extension)) {
          errors.push(`${file.name}: formato no admitido.`);
          continue;
        }
        if (file.size === 0 || file.size > maxFileBytes) {
          errors.push(`${file.name}: el archivo está vacío o supera los 10 MB.`);
          continue;
        }
        const key = JSON.stringify([file.name, file.size, file.lastModified, file.type]);
        if (files.has(key)) continue;
        if (files.size >= maxFiles) {
          errors.push('Puedes seleccionar hasta 10 archivos en esta categoría.');
          break;
        }
        files.set(key, file);
      }
      input.value = '';
      error.textContent = errors.join(' ');
      error.hidden = errors.length === 0;
      render();
    });
  });
})();
