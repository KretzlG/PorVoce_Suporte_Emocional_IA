// index.js - Efeitos modernos e profissionais para a tela principal

document.addEventListener('DOMContentLoaded', function () {
    // Animação de fade-in sequencial nos cards de features e steps
    function animateSequential(selector, delayBase = 200) {
        const items = document.querySelectorAll(selector);
        items.forEach((el, i) => {
            el.style.opacity = 0;
            setTimeout(() => {
                el.style.transition = 'opacity 0.7s cubic-bezier(.4,0,.2,1)';
                el.style.opacity = 1;
            }, delayBase + i * 180);
        });
    }
    animateSequential('.modern-feature-card');
    animateSequential('.modern-step');

    // Efeito hover sutil no logo
    const logo = document.querySelector('.hero-logo');
    if (logo) {
        logo.addEventListener('mouseenter', () => {
            logo.style.transform = 'scale(1.08) rotate(-3deg)';
            logo.style.boxShadow = '0 16px 40px rgba(82,199,195,0.22)';
        });
        logo.addEventListener('mouseleave', () => {
            logo.style.transform = '';
            logo.style.boxShadow = '0 8px 32px rgba(82,199,195,0.18)';
        });
    }

    // Botão CTA: efeito de clique
    const ctaBtns = document.querySelectorAll('.btn-primary-custom, .btn-secondary-custom, .modern-cta-btn');
    ctaBtns.forEach(btn => {
        btn.addEventListener('mousedown', () => {
            btn.style.transform = 'scale(0.96)';
        });
        btn.addEventListener('mouseup', () => {
            btn.style.transform = '';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
        });
    });

    // Animação do header/navbar ao rolar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        function onScroll() {
            if (window.scrollY > 10) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
        window.addEventListener('scroll', onScroll);
        onScroll(); // inicializa estado
    }
});
