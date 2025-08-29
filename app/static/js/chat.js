// Chat.js - Sistema de Chat com Histórico
let currentSessionId = null;
let conversationToDelete = null;

// Elementos DOM
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const endChatBtn = document.getElementById('end-chat-btn');
const backToHomeBtn = document.getElementById('back-to-home');
const chatList = document.getElementById('chat-list');
const chatTitle = document.getElementById('chat-title');
const chatStatus = document.getElementById('chat-status');
const deleteModal = document.getElementById('delete-modal');
const modalClose = document.getElementById('modal-close');
const confirmDelete = document.getElementById('confirm-delete');
const cancelDelete = document.getElementById('cancel-delete');
const emojiBtn = document.getElementById('emoji-btn');
const fileBtn = document.getElementById('file-btn');
const emojiPicker = document.getElementById('emoji-picker');
const fileInput = document.getElementById('file-input');

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    loadConversationHistory();
    setupEventListeners();
    
    // Habilitar input por padrão para permitir nova conversa
    enableChatInput();
    showWelcomeScreen();
});

function setupEventListeners() {
    // Botões principais
    newChatBtn.addEventListener('click', startNewChat);
    endChatBtn.addEventListener('click', endCurrentChat);
    backToHomeBtn.addEventListener('click', goBackToHome);
    sendBtn.addEventListener('click', sendMessage);
    
    // Input de mensagem
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Emoji e arquivo
    emojiBtn.addEventListener('click', toggleEmojiPicker);
    fileBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileUpload);
    
    // Emoji picker
    document.addEventListener('click', (e) => {
        if (!emojiPicker.contains(e.target) && !emojiBtn.contains(e.target)) {
            emojiPicker.style.display = 'none';
        }
    });
    
    // Emojis individuais
    document.querySelectorAll('.emoji').forEach(emoji => {
        emoji.addEventListener('click', (e) => {
            insertEmoji(e.target.dataset.emoji);
        });
    });
    
    // Modal
    modalClose.addEventListener('click', closeDeleteModal);
    cancelDelete.addEventListener('click', closeDeleteModal);
    confirmDelete.addEventListener('click', confirmDeleteConversation);
    
    // Fechar modal clicando fora
    deleteModal.addEventListener('click', (e) => {
        if (e.target === deleteModal) {
            closeDeleteModal();
        }
    });
}

// Carregar histórico de conversas
async function loadConversationHistory() {
    try {
        const response = await fetch('/chat/api/conversations', {
            credentials: 'include'
        });
        
        if (!response.ok) throw new Error('Erro ao carregar conversas');
        
        const data = await response.json();
        displayConversations(data.conversations || []);
        
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        chatList.innerHTML = `
            <div class="loading-conversations">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Erro ao carregar conversas</span>
            </div>
        `;
    }
}

