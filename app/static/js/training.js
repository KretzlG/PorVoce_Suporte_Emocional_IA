/**
 * Training Module JavaScript
 * Funcionalidades para o sistema de treinamento da IA
 */

const TrainingJS = {
    /**
     * Inicializar página de submissão
     */
    initSubmitPage() {
        console.log('Inicializando página de submissão de treinamento');
        
        // Alternar entre tipo de conteúdo
        this.setupContentTypeToggle();
        
        // Configurar upload de arquivo
        this.setupFileUpload();
        
        // Configurar submissão do formulário
        this.setupFormSubmission();
    },

    /**
     * Inicializar página de listagem
     */
    initListPage() {
        console.log('Inicializando página de listagem de treinamentos');
        
        // Configurar filtros
        this.setupFilters();
        
        // Configurar tooltips
        this.setupTooltips();
    },

    /**
     * Inicializar página de visualização
     */
    initViewPage() {
        console.log('Inicializando página de visualização de treinamento');
        
        // Configurar círculo de score
        this.setupScoreCircle();
        
        // Configurar tooltips
        this.setupTooltips();
    },

    /**
     * Configurar alternância entre tipos de conteúdo
     */
    setupContentTypeToggle() {
        const textRadio = document.getElementById('type_text');
        const fileRadio = document.getElementById('type_file');
        const textSection = document.getElementById('text_content_section');
        const fileSection = document.getElementById('file_upload_section');
        const contentField = document.getElementById('content');
        const fileField = document.getElementById('file');

        const toggleSections = () => {
            if (textRadio.checked) {
                textSection.style.display = 'block';
                fileSection.style.display = 'none';
                contentField.required = true;
                fileField.required = false;
            } else {
                textSection.style.display = 'none';
                fileSection.style.display = 'block';
                contentField.required = false;
                fileField.required = true;
            }
        };

        textRadio.addEventListener('change', toggleSections);
        fileRadio.addEventListener('change', toggleSections);
        
        // Inicializar estado
        toggleSections();
    },

    /**
     * Configurar upload de arquivo
     */
    setupFileUpload() {
        const fileInput = document.getElementById('file');
        const filePreview = document.getElementById('file_preview');
        const fileName = document.getElementById('file_name');
        const fileSize = document.getElementById('file_size');

        if (!fileInput) return;

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            
            if (file) {
                // Validar tipo de arquivo
                const allowedTypes = ['txt', 'pdf', 'doc', 'docx', 'odt'];
                const fileExtension = file.name.split('.').pop().toLowerCase();
                
                if (!allowedTypes.includes(fileExtension)) {
                    this.showAlert('Tipo de arquivo não permitido. Use: ' + allowedTypes.join(', '), 'error');
                    fileInput.value = '';
                    filePreview.style.display = 'none';
                    return;
                }
                
                // Validar tamanho (16MB)
                const maxSize = 16 * 1024 * 1024;
                if (file.size > maxSize) {
                    this.showAlert('Arquivo muito grande. Tamanho máximo: 16MB', 'error');
                    fileInput.value = '';
                    filePreview.style.display = 'none';
                    return;
                }
                
                // Mostrar prévia
                fileName.textContent = file.name;
                fileSize.textContent = `(${this.formatFileSize(file.size)})`;
                filePreview.style.display = 'block';
            } else {
                filePreview.style.display = 'none';
            }
        });
    },

    /**
     * Configurar submissão do formulário
     */
    setupFormSubmission() {
        const form = document.getElementById('trainingForm');
        const submitBtn = document.getElementById('submitBtn');
        const loadingModal = document.getElementById('loadingModal');
        const validationResult = document.getElementById('validation_result');

        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Validar formulário
            if (!this.validateForm(form)) {
                return;
            }
            
            // Mostrar loading
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Validando...';
            
            if (loadingModal) {
                const modal = new bootstrap.Modal(loadingModal);
                modal.show();
            }

            try {
                // Preparar dados
                const formData = new FormData(form);
                
                // Enviar requisição
                const response = await fetch('/training/submit', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (loadingModal) {
                    bootstrap.Modal.getInstance(loadingModal).hide();
                }
                
                if (result.success) {
                    this.showValidationResult(result.data, validationResult);
                    this.showAlert('Treinamento enviado com sucesso!', 'success');
                    
                    // Resetar formulário após sucesso
                    setTimeout(() => {
                        if (confirm('Deseja enviar outro treinamento?')) {
                            form.reset();
                            validationResult.style.display = 'none';
                            this.setupContentTypeToggle(); // Reconfigurar após reset
                        } else {
                            window.location.href = '/training';
                        }
                    }, 2000);
                } else {
                    this.showAlert(result.message || 'Erro ao enviar treinamento', 'error');
                }
                
            } catch (error) {
                console.error('Erro:', error);
                
                if (loadingModal) {
                    bootstrap.Modal.getInstance(loadingModal).hide();
                }
                
                this.showAlert('Erro de conexão. Tente novamente.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar para Validação';
            }
        });
    },

    /**
     * Mostrar resultado da validação
     */
    showValidationResult(data, container) {
        if (!container) return;
        
        const status = data.status;
        const score = Math.round(data.score * 100);
        const summary = data.validation_summary || '';
        
        let statusClass, statusIcon, statusText;
        
        if (status === 'approved') {
            statusClass = 'success';
            statusIcon = 'check-circle';
            statusText = 'Aprovado';
        } else {
            statusClass = 'danger';
            statusIcon = 'times-circle';
            statusText = 'Rejeitado';
        }
        
        container.innerHTML = `
            <div class="alert alert-${statusClass} mb-3">
                <i class="fas fa-${statusIcon} me-2"></i>
                <strong>${statusText}</strong> - Score: ${score}%
            </div>
            <div class="validation-summary">
                <h6>Detalhes da Validação:</h6>
                <pre class="small">${summary}</pre>
            </div>
        `;
        
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });
    },

    /**
     * Validar formulário
     */
    validateForm(form) {
        const dataType = form.querySelector('input[name="data_type"]:checked').value;
        const title = form.querySelector('#title').value.trim();
        
        if (!title) {
            this.showAlert('Título é obrigatório', 'error');
            return false;
        }
        
        if (dataType === 'text') {
            const content = form.querySelector('#content').value.trim();
            if (!content) {
                this.showAlert('Conteúdo é obrigatório', 'error');
                return false;
            }
            if (content.length < 50) {
                this.showAlert('Conteúdo deve ter pelo menos 50 caracteres', 'error');
                return false;
            }
        } else {
            const file = form.querySelector('#file').files[0];
            if (!file) {
                this.showAlert('Arquivo é obrigatório', 'error');
                return false;
            }
        }
        
        return true;
    },

    /**
     * Configurar filtros
     */
    setupFilters() {
        // Auto-submit do formulário de filtros
        const statusSelect = document.getElementById('status');
        if (statusSelect) {
            statusSelect.addEventListener('change', () => {
                statusSelect.closest('form').submit();
            });
        }
    },

    /**
     * Configurar tooltips
     */
    setupTooltips() {
        // Inicializar tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    /**
     * Configurar círculo de score
     */
    setupScoreCircle() {
        const progressCircles = document.querySelectorAll('.progress-circle[data-score]');
        
        progressCircles.forEach(circle => {
            const score = parseFloat(circle.dataset.score);
            const percentage = score * 360; // Converter para graus
            circle.style.setProperty('--progress', `${percentage}deg`);
        });
    },

    /**
     * Validar treinamento (função para admins)
     */
    async validateTraining(trainingId, action, notes = '') {
        try {
            const response = await fetch(`/training/${trainingId}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: action,
                    notes: notes
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(result.message, 'success');
                
                // Atualizar interface se necessário
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
                
                return true;
            } else {
                this.showAlert(result.message || 'Erro ao validar treinamento', 'error');
                return false;
            }
            
        } catch (error) {
            console.error('Erro:', error);
            this.showAlert('Erro de conexão. Tente novamente.', 'error');
            return false;
        }
    },

    /**
     * Mostrar alerta
     */
    showAlert(message, type = 'info') {
        // Remover alertas existentes
        const existingAlerts = document.querySelectorAll('.training-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Criar novo alerta
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show training-alert`;
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.style.minWidth = '300px';
        
        const icon = this.getAlertIcon(type);
        
        alertDiv.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    /**
     * Obter ícone do alerta
     */
    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-triangle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    /**
     * Formatar tamanho de arquivo
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Carregar estatísticas via API
     */
    async loadStats() {
        try {
            const response = await fetch('/training/api/stats');
            const stats = await response.json();
            
            // Atualizar números na interface
            this.updateStatNumbers(stats);
            
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    },

    /**
     * Atualizar números das estatísticas
     */
    updateStatNumbers(stats) {
        const elements = {
            'total': document.querySelector('.stat-total .stat-number'),
            'approved': document.querySelector('.stat-approved .stat-number'),
            'pending': document.querySelector('.stat-pending .stat-number'),
            'rejected': document.querySelector('.stat-rejected .stat-number')
        };
        
        Object.keys(elements).forEach(key => {
            if (elements[key] && stats[key] !== undefined) {
                this.animateNumber(elements[key], stats[key]);
            }
        });
    },

    /**
     * Animar números
     */
    animateNumber(element, targetValue) {
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 segundo
        const startTime = performance.now();
        
        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.round(startValue + (targetValue - startValue) * progress);
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    },

    /**
     * Inicializar componentes globais
     */
    init() {
        console.log('Training Module initialized');
        
        // Carregar estatísticas periodicamente
        this.loadStats();
        setInterval(() => this.loadStats(), 30000); // A cada 30 segundos
        
        // Configurar tooltips globais
        this.setupTooltips();
    }
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    TrainingJS.init();
});

// Exportar para uso global
window.TrainingJS = TrainingJS;
