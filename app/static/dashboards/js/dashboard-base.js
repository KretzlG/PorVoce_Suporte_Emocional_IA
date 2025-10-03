// ForYou Dashboard Base JS
// Animações, contadores e integrações comuns para todos os dashboards

// Função para animar contadores
function animateCounter(counter, target) {
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
}


// Detecta tipo de dashboard pela URL
function getDashboardType() {
	if (window.location.pathname.includes('/admin')) return 'admin';
	if (window.location.pathname.includes('/volunteer')) return 'volunteer';
	if (window.location.pathname.includes('/client')) return 'client';
	// fallback: tenta pelo body
	if (document.body.classList.contains('dashboard-admin')) return 'admin';
	if (document.body.classList.contains('dashboard-volunteer')) return 'volunteer';
	if (document.body.classList.contains('dashboard-client')) return 'client';
	return 'admin'; // padrão
}

// Função para atualizar dashboard dinamicamente
async function updateDashboard() {
	try {
		let endpoint = '/admin/api/dashboard-stats';
		const dashType = getDashboardType();
		if (dashType === 'volunteer') endpoint = '/volunteer/api/dashboard-stats';
		if (dashType === 'client') endpoint = '/api/dashboard-stats';
		const res = await fetch(endpoint);
		if (!res.ok) return;
		const data = await res.json();

		// ADMIN: lógica igual ao original
		if (dashType === 'admin' && data.stats) {
			document.querySelectorAll('[data-counter]').forEach(el => {
				const key = el.getAttribute('data-counter-key');
				if (key && data.stats[key] !== undefined) {
					animateCounter(el, data.stats[key]);
				}
			});
			if (window.usersChart && data.growth) {
				usersChart.data.labels = data.growth.labels;
				usersChart.data.datasets[0].data = data.growth.data;
				usersChart.update();
			}
			if (window.riskChart && data.risk_distribution) {
				riskChart.data.labels = Object.keys(data.risk_distribution);
				riskChart.data.datasets[0].data = Object.values(data.risk_distribution);
				riskChart.update();
			}
			if (data.recent_activities) {
				const tbody = document.querySelector('#recent-activities-tbody');
				if (tbody) {
					tbody.innerHTML = '';
					if (data.recent_activities.length === 0) {
						tbody.innerHTML = '<tr><td colspan="4">Nenhuma atividade recente.</td></tr>';
					} else {
						data.recent_activities.forEach(act => {
							tbody.innerHTML += `<tr>
								<td>${act.user_name}</td>
								<td>${act.action}</td>
								<td>${act.timestamp}</td>
								<td><span class="badge ${act.status_class}">${act.status_label}</span></td>
							</tr>`;
						});
					}
				}
			}
		}

		// VOLUNTÁRIO: atualizar counters e lista de atividades
		if (dashType === 'volunteer' && data.stats) {
			const stats = data.stats;
			const counters = document.querySelectorAll('[data-counter]');
			if (counters.length >= 2) {
				animateCounter(counters[0], stats.sessions || 0);
				animateCounter(counters[1], stats.users_helped || 0);
			}
			// Último atendimento (texto)
			if (counters.length >= 3) {
				counters[2].textContent = stats.last_session || 'N/A';
			}
			// Atividades recentes
			if (data.recent_activities) {
				const ul = document.querySelector('.card-body ul.list-group');
				if (ul) {
					ul.innerHTML = '';
					if (data.recent_activities.length === 0) {
						ul.innerHTML = '<li class="list-group-item text-muted">Nenhuma atividade recente.</li>';
					} else {
						data.recent_activities.forEach(act => {
							ul.innerHTML += `<li class="list-group-item">${act}</li>`;
						});
					}
				}
			}
		}

		// CLIENTE: atualizar counters e atividades recentes
		if (dashType === 'client' && data.user_stats) {
			const stats = data.user_stats;
			const counters = document.querySelectorAll('[data-counter]');
			if (counters.length >= 1) {
				animateCounter(counters[0], stats.total_chats || 0);
			}
			// Último acesso
			if (counters.length >= 4 && stats.last_activity) {
				counters[3].textContent = stats.last_activity;
			}
			// Atividades recentes
			if (data.recent_entries) {
				const list = document.querySelector('.card-body .list-group');
				if (list) {
					list.innerHTML = '';
					if (data.recent_entries.length === 0) {
						list.innerHTML = `<div class="list-group-item border-0 px-0 text-muted text-center py-4">
							<i class="fas fa-inbox fs-2 mb-2 d-block text-muted"></i>
							Nenhuma atividade recente.<br><small>Comece uma conversa para ver suas atividades aqui!</small>
						</div>`;
					} else {
						data.recent_entries.forEach(entry => {
							list.innerHTML += `<div class="list-group-item border-0 px-0">
								<div class="d-flex align-items-center">
									<i class="fas fa-circle text-info me-2" style="font-size: 0.5rem;"></i>
									<span>${entry.title || entry.text}</span>
								</div>
							</div>`;
						});
					}
				}
			}
		}
	} catch (e) {
		// erro silencioso
	}
}

document.addEventListener('DOMContentLoaded', function () {
	// Animação de fade-in para cards
	const fadeEls = document.querySelectorAll('.fade-in');
	fadeEls.forEach((el, i) => {
		setTimeout(() => {
			el.classList.add('show');
		}, 100 + i * 120);
	});

	// Inicializar dashboard dinâmico
	updateDashboard();
	setInterval(updateDashboard, 15000); // Atualiza a cada 15s

	// Sidebar toggle moderno
	const sidebar = document.getElementById('sidebar');
	const sidebarToggle = document.getElementById('sidebar-toggle');
	const sidebarToggleClose = document.getElementById('sidebar-toggle-close');
	function toggleSidebar() {
		if (sidebar) sidebar.classList.toggle('collapsed');
	}
	if (sidebarToggle) {
		sidebarToggle.addEventListener('click', toggleSidebar);
	}
	if (sidebarToggleClose) {
		sidebarToggleClose.addEventListener('click', toggleSidebar);
	}
	// Esconde sidebar ao clicar fora em telas pequenas
	document.addEventListener('click', function(e) {
		if (window.innerWidth < 992 && sidebar && !sidebar.classList.contains('collapsed')) {
			if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
				sidebar.classList.add('collapsed');
			}
		}
	});
});