// Exibir conversas na sidebar
function displayConversations(conversations) {
    if (conversations.length === 0) {
        chatList.innerHTML = `
            <div class="loading-conversations">
                <i class="fas fa-comments"></i>
                <span>Nenhuma conversa ainda</span>
                <small>Clique em "+" para iniciar</small>
            </div>
        `;
        return;
    }
    
    chatList.innerHTML = conversations.map(conv => `
        <div class="conversation-item" data-session-id="${conv.id}">
            <div class="conversation-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="conversation-info">
                <div class="conversation-header">
                    <div class="conversation-title">${conv.title || 'Conversa sem título'}</div>
                    <div class="conversation-date">${formatDate(conv.created_at)}</div>
                </div>
                <div class="conversation-preview">${conv.last_message || 'Conversa iniciada'}</div>
            </div>
            <div class="conversation-actions">
                <button class="delete-conversation" data-session-id="${conv.id}" title="Excluir conversa">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    // Adicionar event listeners
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.conversation-actions')) {
                const sessionId = item.dataset.sessionId;
                loadConversation(sessionId);
            }
        });
    });
    
    document.querySelectorAll('.delete-conversation').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const sessionId = btn.dataset.sessionId;
            showDeleteModal(sessionId);
        });
    });
}

// Carregar conversa específica
async function loadConversation(sessionId) {
    try {
        currentSessionId = sessionId;
        
        // Atualizar UI
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-session-id="${sessionId}"]`).classList.add('active');
        
        // Carregar mensagens
        const response = await fetch(`/chat/api/chat/receive?session_id=${sessionId}`, {
            credentials: 'include'
        });
        
        if (!response.ok) throw new Error('Erro ao carregar conversa');
        
        const data = await response.json();
        
        if (data.success) {
            // Limpar área de mensagens
            chatMessages.innerHTML = '';
            
            // Renderizar mensagens
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    renderMessage(msg.content, msg.message_type, msg.created_at);
                });
            } else {
                chatMessages.innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <h3>Conversa Carregada</h3>
                        <p>Continue sua conversa onde parou.</p>
                    </div>
                `;
            }
            
            // Habilitar input
            enableChatInput();
            updateChatStatus('Conversa ativa');
        }
        
    } catch (error) {
        console.error('Erro ao carregar conversa:', error);
        showError('Erro ao carregar conversa');
    }
}

// Iniciar nova conversa
async function startNewChat() {
    try {
        const response = await fetch('/chat/new-session', {
            method: 'POST',
            credentials: 'include'
        });
        
        if (!response.ok) throw new Error('Erro ao criar nova conversa');
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.session_id;
            
            // Limpar seleção anterior
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Limpar mensagens e mostrar boas-vindas
            chatMessages.innerHTML = '';
            showWelcomeScreen();
            
            // Habilitar input
            enableChatInput();
            updateChatStatus('Nova conversa iniciada - Digite sua primeira mensagem');
            
            // Recarregar histórico apenas uma vez ao final
            loadConversationHistory();
            
        } else {
            throw new Error(data.message || 'Erro ao criar conversa');
        }
        
    } catch (error) {
        console.error('Erro ao iniciar nova conversa:', error);
        showError('Erro ao iniciar nova conversa');
    }
}

// Encerrar conversa atual
async function endCurrentChat() {
    if (!currentSessionId) {
        showError('Nenhuma conversa ativa');
        return;
    }
    
    try {
        const response = await fetch('/chat/api/end-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ session_id: currentSessionId })
        });
        
        if (!response.ok) throw new Error('Erro ao encerrar conversa');
        
        const data = await response.json();
        
        if (data.success) {
            // Mostrar mensagem de encerramento
            showWelcomeScreen();
            updateChatStatus('Conversa encerrada - Digite uma mensagem para iniciar nova conversa');
            
            // Manter input habilitado para nova conversa
            enableChatInput();
            
            // Recarregar histórico
            loadConversationHistory();
            
            currentSessionId = null;
        }
        
    } catch (error) {
        console.error('Erro ao encerrar conversa:', error);
        showError('Erro ao encerrar conversa');
    }
}

// Enviar mensagem
async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    // Se não há sessão ativa, criar uma nova
    if (!currentSessionId) {
        try {
            await startNewChat();
            if (!currentSessionId) {
                showError('Erro ao iniciar nova conversa');
                return;
            }
        } catch (error) {
            showError('Erro ao iniciar nova conversa');
            return;
        }
    }
    
    // Renderizar mensagem do usuário
    renderMessage(text, 'user');
    chatInput.value = '';
    
    // Mostrar indicador de digitação
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat/api/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ 
                message: text, 
                session_id: currentSessionId 
            })
        });
        
        if (!response.ok) throw new Error('Erro ao enviar mensagem');
        
        const data = await response.json();
        hideTypingIndicator();
        
        if (data.success && data.ai_response) {
            renderMessage(data.ai_response.content, 'ai');
        } else {
            showError('Erro ao obter resposta da IA');
        }

        // Verificação do Alert no JSON
        
            if (data.alert) {
                alert(data.alert);
                window.location.href = '/triage';
            }
        
        // Não recarregar histórico desnecessariamente
        // As mensagens já foram renderizadas acima
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Erro ao enviar mensagem:', error);
        showError('Erro de conexão com o servidor');
    }
}

// Renderizar mensagem
function renderMessage(content, sender, timestamp = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    // Wrapper para avatar e conteúdo
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = 'message-wrapper';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'user' ? 
        '<i class="fas fa-user"></i>' : 
        '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = markdownToHtml(content);
    
    wrapperDiv.appendChild(avatarDiv);
    wrapperDiv.appendChild(contentDiv);
    messageDiv.appendChild(wrapperDiv);
    
    if (timestamp) {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = formatTime(timestamp);
        messageDiv.appendChild(timeDiv);
    }
    
    // Remover tela de boas-vindas se existir
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Indicador de digitação
function showTypingIndicator() {
    hideTypingIndicator(); // Remove indicador anterior se existir
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'typing-indicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="typing-content">
            A IA está digitando
            <span class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </span>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Modal de exclusão
function showDeleteModal(sessionId) {
    conversationToDelete = sessionId;
    deleteModal.style.display = 'block';
}

function closeDeleteModal() {
    deleteModal.style.display = 'none';
    conversationToDelete = null;
}

async function confirmDeleteConversation() {
    if (!conversationToDelete) return;
    
    try {
        const response = await fetch('/chat/api/delete-conversation', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ session_id: conversationToDelete })
        });
        
        if (!response.ok) throw new Error('Erro ao excluir conversa');
        
        const data = await response.json();
        
        if (data.success) {
            // Se é a conversa atual, limpar interface
            if (conversationToDelete == currentSessionId) {
                showWelcomeScreen();
                currentSessionId = null;
                // Manter input habilitado para permitir nova conversa
                enableChatInput();
            }
            
            // Recarregar histórico
            loadConversationHistory();
            closeDeleteModal();
        }
        
    } catch (error) {
        console.error('Erro ao excluir conversa:', error);
        showError('Erro ao excluir conversa');
    }
}

// Utilitários de UI
function enableChatInput() {
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.placeholder = 'Digite sua mensagem...';
}

function disableChatInput() {
    chatInput.disabled = true;
    sendBtn.disabled = true;
    chatInput.placeholder = 'Inicie uma nova conversa para continuar...';
}

function updateChatStatus(status) {
    // Se for "Conversa ativa", remove qualquer texto sobre primeira mensagem do status atual
    if (status === 'Conversa ativa') {
        const currentStatus = chatStatus.textContent;
        if (currentStatus.includes('- Digite sua primeira mensagem')) {
            // Mantém a parte antes do " - Digite sua primeira mensagem"
            const baseStatus = currentStatus.split(' - Digite sua primeira mensagem')[0];
            chatStatus.textContent = status;
        } else {
            chatStatus.textContent = status;
        }
    } else {
        chatStatus.textContent = status;
    }
}

function showWelcomeScreen() {
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <i class="fas fa-heart"></i>
            </div>
            <h3>Bem-vindo ao Chat de Apoio Emocional</h3>
            <p>Inicie uma nova conversa ou selecione uma conversa anterior do histórico.</p>
        </div>
    `;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message ai';
    errorDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="message-content" style="background: #f8d7da; color: #721c24; border-color: #f5c6cb;">
            ${message}
        </div>
    `;
    chatMessages.appendChild(errorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Utilitários
function markdownToHtml(text) {
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Hoje';
    if (diffDays === 2) return 'Ontem';
    if (diffDays <= 7) return `${diffDays} dias atrás`;
    
    return date.toLocaleDateString('pt-BR');
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Funcionalidades de Emoji e Arquivo
function toggleEmojiPicker() {
    const isVisible = emojiPicker.style.display === 'block';
    emojiPicker.style.display = isVisible ? 'none' : 'block';
}

function insertEmoji(emoji) {
    const currentValue = chatInput.value;
    const cursorPosition = chatInput.selectionStart;
    const textBefore = currentValue.substring(0, cursorPosition);
    const textAfter = currentValue.substring(cursorPosition);
    
    chatInput.value = textBefore + emoji + textAfter;
    chatInput.setSelectionRange(cursorPosition + emoji.length, cursorPosition + emoji.length);
    chatInput.focus();
    
    emojiPicker.style.display = 'none';
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Verificar tamanho do arquivo (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('Arquivo muito grande. Tamanho máximo: 5MB');
        return;
    }
    
    // Tipos de arquivo permitidos
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
        showError('Tipo de arquivo não suportado. Use: JPG, PNG, GIF, PDF ou TXT');
        return;
    }
    
    // Simular upload de arquivo
    showMessage(`📎 Arquivo anexado: ${file.name}`, 'user');
    
    // Limpar input
    event.target.value = '';
    
    // Simular resposta da IA sobre o arquivo
    setTimeout(() => {
        showMessage('Recebi o arquivo que você enviou. Como posso ajudá-lo com isso?', 'ai');
    }, 1000);
}

// Função para voltar ao início
function goBackToHome() {
    // Redirecionar para a página inicial
    window.location.href = '/';
}
