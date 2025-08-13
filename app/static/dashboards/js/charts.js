/* ===============================================
   ForYou Dashboard - Chart Integration
   Integração com Chart.js para gráficos
   =============================================== */

class ForYouCharts {
	constructor() {
		this.charts = {};
		this.colors = {
			primary: '#be0049',
			secondary: '#ff348e',
			accent: '#ff97ca',
			light: '#ffffff',
			dark: '#770021'
		};
		this.init();
	}

	init() {
		// Verificar se Chart.js está disponível
		if (typeof Chart !== 'undefined') {
			this.setupDefaults();
			this.initializeCharts();
		} else {
			console.warn('Chart.js não encontrado. Carregando...');
			this.loadChartJS();
		}
	}

	loadChartJS() {
		const script = document.createElement('script');
		script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
		script.onload = () => {
			this.setupDefaults();
			this.initializeCharts();
		};
		document.head.appendChild(script);
	}

	setupDefaults() {
		Chart.defaults.font.family = '"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
		Chart.defaults.font.size = 12;
		Chart.defaults.color = '#6b7280';
		Chart.defaults.borderColor = 'rgba(190, 0, 73, 0.1)';
		Chart.defaults.backgroundColor = 'rgba(190, 0, 73, 0.05)';
	}

	initializeCharts() {
		// Gráfico de usuários por mês
		this.createUsersChart();
		// Gráfico de conversas por dia
		this.createChatsChart();
		// Gráfico de distribuição por risco
		this.createRiskChart();
		// Gráfico de voluntários ativos
		this.createVolunteersChart();
	}

	createUsersChart() {
		const canvas = document.getElementById('usersChart');
		if (!canvas) return;
		const ctx = canvas.getContext('2d');
		this.charts.users = new Chart(ctx, {
			type: 'line',
			data: {
				labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
				datasets: [{
					label: 'Novos Usuários',
					data: [12, 19, 8, 15, 28, 35],
					borderColor: this.colors.primary,
					backgroundColor: this.colors.primary + '20',
					tension: 0.4,
					fill: true,
					pointBackgroundColor: this.colors.primary,
					pointBorderColor: '#ffffff',
					pointBorderWidth: 2,
					pointRadius: 5
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						display: false
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						grid: {
							color: 'rgba(190, 0, 73, 0.1)'
						}
					},
					x: {
						grid: {
							display: false
						}
					}
				}
			}
		});
	}

	createChatsChart() {
		const canvas = document.getElementById('chatsChart');
		if (!canvas) return;
		const ctx = canvas.getContext('2d');
		this.charts.chats = new Chart(ctx, {
			type: 'bar',
			data: {
				labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
				datasets: [{
					label: 'Conversas',
					data: [45, 52, 38, 41, 58, 33, 28],
					backgroundColor: [
						this.colors.primary + '80',
						this.colors.secondary + '80',
						this.colors.accent + '80',
						this.colors.primary + '80',
						this.colors.secondary + '80',
						this.colors.accent + '80',
						this.colors.primary + '80'
					],
					borderColor: [
						this.colors.primary,
						this.colors.secondary,
						this.colors.accent,
						this.colors.primary,
						this.colors.secondary,
						this.colors.accent,
						this.colors.primary
					],
					borderWidth: 2,
					borderRadius: 6,
					borderSkipped: false
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						display: false
					}
				},
				scales: {
					y: {
						beginAtZero: true,
						grid: {
							color: 'rgba(190, 0, 73, 0.1)'
						}
					},
					x: {
						grid: {
							display: false
						}
					}
				}
			}
		});
	}

	createRiskChart() {
		const canvas = document.getElementById('riskChart');
		if (!canvas) return;
		const ctx = canvas.getContext('2d');
		this.charts.risk = new Chart(ctx, {
			type: 'doughnut',
			data: {
				labels: ['Baixo', 'Médio', 'Alto', 'Crítico'],
				datasets: [{
					data: [65, 25, 8, 2],
					backgroundColor: [
						'#10b981',
						'#f59e0b',
						this.colors.secondary,
						this.colors.primary
					],
					borderWidth: 0,
					cutout: '60%'
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						position: 'right',
						labels: {
							usePointStyle: true,
							padding: 20
						}
					}
				}
			}
		});
	}

	createVolunteersChart() {
		const canvas = document.getElementById('volunteersChart');
		if (!canvas) return;
		const ctx = canvas.getContext('2d');
		this.charts.volunteers = new Chart(ctx, {
			type: 'radar',
			data: {
				labels: ['Disponível', 'Ocupado', 'Ausente', 'Treinamento', 'Licença'],
				datasets: [{
					label: 'Status dos Voluntários',
					data: [15, 8, 3, 2, 1],
					borderColor: this.colors.primary,
					backgroundColor: this.colors.primary + '30',
					pointBackgroundColor: this.colors.primary,
					pointBorderColor: '#ffffff',
					pointBorderWidth: 2
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						display: false
					}
				},
				scales: {
					r: {
						beginAtZero: true,
						grid: {
							color: 'rgba(190, 0, 73, 0.1)'
						},
						angleLines: {
							color: 'rgba(190, 0, 73, 0.1)'
						}
					}
				}
			}
		});
	}

	// Método para atualizar dados dos gráficos
	updateChart(chartName, data) {
		if (this.charts[chartName]) {
			this.charts[chartName].data = data;
			this.charts[chartName].update('active');
		}
	}

	// Método para redimensionar gráficos
	resizeCharts() {
		Object.values(this.charts).forEach(chart => {
			chart.resize();
		});
	}

	// Método para destruir gráficos
	destroyCharts() {
		Object.values(this.charts).forEach(chart => {
			chart.destroy();
		});
		this.charts = {};
	}
}

// Inicializar gráficos quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
	// Aguardar um pouco para garantir que o dashboard base foi inicializado
	setTimeout(() => {
		window.forYouCharts = new ForYouCharts();
	}, 200);
});

// Redimensionar gráficos quando a janela for redimensionada
window.addEventListener('resize', () => {
	if (window.forYouCharts) {
		window.forYouCharts.resizeCharts();
	}
});

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
	module.exports = ForYouCharts;
}
// ...conteúdo original...
