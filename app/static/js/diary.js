// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Diary.js carregado');
    initializeDiary();
});

// Estado da aplicação
const DiaryState = {
    currentPage: 1,
    totalPages: 1,
    currentFilters: {
        period: 30,
        mood: 'all'
    },
    isLoading: false,
    entries: []
};

// Inicialização principal
function initializeDiary() {
    console.log('📱 Inicializando diário...');
    
    // Event listeners
    setupEventListeners();
    
    // Carregar dados iniciais
    loadEntries();
    loadInsights();
    
    console.log('✅ Diário inicializado');
}

// Configurar event listeners
function setupEventListeners() {
    // Botões do header
    const backBtn = document.getElementById('back-to-home');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.location.href = DASHBOARD_URL || '/';
        });
    }

    const newEntryBtn = document.getElementById('new-entry-btn');
    const toggleFormBtn = document.getElementById('toggle-form');
    
    [newEntryBtn, toggleFormBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', toggleEntryForm);
        }
    });

    // Formulário
    const diaryForm = document.getElementById('diary-form');
    if (diaryForm) {
        diaryForm.addEventListener('submit', handleFormSubmit);
    }

    // Botões do formulário
    const cancelBtn = document.getElementById('cancel-entry');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            toggleEntryForm(false);
            clearForm();
        });
    }

    // Contador de caracteres
    const contentTextarea = document.getElementById('content');
    if (contentTextarea) {
        contentTextarea.addEventListener('input', updateCharCounter);
    }

    // Filtros
    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }

    // Modal
    setupModalListeners();

    console.log('🔗 Event listeners configurados');
}

// Modal listeners
function setupModalListeners() {
    const modal = document.getElementById('delete-modal');
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    const confirmDeleteBtn = document.getElementById('confirm-delete');

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            entryToDelete = null; // Reset da variável
        });
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', confirmDelete);
    }

    // Fechar modal ao clicar fora
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
                entryToDelete = null; // Reset da variável
            }
        });
    }
}

// Toggle formulário
function toggleEntryForm(show = null) {
    const container = document.getElementById('entry-form-container');
    if (!container) return;

    const isVisible = container.style.display !== 'none';
    
    if (show === null) {
        show = !isVisible;
    }
    
    container.style.display = show ? 'block' : 'none';
    
    if (show) {
        const contentField = document.getElementById('content');
        if (contentField) {
            contentField.focus();
        }
    } else {
        clearForm();
    }
}

// Limpar formulário
function clearForm() {
    const form = document.getElementById('diary-form');
    if (!form) return;
    
    form.reset();
    
    // Resetar humor para neutro
    const neutroRadio = document.getElementById('neutro');
    if (neutroRadio) {
        neutroRadio.checked = true;
    }
    
    updateCharCounter();
}

// Atualizar contador de caracteres
function updateCharCounter() {
    const textarea = document.getElementById('content');
    const counter = document.getElementById('char-count');
    
    if (!textarea || !counter) return;
    
    const length = textarea.value.length;
    counter.textContent = length;
    
    // Mudar cor se próximo do limite
    if (length > 900) {
        counter.style.color = '#ef4444';
    } else if (length > 700) {
        counter.style.color = '#f59e0b';
    } else {
        counter.style.color = '#6b7280';
    }
}

