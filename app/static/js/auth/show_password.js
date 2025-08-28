function mostrarSenha(idInput, idBotao) {
    var inputPass = document.getElementById(idInput);
    var btnShowPass = document.getElementById(idBotao);

    if (inputPass.type === 'password') {
        inputPass.type = 'text';
        btnShowPass.classList.replace('bi-eye-fill', 'bi-eye-slash-fill');
    } else {
        inputPass.type = 'password';
        btnShowPass.classList.replace('bi-eye-slash-fill', 'bi-eye-fill');
    }
}

document.querySelector('form').addEventListener('submit', function(event) {
    const senha1 = document.getElementById('senha1').value;
    const senha2 = document.getElementById('senha2').value;
    const msgErro = document.getElementById('msg-erro');

    if (senha1 !== senha2) {
      event.preventDefault(); // impede o envio do form
      msgErro.textContent = 'As senhas não coincidem. Por favor, verifique.';
      msgErro.style.display = 'block';
    } else {
      msgErro.style.display = 'none'; // esconde a mensagem caso as senhas estejam iguais
    }
});