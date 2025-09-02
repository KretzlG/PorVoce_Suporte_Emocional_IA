/**
 * Training Module JavaScript - Chat Style Layout
 * Funcionalidades para o sistema de treinamento da IA com layout inspirado no chat
 */

const TrainingJS = {
    /**
     * Inicializar módulo de treinamento
     */
    init() {
        console.log('Training Module initialized with chat-style layout');
        
        // Configurar navegação da sidebar
        this.setupSidebarNavigation();
        
        // Configurar responsividade
        this.setupResponsive();
        
        // Configurar tooltips globais
        this.setupTooltips();
        
        // Configurar navegação do histórico do browser
        this.setupBrowserNavigation();
        
        // Carregar estatísticas periodicamente
        this.loadStats();
        setInterval(() => this.loadStats(), 30000); // A cada 30 segundos
        
        // Detectar página atual e inicializar funcionalidades específicas
        this.detectPageAndInit();
    },

    /**
     * Configurar navegação do histórico do browser
     */
    setupBrowserNavigation() {
        // Listener para navegação com botões voltar/avançar do browser
        window.addEventListener('popstate', (event) => {
            // Recarregar o conteúdo quando o usuário usar os botões do browser
            const currentUrl = window.location.pathname + window.location.search;
            this.loadContentFromUrl(currentUrl);
        });
    },

    /**
     * Carregar conteúdo a partir de uma URL
     */
    async loadContentFromUrl(url) {
        try {
            // Atualizar item ativo baseado na URL
            this.updateActiveMenuItemFromUrl(url);
            
            // Carregar conteúdo
            await this.loadContent(url, null, false); // false = não atualizar history
            
        } catch (error) {
            console.error('Erro ao carregar conteúdo da URL:', error);
        }
    },

    /**
     * Atualizar item ativo baseado na URL
     */
    updateActiveMenuItemFromUrl(url) {
        const menuItems = document.querySelectorAll('.menu-item');
        
        menuItems.forEach(item => {
            item.classList.remove('active');
            
            const itemHref = item.getAttribute('href');
            if (itemHref && url.startsWith(itemHref)) {
                item.classList.add('active');
            }
        });
    },

    /**
     * Detectar página atual e inicializar funcionalidades específicas
     */
    detectPageAndInit() {
        const currentPath = window.location.pathname;
        
        // Marcar o item correto como ativo baseado na URL atual
        this.updateActiveMenuItemFromUrl(currentPath);
        
        if (currentPath.includes('/submit')) {
            this.initSubmitPage();
        } else if (currentPath.includes('/list') || currentPath.includes('/training') && !currentPath.includes('/submit')) {
            this.initListPage();
        } else if (currentPath.includes('/view/')) {
            this.initViewPage();
        }
    },

    /**
     * Configurar navegação da sidebar (similar ao chat)
     */
    setupSidebarNavigation() {
        const sidebarItems = document.querySelectorAll('.menu-item');
        
        // Adicionar efeito hover e clique aos itens do menu
        sidebarItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(5px)';
            });
            
            item.addEventListener('mouseleave', function() {
                if (!this.classList.contains('active')) {
                    this.style.transform = 'translateX(0)';
                }
            });

            // Interceptar cliques para carregamento AJAX
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const url = item.getAttribute('href');
                this.loadContent(url, item);
            });
        });

        // Configurar botão de voltar ao home
        const backBtn = document.getElementById('back-to-home');
        if (backBtn) {
            backBtn.addEventListener('click', function() {
                window.location.href = '/dashboard';
            });
        }
    },

    /**
     * Carregar conteúdo via AJAX
     */
    async loadContent(url, clickedItem, updateHistory = true) {
        try {
            // Mostrar loading
            this.showLoading();
            
            // Atualizar item ativo
            if (clickedItem) {
                this.updateActiveMenuItem(clickedItem);
            }
            
            // Fazer requisição AJAX
            const response = await fetch(url + (url.includes('?') ? '&' : '?') + 'ajax=1', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const html = await response.text();
            
            // Atualizar conteúdo
            const contentDiv = document.getElementById('training-content');
            if (contentDiv) {
                contentDiv.innerHTML = html;
            }
            
            // Atualizar URL sem recarregar a página (apenas se updateHistory for true)
            if (updateHistory) {
                window.history.pushState({}, '', url);
            }
            
            // Reconfigurar componentes após carregamento
            this.reinitializeComponents();
            
            // Esconder loading
            this.hideLoading();

        } catch (error) {
            console.error('Erro ao carregar conteúdo:', error);
            this.hideLoading();
            this.showAlert('Erro ao carregar conteúdo. Tente novamente.', 'error');
        }
    },    /**
     * Atualizar item ativo do menu
     */
    updateActiveMenuItem(activeItem) {
        // Remover classe active de todos os itens
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Adicionar classe active ao item clicado
        if (activeItem) {
            activeItem.classList.add('active');
        }
    },

    /**
     * Mostrar loading
     */
    showLoading() {
        const contentDiv = document.getElementById('training-content');
        if (contentDiv) {
            contentDiv.innerHTML = `
                <div class="loading-container" style="
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 400px;
                    flex-direction: column;
                    gap: 20px;
                ">
                    <div class="loading-spinner" style="
                        width: 50px;
                        height: 50px;
                        border: 4px solid rgba(102, 126, 234, 0.3);
                        border-top: 4px solid #667eea;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    "></div>
                    <p style="color: #6b7280; font-size: 16px;">Carregando...</p>
                </div>
            `;
        }
    },

    /**
     * Esconder loading
     */
    hideLoading() {
        const loadingContainer = document.querySelector('.loading-container');
        if (loadingContainer) {
            loadingContainer.remove();
        }
    },

    /**
     * Reinicializar componentes após carregamento AJAX
     */
    reinitializeComponents() {
        // Detectar qual página foi carregada e inicializar funcionalidades específicas
        const currentPath = window.location.pathname;
        
        if (currentPath.includes('/submit')) {
            this.initSubmitPage();
        } else if (currentPath.includes('/list') || currentPath.includes('/training') && !currentPath.includes('/submit')) {
            this.initListPage();
        } else if (currentPath.includes('/view/')) {
            this.initViewPage();
        }
        
        // Reconfigurar tooltips
        this.setupTooltips();
        
        // Reconfigurar outros componentes conforme necessário
        this.setupScoreCircle();
        
        // Interceptar links dentro do conteúdo carregado
        this.setupContentLinks();
    },

    /**
     * Configurar links dentro do conteúdo para navegação AJAX
     */
    setupContentLinks() {
        const contentDiv = document.getElementById('training-content');
        if (!contentDiv) return;
        
        // Interceptar links de treinamento dentro do conteúdo
        const trainingLinks = contentDiv.querySelectorAll('a[href^="/training"]');
        trainingLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const url = link.getAttribute('href');
                this.loadContent(url, null);
            });
        });
        
        // Interceptar links com data-ajax-link
        const ajaxLinks = contentDiv.querySelectorAll('a[data-ajax-link="true"]');
        ajaxLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const url = link.getAttribute('href');
                this.loadContent(url, null);
            });
        });
        
        // Interceptar formulários de paginação
        const paginationForms = contentDiv.querySelectorAll('form[action*="/training"]');
        paginationForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const url = form.action + '?' + new URLSearchParams(formData).toString();
                this.loadContent(url, null);
            });
        });
        
        // Interceptar botões de ação dentro do conteúdo
        const actionButtons = contentDiv.querySelectorAll('[data-training-action]');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const action = button.dataset.trainingAction;
                const trainingId = button.dataset.trainingId;
                
                if (action === 'view') {
                    this.loadContent(`/training/${trainingId}`, null);
                } else if (action === 'approve' || action === 'reject') {
                    this.handleValidationAction(trainingId, action, button);
                }
            });
        });
    },

    /**
     * Configurar responsividade (similar ao chat)
     */
    setupResponsive() {
        // Detectar dispositivos móveis
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            this.setupMobileNavigation();
        }
        
        // Reconfigurar no redimensionamento
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768 && !this.mobileSetup) {
                this.setupMobileNavigation();
            } else if (window.innerWidth > 768 && this.mobileSetup) {
                this.removeMobileNavigation();
            }
        });
    },

    /**
     * Configurar navegação mobile
     */
    setupMobileNavigation() {
        this.mobileSetup = true;
        const sidebar = document.querySelector('.training-sidebar');
        
        if (sidebar) {
            // Adicionar overlay
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 99;
                display: none;
            `;
            document.body.appendChild(overlay);
            
            // Adicionar botão toggle mobile
            this.addMobileToggle();
            
            // Configurar eventos
            overlay.addEventListener('click', () => {
                this.closeMobileSidebar();
            });
        }
    },

    /**
     * Adicionar botão toggle mobile
     */
    addMobileToggle() {
        const header = document.querySelector('.training-header');
        if (header && !document.getElementById('mobile-menu-toggle')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.id = 'mobile-menu-toggle';
            toggleBtn.className = 'mobile-menu-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            toggleBtn.style.cssText = `
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 8px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                z-index: 101;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            `;
            
            toggleBtn.addEventListener('click', () => {
                this.toggleMobileSidebar();
            });
            
            header.style.position = 'relative';
            header.appendChild(toggleBtn);
        }
    },

    /**
     * Toggle sidebar mobile
     */
    toggleMobileSidebar() {
        const sidebar = document.querySelector('.training-sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar.classList.contains('open')) {
            this.closeMobileSidebar();
        } else {
            sidebar.classList.add('open');
            overlay.style.display = 'block';
        }
    },

    /**
     * Fechar sidebar mobile
     */
    closeMobileSidebar() {
        const sidebar = document.querySelector('.training-sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        sidebar.classList.remove('open');
        overlay.style.display = 'none';
    },

    /**
     * Remover navegação mobile
     */
    removeMobileNavigation() {
        this.mobileSetup = false;
        const overlay = document.querySelector('.sidebar-overlay');
        const toggleBtn = document.getElementById('mobile-menu-toggle');
        
        if (overlay) overlay.remove();
        if (toggleBtn) toggleBtn.remove();
    },

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

        // Verificar se todos os elementos existem
        if (!textRadio || !fileRadio || !textSection || !fileSection || !contentField || !fileField) {
            console.log('Alguns elementos do formulário não foram encontrados, pulando configuração');
            return;
        }

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
                            // Carregar a página de lista via AJAX
                            this.loadContent('/training/list', null);
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
            const response = await fetch(`/training/validate/${trainingId}`, {
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
     * Mostrar alerta (estilo chat)
     */
    showAlert(message, type = 'info') {
        // Remover alertas existentes
        const existingAlerts = document.querySelectorAll('.training-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Criar novo alerta
        const alertDiv = document.createElement('div');
        alertDiv.className = `training-alert alert-${type}`;
        alertDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            padding: 15px 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideInRight 0.3s ease;
            cursor: pointer;
        `;
        
        // Cores baseadas no tipo
        const colors = {
            'success': 'background: rgba(16, 185, 129, 0.9); color: white;',
            'error': 'background: rgba(239, 68, 68, 0.9); color: white;',
            'danger': 'background: rgba(239, 68, 68, 0.9); color: white;',
            'warning': 'background: rgba(245, 158, 11, 0.9); color: white;',
            'info': 'background: rgba(59, 130, 246, 0.9); color: white;'
        };
        
        alertDiv.style.cssText += colors[type] || colors['info'];
        
        const icon = this.getAlertIcon(type);
        
        alertDiv.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span style="flex: 1;">${message}</span>
            <i class="fas fa-times" style="cursor: pointer; opacity: 0.7;"></i>
        `;
        
        // Adicionar evento de fechar
        alertDiv.addEventListener('click', () => alertDiv.remove());
        
        document.body.appendChild(alertDiv);
        
        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => alertDiv.remove(), 300);
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
     * Gerenciar ações de validação (aprovar/rejeitar)
     */
    async handleValidationAction(trainingId, action, button) {
        const actionText = action === 'approve' ? 'aprovar' : 'rejeitar';
        
        if (!confirm(`Tem certeza que deseja ${actionText} este treinamento?`)) {
            return;
        }
        
        let notes = '';
        if (action === 'reject') {
            notes = prompt('Digite uma nota explicando o motivo da rejeição (obrigatório):');
            if (!notes || notes.trim() === '') {
                this.showAlert('Nota é obrigatória para rejeição.', 'warning');
                return;
            }
        }
        
        // Desabilitar botão durante a requisição
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';
        
        try {
            const response = await this.validateTraining(trainingId, action, notes);
            
            if (response) {
                // Recarregar a página atual para mostrar as mudanças
                const currentUrl = window.location.pathname + window.location.search;
                await this.loadContent(currentUrl, null, false);
            }
            
        } catch (error) {
            console.error('Erro na validação:', error);
            this.showAlert('Erro ao processar validação. Tente novamente.', 'error');
        } finally {
            button.disabled = false;
            button.innerHTML = originalText;
        }
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
     * Adicionar animações CSS necessárias
     */
    addAnimationStyles() {
        if (!document.getElementById('training-animations')) {
            const style = document.createElement('style');
            style.id = 'training-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from {
                        opacity: 0;
                        transform: translateX(100%);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
                
                @keyframes slideOutRight {
                    from {
                        opacity: 1;
                        transform: translateX(0);
                    }
                    to {
                        opacity: 0;
                        transform: translateX(100%);
                    }
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .training-sidebar.open {
                    left: 0 !important;
                }
                
                .sidebar-overlay {
                    transition: opacity 0.3s ease;
                }
                
                .training-content {
                    animation: fadeIn 0.3s ease;
                }
            `;
            document.head.appendChild(style);
        }
    }
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    TrainingJS.addAnimationStyles();
    TrainingJS.init();
});

// Exportar para uso global
window.TrainingJS = TrainingJS;
