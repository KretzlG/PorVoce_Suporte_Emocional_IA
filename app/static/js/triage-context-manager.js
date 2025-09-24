/**
 * Funções para gerenciar contexto de triagem no chat
 * Adicione essas funções ao seu JavaScript principal do chat
 */

// Função para marcar triagem como iniciada
function markTriageInitiated(sessionId, context = {}) {
    return fetch('/triage/initiated', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            context: context
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Triagem marcada como iniciada');
            return data;
        } else {
            console.error('Erro ao marcar triagem:', data.error);
            return null;
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        return null;
    });
}

// Função para marcar triagem como recusada
function markTriageDeclined(sessionId, reason = 'Não informado') {
    return fetch('/triage/declined', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Triagem marcada como recusada');
            return data;
        } else {
            console.error('Erro ao marcar triagem recusada:', data.error);
            return null;
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        return null;
    });
}

// Função para marcar triagem como completada
function markTriageCompleted(sessionId, results = {}) {
    return fetch('/triage/completed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            results: results
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Triagem marcada como completada');
            return data;
        } else {
            console.error('Erro ao marcar triagem completada:', data.error);
            return null;
        }
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
        return null;
    });
}

// Exemplo de uso quando o usuário aceita a triagem
function onTriageAccepted(sessionId) {
    markTriageInitiated(sessionId, {
        user_action: 'accepted',
        timestamp: new Date().toISOString()
    });
}

// Exemplo de uso quando o usuário recusa a triagem
function onTriageDeclined(sessionId, reason) {
    markTriageDeclined(sessionId, reason);
}

// Exemplo de uso quando a triagem é finalizada
function onTriageFinished(sessionId, triageData) {
    markTriageCompleted(sessionId, triageData);
}

// Integração com o fluxo de triagem existente
// Adicione estas chamadas nos pontos apropriados do seu código de triagem:

/*
EXEMPLO DE INTEGRAÇÃO:

// Quando mostrar popup de triagem
if (riskLevel === 'moderate' || riskLevel === 'high' || riskLevel === 'critical') {
    showTriagePopup();
    // Não marcar como iniciada ainda, apenas quando usuário aceitar
}

// No botão "Aceitar triagem"
document.getElementById('accept-triage-btn').addEventListener('click', function() {
    onTriageAccepted(currentSessionId);
    // Continuar com o fluxo normal de triagem
});

// No botão "Recusar triagem"
document.getElementById('decline-triage-btn').addEventListener('click', function() {
    const reason = document.getElementById('decline-reason').value || 'Não quis informar';
    onTriageDeclined(currentSessionId, reason);
    closeTriagePopup();
});

// Ao finalizar o processo de triagem
function finishTriageProcess(results) {
    onTriageFinished(currentSessionId, {
        emotions: results.selectedEmotions,
        main_concern: results.mainConcern,
        urgency: results.urgencyLevel,
        completed_sections: results.completedSections
    });
}
*/