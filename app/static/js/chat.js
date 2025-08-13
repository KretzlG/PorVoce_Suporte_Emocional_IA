// chat.js - ForYou

let sessionId = null;
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');

function renderMessage(content, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.className = 'message ' + sender;
  if (sender !== 'user') {
    // Avatar só para IA
    const avatar = document.createElement('span');
    avatar.className = 'avatar';
    avatar.innerHTML = '<img src="/static/img/conversando.png" alt="IA" style="width:32px;height:32px;border-radius:8px;">';
    msgDiv.appendChild(avatar);
  }
  // Markdown básico
  const msgContent = document.createElement('span');
  msgContent.className = 'msg-content';
  msgContent.innerHTML = markdownToHtml(content);
  msgDiv.appendChild(msgContent);
  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator(show) {
  let indicator = document.getElementById('typing-indicator');
  if (show) {
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'typing-indicator';
      indicator.className = 'typing-indicator';
  indicator.innerHTML = '<img src="/static/img/conversando.png" alt="IA" style="width:24px;height:24px;border-radius:6px;vertical-align:middle;margin-right:6px;"> A IA está digitando <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>';
      chatMessages.appendChild(indicator);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  } else if (indicator) {
    indicator.remove();
  }
}

function markdownToHtml(text) {
  // Negrito **texto**
  text = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
  // Itálico *texto*
  text = text.replace(/\*(.*?)\*/g, '<i>$1</i>');
  // Links [texto](url)
  text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
  // Quebra de linha
  text = text.replace(/\n/g, '<br>');
  return text;
}

async function startSession() {
  const res = await fetch('/chat/new-session', { method: 'POST', credentials: 'include' });
  const data = await res.json();
  if (data.success) {
    sessionId = data.session_id;
    loadHistory();
  } else {
    renderMessage('Erro ao iniciar sessão de chat.', 'ai');
  }
}

async function loadHistory() {
  if (!sessionId) return;
  chatMessages.innerHTML = '';
  const res = await fetch(`/chat/api/chat/receive?session_id=${sessionId}`, { credentials: 'include' });
  const data = await res.json();
  if (data.success && data.messages) {
    data.messages.forEach(msg => {
      renderMessage(msg.content, msg.message_type);
    });
  }
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text || !sessionId) return;
  renderMessage(text, 'user');
  chatInput.value = '';
  showTypingIndicator(true);
  try {
  const res = await fetch('/chat/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ message: text, session_id: sessionId })
    });
    const data = await res.json();
    showTypingIndicator(false);
    if (data.success && data.ai_response) {
      renderMessage(data.ai_response.content, 'ai');
    } else {
      renderMessage('Erro ao obter resposta da IA.', 'ai');
    }
  } catch (e) {
    showTypingIndicator(false);
    renderMessage('Erro de conexão com o servidor.', 'ai');
  }
}

sendBtn.onclick = sendMessage;
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') sendMessage();
});

clearBtn.onclick = () => {
  chatMessages.innerHTML = '';
  startSession();
};

window.onload = startSession;
