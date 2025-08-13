// ForYou Dashboard Base JS
// Animações, contadores e integrações comuns para todos os dashboards

// Animação de fade-in para cards
document.addEventListener('DOMContentLoaded', function () {
	const fadeEls = document.querySelectorAll('.fade-in');
	fadeEls.forEach((el, i) => {
		setTimeout(() => {
			el.classList.add('show');
		}, 100 + i * 120);
	});

	// Contadores animados
	const counters = document.querySelectorAll('[data-counter]');
	counters.forEach(counter => {
		const target = parseFloat(counter.getAttribute('data-counter'));
		let current = 0;
		let increment = target / 40;
		if (target < 10) increment = 0.1;
		const update = () => {
			current += increment;
			if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
				counter.textContent = target;
			} else {
				counter.textContent = Math.round(current * 10) / 10;
				requestAnimationFrame(update);
			}
		};
		update();
	});
});

// Exemplo de integração: abrir/fechar sidebar
document.addEventListener('DOMContentLoaded', function () {
	const sidebarToggle = document.getElementById('sidebar-toggle');
	const sidebar = document.querySelector('.sidebar');
	if (sidebarToggle && sidebar) {
		sidebarToggle.addEventListener('click', function () {
			sidebar.classList.toggle('collapsed');
		});
	}
});
// ...conteúdo original...
