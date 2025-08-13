
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
