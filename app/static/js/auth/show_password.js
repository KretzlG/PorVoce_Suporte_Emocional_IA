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

// Adiciona validação apenas se estivermos na página de registro
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (!form) return;
    
    // Verifica se é a página de registro (tem campos de radio)
    const isRegisterPage = document.querySelector('input[name="user_type"]') !== null;
    
    if (isRegisterPage) {
        form.addEventListener('submit', function(event) {
            const msgErro = document.getElementById('msg-erro');
            const userType = document.querySelector('input[name="user_type"]:checked');
            const terms = document.getElementById('terms');
            
            // Limpa mensagens anteriores
            msgErro.style.display = 'none';
            msgErro.textContent = '';
            
            // Valida se um tipo de usuário foi selecionado
            if (!userType) {
                event.preventDefault();
                msgErro.textContent = 'Por favor, selecione se você é paciente ou profissional.';
                msgErro.style.display = 'block';
                return;
            }
            
            // Valida se os termos foram aceitos
            if (!terms.checked) {
                event.preventDefault();
                msgErro.textContent = 'Por favor, aceite os termos e condições de serviço.';
                msgErro.style.display = 'block';
                return;
            }
        });
    }
});