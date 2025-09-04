document.addEventListener('DOMContentLoaded', function() {
    // Exemplo: animação de entrada do container
    const container = document.querySelector('.service-intake-container');
    if (container) {
        container.style.opacity = 0;
        container.style.transform = 'translateY(30px)';
        setTimeout(() => {
            container.style.transition = 'opacity 0.6s, transform 0.6s';
            container.style.opacity = 1;
            container.style.transform = 'translateY(0)';
        }, 100);
    }
    // Exemplo: feedback visual ao clicar nos botões
    document.querySelectorAll('.intake-actions .btn').forEach(btn => {
        btn.addEventListener('mousedown', function() {
            btn.classList.add('active-btn');
        });
        btn.addEventListener('mouseup', function() {
            btn.classList.remove('active-btn');
        });
        btn.addEventListener('mouseleave', function() {
            btn.classList.remove('active-btn');
        });
    });
});
