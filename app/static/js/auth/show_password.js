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

// Adiciona validação para a página de registro
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (!form) return;
    
    // Verifica se é a página de registro (tem campos de radio)
    const isRegisterPage = document.querySelector('input[name="user_type"]') !== null;
    
    if (isRegisterPage) {
        form.addEventListener('submit', function(event) {
            const senha1 = document.querySelector('input[name="password"]');
            const senha2 = document.querySelector('input[name="confirm_password"]');
            const userType = document.querySelector('input[name="user_type"]:checked');
            const terms = document.getElementById('terms');
            const firstName = document.querySelector('input[name="first_name"]');
            const email = document.querySelector('input[name="email"]');
            
            let hasError = false;
            
            // Remove mensagens de erro anteriores
            const existingErrors = document.querySelectorAll('.client-error');
            existingErrors.forEach(error => error.remove());
            
            // Validação do nome
            if (!firstName.value.trim() || firstName.value.trim().length < 2) {
                showFieldError(firstName, 'Nome deve ter pelo menos 2 caracteres');
                hasError = true;
            }
            
            // Validação do email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email.value.trim() || !emailRegex.test(email.value.trim())) {
                showFieldError(email, 'Email inválido');
                hasError = true;
            }
            
            // Validação das senhas
            if (!senha1.value || senha1.value.length < 6) {
                showFieldError(senha1, 'A senha deve ter pelo menos 6 caracteres');
                hasError = true;
            }
            
            if (senha1.value !== senha2.value) {
                showFieldError(senha2, 'As senhas não coincidem');
                hasError = true;
            }
            
            // Validação do tipo de usuário
            if (!userType) {
                const radioGroup = document.querySelector('.radio-group');
                showGroupError(radioGroup, 'Por favor, selecione se você é paciente ou profissional');
                hasError = true;
            }
            
            // Validação dos termos
            if (!terms.checked) {
                const checkboxContainer = document.querySelector('.checkbox-container');
                showGroupError(checkboxContainer, 'Por favor, aceite os termos e condições de serviço');
                hasError = true;
            }
            
            if (hasError) {
                event.preventDefault();
            }
        });
    }
    
    function showFieldError(field, message) {
        const container = field.closest('.input-container');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'client-error';
        errorDiv.style.color = '#e51b61';
        errorDiv.style.fontSize = '12px';
        errorDiv.style.marginTop = '5px';
        errorDiv.textContent = message;
        container.appendChild(errorDiv);
        
        field.style.borderColor = '#e51b61';
        field.style.backgroundColor = '#ffebee';
    }
    
    function showGroupError(group, message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'client-error';
        errorDiv.style.color = '#e51b61';
        errorDiv.style.fontSize = '12px';
        errorDiv.style.marginTop = '5px';
        errorDiv.style.textAlign = 'center';
        errorDiv.textContent = message;
        group.appendChild(errorDiv);
    }
    
    // Limpar erros quando o usuário digitar
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            this.style.borderColor = '';
            this.style.backgroundColor = '';
            const container = this.closest('.input-container');
            if (container) {
                const error = container.querySelector('.client-error');
                if (error) error.remove();
            }
        });
        
        input.addEventListener('change', function() {
            const group = this.closest('.radio-group, .checkbox-container');
            if (group) {
                const error = group.querySelector('.client-error');
                if (error) error.remove();
            }
        });
    });
});