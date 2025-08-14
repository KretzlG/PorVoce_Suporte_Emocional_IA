const form = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const messages = document.getElementById("messages");
const button = document.querySelector('.ripple-button');
const submitButton = document.querySelector('.ripple-button2');

form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage();
});

window.onload = () => {
    loadMessages();
    userInput.focus();
};

function loadPage(pagina) {
  fetch(`${pagina}.html`)
    .then(res => res.text())
    .then(html => {
      document.getElementById('conteudo').innerHTML = html;
    });
}

function sendMessage() {
    const input = userInput.value.trim();
    if (input === "") return;

    appendMessage(input, false);
    userInput.value = "";
    userInput.disabled = true;
    sendButton.disabled = true;

    const thinking = showThinkingAnimation();

    setTimeout(() => {
        clearInterval(thinking.interval);
        messages.removeChild(thinking.element);

        appendMessage("Entendi. Pode me contar mais sobre isso ?", true, false, () => {
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
            saveMessages();
        });

    }, 2000);
}

function appendMessage(content, isBot = true, skipAnimation = false, callback) {
    const msg = document.createElement("div");
    msg.classList.add("message");
    msg.classList.add(isBot ? "bot" : "user");

    if (isBot && !skipAnimation) {
        let index = 0;
        const interval = setInterval(() => {
            msg.textContent = content.slice(0, index++);
            if (index >= content.length) {
                clearInterval(interval);
                if (callback) callback(); 
            }
        }, 30);
    } else {
        msg.textContent = content;
        if (callback) callback();
    }

    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
}

function showThinkingAnimation() {
    const thinking = document.createElement("div");
    thinking.classList.add("message", "bot", "thinking-animation");
    thinking.textContent = "Pensando";
    messages.appendChild(thinking);
    messages.scrollTop = messages.scrollHeight;

    let dotCount = 0;
    const interval = setInterval(() => {
        dotCount = (dotCount + 1) % 4;
        thinking.textContent = "Pensando" + ".".repeat(dotCount);
    }, 500);

    return { element: thinking, interval };
}

function saveMessages() {
    const savedMessages = [];
    const allMessages = messages.querySelectorAll(".message");

    allMessages.forEach(msg => {
        const content = msg.textContent || "";  
        savedMessages.push({
            text: content.trim(),
            isBot: msg.classList.contains("bot")
        });
    });

    localStorage.setItem("chatHistory", JSON.stringify(savedMessages));
}

function loadMessages() {
    const saved = localStorage.getItem("chatHistory");
    if (!saved) return;

    const parsed = JSON.parse(saved);
    parsed.forEach(msg => {
        if (
            !(msg.isBot && (
                msg.text === "Bem-vindo ao Chat de Suporte Emocional !" ||
                msg.text === "Como você está se sentindo hoje?" ||
                msg.text === "Bem-vindo ao Chat de Suporte Emocional !Como você está se sentindo hoje?"
            ))
        ) {
            appendMessage(msg.text, msg.isBot, true);
        }
    });
}

button.addEventListener('click', function (e) {
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');

    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = `${size}px`;
    ripple.style.height = `${size}px`;

    const x = e.clientX - rect.left - size / 2.16;
    const y = e.clientY - rect.top - size / 3.07;

    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;

    button.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
});

submitButton.addEventListener('click', function (e) {
    const ripple = document.createElement('span');
    ripple.classList.add('rippleSubmit');

    const rect = submitButton.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = `${size}px`;

    const RIPPLE_OFFSET_X_DIVISOR = 1.82; 
    const RIPPLE_OFFSET_Y_DIVISOR = 2;    

    const x = e.clientX - rect.left - size / RIPPLE_OFFSET_X_DIVISOR;
    const y = e.clientY - rect.top - size / RIPPLE_OFFSET_Y_DIVISOR;

    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;

    submitButton.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 700);
});