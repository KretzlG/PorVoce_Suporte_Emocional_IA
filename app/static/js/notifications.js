/**
 * Sistema de notificações - evita acúmulo de mensagens
 */

document.addEventListener('DOMContentLoaded', function() {
    // Limpar mensagens antigas ao carregar a página
    clearOldNotifications();
    
    // Auto-hide das mensagens após alguns segundos
    autoHideNotifications();
    
    // Limpar notifications do localStorage se estiver na home
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        clearStoredNotifications();
    }
});

function clearOldNotifications() {
    // Remove mensagens que podem ter ficado grudadas no DOM
    const existingMessages = document.querySelectorAll('.error-messages, .success-messages, .alert');
    
    // Se estamos numa página diferente da que gerou a mensagem, limpar
    const currentPage = window.location.pathname;
    const lastNotificationPage = localStorage.getItem('lastNotificationPage');
    
    if (lastNotificationPage && lastNotificationPage !== currentPage) {
        existingMessages.forEach(msg => {
            if (!msg.dataset.fresh) { // Não remover mensagens recém criadas
                msg.remove();
            }
        });
    }
}

function autoHideNotifications() {
    const messages = document.querySelectorAll('.error-message, .success-message, .alert');
    
    messages.forEach(message => {
        // Marcar como fresh para não ser removido imediatamente
        message.dataset.fresh = 'true';
        
        // Auto-hide após 5 segundos
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            
            setTimeout(() => {
                if (message.parentNode) {
                    message.remove();
                }
            }, 500);
        }, 5000);
        
        // Permitir fechar clicando na mensagem
        message.style.cursor = 'pointer';
        message.addEventListener('click', function() {
            this.style.opacity = '0';
            this.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                if (this.parentNode) {
                    this.remove();
                }
            }, 300);
        });
    });
    
    // Armazenar página atual
    localStorage.setItem('lastNotificationPage', window.location.pathname);
}

function clearStoredNotifications() {
    localStorage.removeItem('lastNotificationPage');
}

// Função para criar notificações programaticamente
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.container') || document.body;
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} error-message`;
    notification.style.cssText = `
        display: block;
        margin-bottom: 5px;
        padding: 10px;
        border-radius: 5px;
        font-size: 13px;
        opacity: 1;
        transition: opacity 0.3s ease;
        cursor: pointer;
    `;
    
    if (type === 'danger' || type === 'error') {
        notification.style.backgroundColor = '#ffebee';
        notification.style.border = '1px solid #e51b61';
        notification.style.color = '#e51b61';
    } else if (type === 'success') {
        notification.style.backgroundColor = '#e8f5e8';
        notification.style.border = '1px solid #4caf50';
        notification.style.color = '#4caf50';
    }
    
    notification.textContent = message;
    notification.dataset.fresh = 'true';
    
    // Inserir no início do container
    container.insertBefore(notification, container.firstChild);
    
    // Auto-hide
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, duration);
    
    // Click para fechar
    notification.addEventListener('click', function() {
        this.style.opacity = '0';
        setTimeout(() => {
            if (this.parentNode) {
                this.remove();
            }
        }, 300);
    });
    
    return notification;
}

// Exportar para uso global
window.showNotification = showNotification;
