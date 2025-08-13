document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('.auth-form');
  if (!form) return;
  form.addEventListener('submit', function(e) {
    const email = form.email.value.trim();
    const password = form.password.value.trim();
    if (!email || !password) {
      e.preventDefault();
      showError('Preencha todos os campos.');
    }
  });

  function showError(msg) {
    let flash = document.querySelector('.flash-messages');
    if (!flash) {
      flash = document.createElement('div');
      flash.className = 'flash-messages';
      form.prepend(flash);
    }
    flash.innerHTML = `<div class="alert alert-danger">${msg}</div>`;
  }
});
