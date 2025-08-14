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
