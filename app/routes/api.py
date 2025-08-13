
"""
API REST simplificada para ForYou: apenas OpenAI, sem fallback, endpoints essenciais.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, ChatSession, DiaryEntry
from app import ai_service, db
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

# Diário
@api.route('/diary/entries', methods=['GET'])
@jwt_required()
def get_diary_entries():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    entries = DiaryEntry.query.filter_by(user_id=user.id).order_by(DiaryEntry.created_at.desc()).all()
    return jsonify({'entries': [entry.to_dict() for entry in entries]})

@api.route('/diary/entries', methods=['POST'])
@jwt_required()
def create_diary_entry():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    mood_score = data.get('mood_score')
    is_private = data.get('is_private', True)
    if not content:
        return jsonify({'error': 'Conteúdo é obrigatório'}), 400
    try:
        entry = DiaryEntry(user_id=user.id, title=title or f"Entrada de {datetime.now().strftime('%d/%m/%Y')}", content=content, mood_score=mood_score, is_private=is_private)
        db.session.add(entry)
        db.session.commit()
        return jsonify({'success': True, 'entry': entry.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar entrada', 'details': str(e)}), 500

@api.route('/diary/entries/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_diary_entry(entry_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    entry = DiaryEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        return jsonify({'error': 'Entrada não encontrada'}), 404
    return jsonify({'entry': entry.to_dict()})

@api.route('/diary/entries/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_diary_entry(entry_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    entry = DiaryEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        return jsonify({'error': 'Entrada não encontrada'}), 404
    data = request.get_json()
    try:
        if 'title' in data:
            entry.title = data['title'].strip()
        if 'content' in data:
            entry.content = data['content'].strip()
        if 'mood_score' in data:
            entry.mood_score = data['mood_score']
        if 'is_private' in data:
            entry.is_private = data['is_private']
        entry.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'entry': entry.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar entrada'}), 500

@api.route('/diary/entries/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_diary_entry(entry_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    entry = DiaryEntry.query.filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        return jsonify({'error': 'Entrada não encontrada'}), 404
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Entrada deletada'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar entrada'}), 500

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