// Carregar entradas
async function loadEntries(page = 1) {
    if (DiaryState.isLoading) {
        console.log('⏳ Já carregando entradas, ignorando...');
        return;
    }

    console.log(`📖 Carregando entradas - Página ${page}`);
    DiaryState.isLoading = true;
    
    const entriesList = document.getElementById('entries-list');
    if (!entriesList) {
        console.error('❌ Lista de entradas não encontrada');
        DiaryState.isLoading = false;
        return;
    }

    // Mostrar loading apenas se for primeira carga
    if (page === 1) {
        entriesList.innerHTML = `
            <div class="loading-entries">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Carregando suas entradas...</span>
            </div>
        `;
    }

    try {
        const params = new URLSearchParams({
            page: page,
            per_page: 10,
            period: DiaryState.currentFilters.period,
            mood: DiaryState.currentFilters.mood
        });

        console.log(`🔍 Fazendo requisição: /api/diary/get?${params}`);
        
        const response = await fetch(`/api/diary/get?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        console.log(`📡 Resposta recebida:`, response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(`📊 Dados recebidos:`, data);

        if (data.success) {
            DiaryState.entries = data.entries || [];
            DiaryState.currentPage = data.current_page || 1;
            DiaryState.totalPages = data.total_pages || 1;
            
            displayEntries(DiaryState.entries);
            updatePagination();
            
            console.log(`✅ ${DiaryState.entries.length} entradas carregadas`);
        } else {
            throw new Error(data.message || 'Erro ao carregar entradas');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar entradas:', error);
        entriesList.innerHTML = `
            <div class="no-entries">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Erro ao carregar entradas</h3>
                <p>${error.message}</p>
                <button onclick="loadEntries(${page})" class="btn-primary">
                    <i class="fas fa-redo"></i>
                    Tentar novamente
                </button>
            </div>
        `;
        showNotification('Erro ao carregar entradas: ' + error.message, 'error');
    } finally {
        DiaryState.isLoading = false;
    }
}

// Exibir entradas
function displayEntries(entries) {
    const entriesList = document.getElementById('entries-list');
    if (!entriesList) {
        console.error('❌ Elemento entries-list não encontrado no DOM');
        return;
    }

    if (!entries || entries.length === 0) {
        entriesList.innerHTML = `
            <div class="no-entries">
                <i class="fas fa-journal-whills"></i>
                <h3>Nenhuma entrada encontrada</h3>
                <p>Que tal começar escrevendo sobre como você está se sentindo hoje?</p>
                <button onclick="toggleEntryForm(true)" class="btn-primary">
                    <i class="fas fa-plus"></i>
                    Criar primeira entrada
                </button>
            </div>
        `; 
        console.log('📝 Estado vazio exibido (comentado)');
        return;
    }

    const entriesHTML = entries.map(entry => createEntryHTML(entry)).join('');
    entriesList.innerHTML = `<div class="entries-container">${entriesHTML}</div>`;
    
    // Adicionar event listeners para botões de ação
    setupEntryActions();
    
    console.log(`✅ ${entries.length} entradas exibidas`);
}

// Criar HTML de uma entrada
function createEntryHTML(entry) {
    const date = new Date(entry.created_at).toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
    
    const time = new Date(entry.created_at).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    const moodEmojis = {
        'muito-feliz': '😄',
        'feliz': '😊',
        'neutro': '😐',
        'triste': '😢',
        'muito-triste': '😭'
    };

    const moodLabels = {
        'muito-feliz': 'Muito Feliz',
        'feliz': 'Feliz',
        'neutro': 'Neutro',
        'triste': 'Triste',
        'muito-triste': 'Muito Triste'
    };

    return `
        <div class="entry-card" data-entry-id="${entry.id}">
            <div class="entry-header">
                <div class="entry-mood">
                    <span class="mood-emoji">${moodEmojis[entry.mood] || '😐'}</span>
                    <span class="mood-text">${moodLabels[entry.mood] || 'Neutro'}</span>
                </div>
                <div class="entry-date">
                    <i class="fas fa-calendar"></i>
                    ${date} às ${time}
                </div>
            </div>
            
            ${entry.title ? `<h4 class="entry-title">${escapeHtml(entry.title)}</h4>` : ''}
            
            <div class="entry-content">
                <p>${escapeHtml(entry.content)}</p>
            </div>
            
            <div class="entry-actions">
                <button class="action-btn edit-btn" onclick="editEntry(${entry.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete-btn" onclick="deleteEntry(${entry.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

// Configurar ações das entradas
function setupEntryActions() {
    console.log('⚙️ Configurando ações das entradas');
}

// Carregar insights
async function loadInsights() {
    console.log('💡 Carregando insights...');
    
    const insightsContent = document.getElementById('insights-content');
    if (!insightsContent) {
        console.error('❌ Container de insights não encontrado');
        return;
    }

    try {
        const params = new URLSearchParams({
            period: DiaryState.currentFilters.period
        });

        console.log(`🔍 Fazendo requisição: /api/diary/insights?${params}`);

        const response = await fetch(`/api/diary/insights?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        console.log(`📡 Resposta insights:`, response.status);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(`📊 Insights recebidos:`, data);

        if (data.success) {
            displayInsights(data.insights);
            console.log('✅ Insights carregados');
        } else {
            throw new Error(data.message || 'Erro ao carregar insights');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar insights:', error);
        insightsContent.innerHTML = `
            <div class="insights-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Erro ao carregar insights</p>
                <button onclick="loadInsights()" class="retry-btn">
                    <i class="fas fa-redo"></i>
                    Tentar novamente
                </button>
            </div>
        `;
    }
}

// Exibir insights
function displayInsights(insights) {
    const insightsContent = document.getElementById('insights-content');
    if (!insightsContent) return;

    if (!insights || Object.keys(insights).length === 0) {
        insightsContent.innerHTML = `
            <div class="no-insights">
                <i class="fas fa-chart-line"></i>
                <p>Nenhum insight disponível ainda</p>
                <small>Escreva algumas entradas para ver seus insights!</small>
            </div>
        `;
        return;
    }

    const insightsHTML = `
        <div class="insights-container">
            <div class="insight-item">
                <div class="insight-label">Entradas este mês</div>
                <div class="insight-value">${insights.total_entries || 0}</div>
            </div>
            
            <div class="insight-item">
                <div class="insight-label">Humor predominante</div>
                <div class="insight-value">${insights.dominant_mood || 'N/A'}</div>
            </div>
            
            <div class="insight-item">
                <div class="insight-label">Palavras escritas</div>
                <div class="insight-value">${insights.total_words || 0}</div>
            </div>
            
            ${insights.streak ? `
                <div class="insight-item">
                    <div class="insight-label">Sequência atual</div>
                    <div class="insight-value">${insights.streak} dias</div>
                </div>
            ` : ''}
        </div>
    `;

    insightsContent.innerHTML = insightsHTML;
}

// Aplicar filtros
function applyFilters() {
    console.log('🔍 Aplicando filtros...');
    
    const periodSelect = document.getElementById('period-filter');
    const moodSelect = document.getElementById('mood-filter');
    
    if (periodSelect) DiaryState.currentFilters.period = periodSelect.value;
    if (moodSelect) DiaryState.currentFilters.mood = moodSelect.value;
    
    console.log('📋 Filtros atualizados:', DiaryState.currentFilters);
    
    // Resetar página e recarregar
    DiaryState.currentPage = 1;
    loadEntries(1);
    loadInsights();
}

// Submit do formulário
async function handleFormSubmit(e) {
    e.preventDefault();
    console.log('💾 Salvando entrada...');

    const form = e.target;
    const formData = new FormData(form);
    
    const entryData = {
        mood: formData.get('mood'),
        title: formData.get('title') || '',
        content: formData.get('content')
    };

    console.log('📝 Dados da entrada:', entryData);

    try {
        const response = await fetch('/api/diary/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(entryData)
        });

        console.log(`📡 Resposta do salvamento:`, response.status);

        const data = await response.json();
        console.log('📊 Resultado:', data);

        if (data.success) {
            showNotification('Entrada salva com sucesso!', 'success');
            toggleEntryForm(false);
            clearForm();
            loadEntries(1);
            loadInsights();
        } else {
            throw new Error(data.message || 'Erro ao salvar entrada');
        }
    } catch (error) {
        console.error('❌ Erro ao salvar entrada:', error);
        showNotification('Erro ao salvar entrada: ' + error.message, 'error');
    }
}

// Utilitários
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
}

function showNotification(message, type = 'success') {
    console.log(`📢 Notificação ${type}: ${message}`);
    
    const notification = document.getElementById('notification');
    if (!notification) return;

    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Funções de ação (placeholder)
function editEntry(id) {
    console.log('✏️ Editar entrada:', id);
    showNotification('Funcionalidade em desenvolvimento', 'info');
}

// Estado global para controle da exclusão
let entryToDelete = null;

function deleteEntry(id) {
    console.log('🗑️ Solicitando exclusão da entrada:', id);
    
    // Armazena o ID da entrada a ser deletada
    entryToDelete = id;
    
    // Exibe o modal de confirmação
    const modal = document.getElementById('delete-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

async function confirmDelete() {
    console.log('✅ Confirmando exclusão da entrada:', entryToDelete);
    
    if (!entryToDelete) {
        console.error('❌ Nenhuma entrada selecionada para exclusão');
        return;
    }
    
    try {
        // Fecha o modal
        const modal = document.getElementById('delete-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        
        // Faz a requisição DELETE para a API
        const response = await fetch(`/api/diary/delete/${entryToDelete}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Entrada deletada com sucesso!', 'success');
            
            // Remove a entrada da interface imediatamente
            const entryElement = document.querySelector(`[data-entry-id="${entryToDelete}"]`);
            if (entryElement) {
                entryElement.style.transform = 'translateX(-100%)';
                entryElement.style.opacity = '0';
                setTimeout(() => {
                    entryElement.remove();
                    // Verifica se não há mais entradas
                    checkForEmptyState();
                }, 300);
            }
            
            // Recarrega os insights
            loadInsights();
            
        } else {
            showNotification(data.error || 'Erro ao deletar entrada', 'error');
        }
        
    } catch (error) {
        console.error('❌ Erro ao deletar entrada:', error);
        showNotification('Erro de conectividade. Tente novamente.', 'error');
    } finally {
        // Reset da variável
        entryToDelete = null;
    }
}

function checkForEmptyState() {
    const entriesList = document.getElementById('entries-list');
    const entryCards = document.querySelectorAll('.entry-card');
    
    if (entryCards.length === 0 && entriesList) {
        /* entriesList.innerHTML = `
            <div class="no-entries">
                <i class="fas fa-journal-whills"></i>
                <h3>Nenhuma entrada encontrada</h3>
                <p>Que tal começar escrevendo sobre como você está se sentindo hoje?</p>
                <button onclick="toggleEntryForm(true)" class="btn-primary">
                    <i class="fas fa-plus"></i>
                    Criar primeira entrada
                </button>
            </div>
        `; */
        console.log('📝 Estado vazio restaurado após exclusão (comentado)');
    }
}

function updatePagination() {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    
    if (DiaryState.totalPages <= 1) {
        pagination.style.display = 'none';
        return;
    }
    
    pagination.style.display = 'block';
    // TODO: Implementar paginação
}
