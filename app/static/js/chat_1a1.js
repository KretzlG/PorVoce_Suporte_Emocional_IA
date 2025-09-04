document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const sessionId = chatMessages ? chatMessages.dataset.sessionId : null;
    let lastMessageCount = 0;

    // Função para buscar mensagens
    function fetchMessages() {
        fetch(`/volunteer/api/messages/${sessionId}`)
            .then(res => res.json())
            .then(data => {
                const prevCount = lastMessageCount;
                lastMessageCount = data.messages.length;
                chatMessages.innerHTML = '';
                data.messages.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = `chat-message ${msg.message_type === 'volunteer' ? 'from-volunteer' : 'from-client'} message-animate`;
                    div.innerHTML = `<span class='chat-author'>${msg.message_type === 'volunteer' ? 'Você' : data.client_name}:</span> <span class='chat-content'>${msg.content}</span>`;
                    chatMessages.appendChild(div);
                    setTimeout(() => div.classList.remove('message-animate'), 600);
                });
                chatMessages.scrollTop = chatMessages.scrollHeight;
                // Notificação sonora/visual
                if (prevCount > 0 && lastMessageCount > prevCount) {
                    playNotification();
                }
            });
    }
    function playNotification() {
        // Notificação sonora
        const audio = new Audio('/static/notification.mp3');
        audio.play();
        // Notificação visual
        chatMessages.classList.add('new-message');
        setTimeout(() => chatMessages.classList.remove('new-message'), 1000);
    }

    // Envio de mensagem via AJAX
    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const content = chatInput.value.trim();
            if (!content) return;
            fetch(`/volunteer/api/send_message/${sessionId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content})
            })
            .then(res => res.json())
            .then(data => {
                chatInput.value = '';
                fetchMessages();
                if (data.warning) {
                    showSessionWarning(data.warning);
                }
            });
        });
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
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                sendBtn.click();
            }
        });
    }

    // Atualização automática
    if (sessionId) {
        setInterval(fetchMessages, 3000);
        fetchMessages();
    }
});
