document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('.auth-form');
  if (!form) return;
  form.addEventListener('submit', function(e) {
    const username = form.username.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value.trim();
    const confirm = form.confirm_password.value.trim();
    if (!username || !email || !password || !confirm) {
      e.preventDefault();
      showError('Preencha todos os campos.');
      return;
    }
    if (password !== confirm) {
      e.preventDefault();
      showError('As senhas não coincidem.');
      return;
    }
    if (password.length < 6) {
      e.preventDefault();
      showError('A senha deve ter pelo menos 6 caracteres.');
      return;
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
