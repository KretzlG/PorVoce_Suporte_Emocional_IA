document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const sessionId = chatMessages ? chatMessages.dataset.sessionId : null;
    let lastMessageCount = 0;

    // Função para buscar mensagens
    function fetchMessages() {
        if (!sessionId) return;
        
        fetch(`/volunteer/api/messages/${sessionId}`)
            .then(res => res.json())
            .then(data => {
                if (!data.success) return;
                
                const prevCount = lastMessageCount;
                const newCount = data.messages.length;
                
                // Só atualizar se houver mudanças
                if (newCount !== lastMessageCount) {
                    lastMessageCount = newCount;
                    updateMessagesDisplay(data.messages);
                    
                    // Notificação para novas mensagens
                    if (prevCount > 0 && newCount > prevCount) {
                        playNotification();
                    }
                }
            })
            .catch(error => {
                console.error('Erro ao buscar mensagens:', error);
            });
    }
    
    // Função separada para atualizar display das mensagens
    function updateMessagesDisplay(messages) {
        chatMessages.innerHTML = '';
        
        messages.forEach(msg => {
            const div = document.createElement('div');
            const isVolunteer = msg.message_type === 'volunteer';
            div.className = `chat-message ${isVolunteer ? 'from-volunteer' : 'from-client'}`;
            
            // Criar avatar
            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'message-avatar';
            avatarDiv.innerHTML = `<i class="${isVolunteer ? 'fas fa-heart' : 'fas fa-user'}"></i>`;
            
            // Criar conteúdo da mensagem
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            const messageText = document.createElement('div');
            messageText.textContent = msg.content;
            
            const timeSpan = document.createElement('div');
            timeSpan.className = 'message-time';
            const msgTime = new Date(msg.created_at);
            timeSpan.textContent = msgTime.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            contentDiv.appendChild(messageText);
            contentDiv.appendChild(timeSpan);
            
            div.appendChild(avatarDiv);
            div.appendChild(contentDiv);
            
            chatMessages.appendChild(div);
        });
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    function playNotification() {
        try {
            // Notificação sonora (opcional)
            const audio = new Audio('/static/notification.mp3');
            audio.play().catch(() => {
                // Ignorar erro de áudio se não conseguir tocar
            });
        } catch (e) {
            // Ignorar erro de áudio
        }
        
        // Notificação visual
        if (chatMessages) {
            chatMessages.classList.add('new-message');
            setTimeout(() => chatMessages.classList.remove('new-message'), 1000);
        }
    }

    // Envio de mensagem via AJAX
    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const content = chatInput.value.trim();
            if (!content) return;
            
            // Desabilitar botão temporariamente
            sendBtn.disabled = true;
            const originalHTML = sendBtn.innerHTML;
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            fetch(`/volunteer/client_chat/${sessionId}/send`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    chatInput.value = '';
                    // Buscar mensagens imediatamente após enviar
                    setTimeout(fetchMessages, 500);
                } else {
                    console.error('Erro ao enviar:', data.error);
                }
                
                if (data.warning) {
                    showSessionWarning(data.warning);
                }
            })
            .catch(error => {
                console.error('Erro ao enviar mensagem:', error);
            })
            .finally(() => {
                // Reabilitar botão
                sendBtn.disabled = false;
                sendBtn.innerHTML = originalHTML;
            });
        });
    }

    // Feedback visual para sessão encerrada
    function showSessionWarning(msg) {
        let warning = document.getElementById('session-warning');
        if (!warning) {
            warning = document.createElement('div');
            warning.id = 'session-warning';
            warning.className = 'session-warning';
            chatMessages.parentNode.insertBefore(warning, chatMessages);
        }
        warning.textContent = msg;
        warning.style.display = 'block';
        clearTimeout(warning._timeout);
        warning._timeout = setTimeout(() => { warning.style.display = 'none'; }, 4000);
    }

    // Permitir envio com Enter
    // Permitir envio com Enter
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                if (sendBtn) sendBtn.click();
            }
        });
    }

    // Atualização automática
    if (sessionId) {
        // Carregar mensagens iniciais
        fetchMessages();
        // Atualização mais suave a cada 5 segundos
        setInterval(fetchMessages, 5000);
    }
});
