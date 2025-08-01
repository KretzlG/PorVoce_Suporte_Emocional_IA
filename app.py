from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from ai_service import EmotionalAIService

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chave-temporaria-para-desenvolvimento')

# Habilitar CORS para permitir requisições AJAX
CORS(app)

# Inicializar serviço de IA
ai_service = EmotionalAIService()

@app.route('/')
def index():
    return redirect(url_for('register')) 
# Pelo amor de Deus, me lembra de adicionar um verificador pra ver se o usuário já está logado ou não.

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/diary')
def diary():
    return render_template('diary.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# =============================================================================
# API ENDPOINTS PARA IA/NLP
# =============================================================================

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    Endpoint principal para chat com IA emocional
    
    Expects JSON: {"message": "mensagem do usuário"}
    Returns JSON: {
        "response": "resposta da IA",
        "risk_level": "baixo|moderado|alto",
        "timestamp": "timestamp da resposta"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Mensagem não fornecida'
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                'error': 'Mensagem vazia'
            }), 400
        
        # Obter resposta da IA
        ai_response, risk_level = ai_service.get_ai_response(user_message)
        
        # Se for alto risco, adicionar resposta de crise
        if risk_level == 'alto':
            crisis_response = ai_service.get_crisis_response()
            ai_response = f"{ai_response}\n\n{crisis_response}"
        
        return jsonify({
            'response': ai_response,
            'risk_level': risk_level,
            'timestamp': None  # Pode adicionar timestamp se necessário
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Tente novamente em alguns momentos'
        }), 500

@app.route('/api/chat/clear', methods=['POST'])
def api_clear_chat():
    """
    Limpa o histórico da conversa atual
    """
    try:
        ai_service.clear_conversation()
        return jsonify({
            'message': 'Conversa limpa com sucesso'
        })
    except Exception as e:
        return jsonify({
            'error': 'Erro ao limpar conversa'
        }), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """
    Endpoint para verificar saúde da API
    """
    return jsonify({
        'status': 'ok',
        'service': 'PorVoce Suporte Emocional IA',
        'ai_service': 'OpenAI GPT-3.5-turbo'
    })

if __name__ == '__main__':
    app.run(debug=True)