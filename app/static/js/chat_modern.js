// Chat Moderno com Alpine.js - JavaScript Interativo
document.addEventListener('alpine:init', () => {
    Alpine.data('modernChat', () => ({
        // Estado do chat
        messages: [],
        currentMessage: '',
        isTyping: false,
        isConnected: true,
        currentMood: 'neutral',
        
        // Sugestões rápidas
        quickSuggestions: [
            "Como você está se sentindo hoje?",
            "Preciso conversar sobre ansiedade",
            "Estou me sentindo triste",
            "Quero técnicas de relaxamento",
            "Preciso de ajuda para dormir",
            "Como lidar com estresse?"
        ],
        
        // Moods disponíveis
        moods: {
            happy: { emoji: '😊', label: 'Feliz', color: '#10b981' },
            sad: { emoji: '😢', label: 'Triste', color: '#6366f1' },
            anxious: { emoji: '😰', label: 'Ansioso', color: '#f59e0b' },
            angry: { emoji: '😠', label: 'Irritado', color: '#ef4444' },
            neutral: { emoji: '😐', label: 'Neutro', color: '#64748b' },
            confused: { emoji: '😕', label: 'Confuso', color: '#8b5cf6' }
        },

        // Inicialização
        init() {
            this.loadChatHistory();
            this.scrollToBottom();
            
            // Auto-resize textarea
            this.$refs.messageInput?.addEventListener('input', (e) => {
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
            });
            
            // Conectar WebSocket se disponível
            this.connectWebSocket();
        },

        // Carregar histórico de mensagens
        loadChatHistory() {
            // Simular algumas mensagens iniciais
            this.messages = [
                {
                    id: 1,
                    content: "Olá! Eu sou sua assistente de suporte emocional. Como posso te ajudar hoje?",
                    sender: 'ai',
                    timestamp: new Date(),
                    mood: null
                }
            ];
        },

        // Enviar mensagem
        async sendMessage() {
            if (!this.currentMessage.trim()) return;
            
            const message = {
                id: Date.now(),
                content: this.currentMessage,
                sender: 'user',
                timestamp: new Date(),
                mood: this.currentMood,
                status: 'sending'
            };
            
            this.messages.push(message);
            const messageContent = this.currentMessage;
            this.currentMessage = '';
            
            // Reset textarea height
            if (this.$refs.messageInput) {
                this.$refs.messageInput.style.height = 'auto';
            }
            
            this.scrollToBottom();
            
            try {
                // Simular envio
                await new Promise(resolve => setTimeout(resolve, 500));
                message.status = 'sent';
                
                // Mostrar indicador de digitação
                this.isTyping = true;
                this.scrollToBottom();
                
                // Simular resposta da IA
                await this.simulateAIResponse(messageContent);
                
            } catch (error) {
                console.error('Erro ao enviar mensagem:', error);
                message.status = 'error';
                this.showNotification('Erro ao enviar mensagem. Tente novamente.', 'error');
            }
        },

        // Simular resposta da IA
        async simulateAIResponse(userMessage) {
            // Delay realista para resposta
            await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));
            
            this.isTyping = false;
            
            // Respostas contextuais baseadas na mensagem do usuário
            let aiResponse = this.generateAIResponse(userMessage);
            
            const aiMessage = {
                id: Date.now(),
                content: aiResponse,
                sender: 'ai',
                timestamp: new Date(),
                mood: null
            };
            
            this.messages.push(aiMessage);
            this.scrollToBottom();
            
            // Análise de risco (simulada)
            this.analyzeRisk(userMessage);
        },

        // Gerar resposta contextual da IA
        generateAIResponse(userMessage) {
            const lowerMessage = userMessage.toLowerCase();
            
            // Palavras-chave para diferentes tipos de resposta
            if (lowerMessage.includes('triste') || lowerMessage.includes('deprimido') || lowerMessage.includes('down')) {
                return "Entendo que você está passando por um momento difícil. É normal sentir tristeza às vezes, e você foi corajoso(a) ao compartilhar isso comigo. Que tal conversarmos sobre o que está te fazendo sentir assim? Às vezes, falar sobre nossos sentimentos pode ajudar a processá-los melhor.";
            }
            
            if (lowerMessage.includes('ansioso') || lowerMessage.includes('ansiedade') || lowerMessage.includes('preocupado')) {
                return "A ansiedade pode ser muito desafiadora, mas quero que saiba que você não está sozinho(a) nisso. Vamos tentar algumas técnicas de respiração? Inspire lentamente por 4 segundos, segure por 4, e expire por 6. Repita isso algumas vezes. Também pode me contar mais sobre o que está causando essa ansiedade.";
            }
            
            if (lowerMessage.includes('ajuda') || lowerMessage.includes('socorro') || lowerMessage.includes('não aguento')) {
                return "Agradeço sua confiança em me procurar. Estou aqui para te apoiar. Se você estiver em uma situação de emergência, é importante buscar ajuda profissional imediatamente (CVV: 188, SAMU: 192). Caso contrário, vamos conversar sobre como posso te ajudar agora mesmo. O que está acontecendo?";
            }
            
            if (lowerMessage.includes('obrigad') || lowerMessage.includes('valeu')) {
                return "Fico muito feliz em poder ajudar! 😊 Lembre-se de que cuidar da sua saúde mental é um ato de amor próprio. Estou sempre aqui quando precisar. Como você está se sentindo agora?";
            }
            
            // Resposta padrão empática
            const responses = [
                "Entendo o que você está sentindo. Pode me contar mais sobre isso?",
                "Obrigada por compartilhar isso comigo. Como posso te ajudar melhor?",
                "Suas emoções são válidas e importantes. Vamos conversar sobre o que você está vivenciando.",
                "Estou aqui para te escutar e apoiar. Que tal me contar mais detalhes sobre sua situação?",
                "Percebo que isso é importante para você. Como você gostaria que eu te ajudasse?"
            ];
            
            return responses[Math.floor(Math.random() * responses.length)];
        },

        // Análise de risco (simulada)
        analyzeRisk(message) {
            const riskKeywords = [
                'suicídio', 'suicida', 'me matar', 'acabar com tudo', 
                'não aguento mais', 'quero morrer', 'sem esperança'
            ];
            
            const hasRisk = riskKeywords.some(keyword => 
                message.toLowerCase().includes(keyword)
            );
            
            if (hasRisk) {
                setTimeout(() => {
                    const emergencyMessage = {
                        id: Date.now(),
                        content: "🚨 ATENÇÃO: Percebi que você pode estar passando por uma crise. Sua vida é valiosa! Por favor, busque ajuda imediatamente:\n\n🔸 CVV (Centro de Valorização da Vida): 188\n🔸 SAMU: 192\n🔸 Procure um pronto-socorro\n🔸 Converse com alguém de confiança\n\nVocê não está sozinho(a). Existem pessoas que querem te ajudar.",
                        sender: 'ai',
                        timestamp: new Date(),
                        type: 'emergency'
                    };
                    
                    this.messages.push(emergencyMessage);
                    this.scrollToBottom();
                    this.showNotification('Detectado risco elevado - Busque ajuda imediata!', 'error');
                }, 1000);
            }
        },

        // Usar sugestão rápida
        useSuggestion(suggestion) {
            this.currentMessage = suggestion;
            this.$refs.messageInput?.focus();
        },

        // Alterar mood
        setMood(mood) {
            this.currentMood = mood;
            
            // Opcional: enviar informação do mood para o backend
            this.sendMoodUpdate(mood);
        },

        // Atualizar mood no backend
        async sendMoodUpdate(mood) {
            try {
                // Aqui você enviaria o mood para o Flask
                await fetch('/api/chat/mood', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ mood: mood })
                });
            } catch (error) {
                console.error('Erro ao atualizar mood:', error);
            }
        },

        // Scroll para o final
        scrollToBottom() {
            this.$nextTick(() => {
                const container = this.$refs.messagesContainer;
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        },

        // Conectar WebSocket (se disponível)
        connectWebSocket() {
            try {
                // Implementar conexão WebSocket real se necessário
                this.isConnected = true;
            } catch (error) {
                console.error('WebSocket não disponível:', error);
                this.isConnected = false;
            }
        },

        // Mostrar notificação
        showNotification(message, type = 'info') {
            // Criar elemento de notificação
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg text-white max-w-sm animate-slide-down ${
                type === 'error' ? 'bg-red-500' : 
                type === 'success' ? 'bg-green-500' : 
                'bg-blue-500'
            }`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Remover após 5 segundos
            setTimeout(() => {
                notification.remove();
            }, 5000);
        },

        // Limpar chat
        clearChat() {
            if (confirm('Tem certeza que deseja limpar o histórico do chat?')) {
                this.messages = [];
                this.showNotification('Chat limpo com sucesso!', 'success');
            }
        },

        // Exportar conversa
        exportChat() {
            const chatData = this.messages.map(msg => ({
                timestamp: msg.timestamp.toLocaleString(),
                sender: msg.sender === 'user' ? 'Você' : 'Assistente IA',
                content: msg.content,
                mood: msg.mood
            }));
            
            const dataStr = JSON.stringify(chatData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            
            this.showNotification('Chat exportado com sucesso!', 'success');
        },

        // Formatters
        formatTime(date) {
            return new Intl.DateTimeFormat('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            }).format(date);
        },

        // Getters computados
        get connectionStatus() {
            return this.isConnected ? 'Conectado' : 'Desconectado';
        },

        get currentMoodData() {
            return this.moods[this.currentMood];
        }
    }));
});

// Utility functions
window.ChatUtils = {
    // Detectar URLs em texto e transformar em links
    linkify(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, '<a href="$1" target="_blank" class="text-blue-500 underline">$1</a>');
    },
    
    // Formatear texto com markdown básico
    formatMarkdown(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>');
    },
    
    // Validar se uma mensagem contém conteúdo apropriado
    validateMessage(text) {
        if (!text.trim()) return false;
        if (text.length > 2000) return false;
        return true;
    }
};