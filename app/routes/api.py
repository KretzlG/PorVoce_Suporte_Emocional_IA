
"""
API REST simplificada para Por Você: apenas OpenAI, sem fallback, endpoints essenciais.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, ChatSession
from app import db
from datetime import datetime

api = Blueprint('api', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

# Sessões de chat
@api.route('/chat/sessions', methods=['GET'])
@jwt_required()
def get_chat_sessions():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    sessions = ChatSession.query.filter_by(user_id=user.id).order_by(ChatSession.started_at.desc()).all()
    return jsonify({'sessions': [session.to_dict() for session in sessions]})

@api.route('/chat/sessions/<int:session_id>/messages', methods=['GET'])
@jwt_required()
def get_chat_messages(session_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    session = ChatSession.query.filter_by(id=session_id, user_id=user.id).first()
    if not session:
        return jsonify({'error': 'Sessão não encontrada'}), 404
    messages = session.get_messages()
    return jsonify({'session': session.to_dict(), 'messages': messages})


# Consentimento
@api.route('/user/consent', methods=['PUT'])
@jwt_required()
def update_consent():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    data = request.get_json()
    try:
        if 'consent_data_usage' in data:
            user.consent_data_usage = data['consent_data_usage']
        if 'consent_ai_analysis' in data:
            user.consent_ai_analysis = data['consent_ai_analysis']
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'user': user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar consentimentos'}), 500


# APIs para Vue.js Dashboard
@api.route('/user/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Estatísticas do usuário para o dashboard"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    total_chats = ChatSession.query.filter_by(user_id=user.id).count()
    
    stats = {
        'total_chats': total_chats,
        'total_assessments': 0,  # Implementar futuramente
        'streak_days': 7,  # Implementar futuramente
        'last_activity': user.last_login.isoformat() if user.last_login else user.created_at.isoformat()
    }
    
    return jsonify(stats)


@api.route('/user/activities', methods=['GET'])
@jwt_required()
def get_user_activities():
    """Atividades recentes do usuário"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    recent_sessions = ChatSession.query.filter_by(user_id=user.id)\
        .order_by(ChatSession.created_at.desc()).limit(10).all()
    
    activities = []
    for session in recent_sessions:
        activities.append({
            'id': session.id,
            'title': session.title or f"Conversa de {session.created_at.strftime('%d/%m')}",
            'description': "Sessão de apoio emocional",
            'time': session.created_at.isoformat(),
            'icon': 'mdi-chat',
            'color': 'primary'
        })
    
    return jsonify({'activities': activities})


@api.route('/user/mood', methods=['POST'])
@jwt_required()
def save_mood():
    """Salvar humor do usuário"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    data = request.get_json()
    mood = data.get('mood')
    notes = data.get('notes', '')
    
    if not mood:
        return jsonify({'error': 'Humor é obrigatório'}), 400
    
    # Aqui você pode salvar o humor em uma tabela específica
    # Por enquanto, vamos apenas retornar sucesso
    return jsonify({'success': True, 'message': 'Humor salvo com sucesso'})


@api.route('/emergency/contacts', methods=['GET'])
def get_emergency_contacts():
    """Contatos de emergência"""
    contacts = [
        {
            'name': 'CVV - Centro de Valorização da Vida',
            'phone': '188',
            'description': 'Apoio emocional e prevenção ao suicídio 24h',
            'color': 'red'
        },
        {
            'name': 'CAPS - Centro de Atenção Psicossocial',
            'phone': '0800 644 0144',
            'description': 'Rede de atenção psicossocial',
            'color': 'blue'
        },
        {
            'name': 'SAMU',
            'phone': '192',
            'description': 'Emergências médicas',
            'color': 'red'
        },
        {
            'name': 'Polícia Militar',
            'phone': '190',
            'description': 'Emergências policiais',
            'color': 'blue'
        }
    ]
    
    return jsonify({'contacts': contacts})
