// Por Você - Base JavaScript Functions

class PorVoceBase {
    constructor() {
        this.init();
    }

    init() {
        this.setupGlobalEvents();
        this.setupFormValidation();
        this.setupAlerts();
        this.setupTooltips();
    }

    setupGlobalEvents() {
        // Auto-dismiss alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.transition = 'opacity 0.5s ease';
                    alert.style.opacity = '0';
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.remove();
                        }
                    }, 500);
                }
            }, 5000);
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Loading states for buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn[type="submit"]') || e.target.closest('.btn[type="submit"]')) {
                const btn = e.target.matches('.btn') ? e.target : e.target.closest('.btn');
                this.setLoadingState(btn, true);
            }
        });
    }

    setupFormValidation() {
        // Basic form validation
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'Este campo é obrigatório');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });

        // Email validation
        const emailInputs = form.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            if (input.value && !this.isValidEmail(input.value)) {
                this.showFieldError(input, 'Email inválido');
                isValid = false;
            }
        });

        return isValid;
    }

    showFieldError(input, message) {
        this.clearFieldError(input);
        
        input.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
    }

    clearFieldError(input) {
        input.classList.remove('is-invalid');
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    setupAlerts() {
        // Setup alert system
        window.showAlert = (type, message, permanent = false) => {
            this.showAlert(type, message, permanent);
        };
    }

    showAlert(type, message, permanent = false) {
        const alertContainer = document.getElementById('alertContainer') || this.createAlertContainer();
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show ${permanent ? 'alert-permanent' : ''}`;
        alertDiv.setAttribute('role', 'alert');
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.appendChild(alertDiv);
        
        // Auto-remove if not permanent
        if (!permanent) {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.style.transition = 'opacity 0.5s ease';
                    alertDiv.style.opacity = '0';
                    setTimeout(() => {
                        if (alertDiv.parentNode) {
                            alertDiv.remove();
                        }
                    }, 500);
                }
            }, 5000);
        }
    }

    createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alertContainer';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    setLoadingState(button, loading) {
        if (loading) {
            button.disabled = true;
            button.setAttribute('data-original-text', button.innerHTML);
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
        } else {
            button.disabled = false;
            button.innerHTML = button.getAttribute('data-original-text') || button.innerHTML;
        }
    }

    // API Helper methods
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Utility methods
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        return new Date(date).toLocaleDateString('pt-BR', mergedOptions);
    }

    formatRelativeTime(date) {
        const now = new Date();
        const diffMs = now - new Date(date);
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Agora mesmo';
        if (diffMins < 60) return `${diffMins} minuto${diffMins > 1 ? 's' : ''} atrás`;
        if (diffHours < 24) return `${diffHours} hora${diffHours > 1 ? 's' : ''} atrás`;
        if (diffDays < 7) return `${diffDays} dia${diffDays > 1 ? 's' : ''} atrás`;
        
        return this.formatDate(date, { year: 'numeric', month: 'short', day: 'numeric' });
    }

    // Theme methods
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('porvoce-theme', theme);
    }

    getTheme() {
    return localStorage.getItem('porvoce-theme') || 'light';
    }

    initTheme() {
        const savedTheme = this.getTheme();
        this.setTheme(savedTheme);
    }
}

// Initialize base functionality when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.PorVoceBase = new PorVoceBase();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PorVoceBase;
}
