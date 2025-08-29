
"""
API REST simplificada para Por Você: apenas OpenAI, sem fallback, endpoints essenciais.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_required, current_user
from app.models import User, ChatSession, TriageLog, RiskLevel
from app import db
from datetime import datetime

api = Blueprint('api', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

# Triagem
@api.route('/API/triage', methods=['POST'])
@login_required
def triage_endpoint():
    """Endpoint de triagem para compatibilidade"""
    try:
        data = request.get_json() or {}
        content = request.form.get('content', '') or data.get('content', '')
        context_type = data.get('context_type', 'form')
        
        if not content:
            return jsonify({'error': 'Conteúdo não fornecido'}), 400
        
        # Análise básica (implementar lógica de IA posteriormente)
        risk_level = RiskLevel.LOW
        confidence = 0.8
        
        # Criar log de triagem
        triage_log = TriageLog(
            user_id=current_user.id,
            risk_level=risk_level,
            context_type=context_type,
            trigger_content=content[:1000],
            analyzed_by_ai=True,
            confidence_score=confidence,
            ai_model_used='basic_analysis'
        )
        
        db.session.add(triage_log)
        db.session.commit()
        
        # Determinar redirecionamento baseado no papel do usuário
        if current_user.is_admin:
            redirect_url = '/admin/dashboard'
        elif current_user.is_volunteer:
            redirect_url = '/volunteer/dashboard'
        else:
            redirect_url = '/dashboard'
        
        return jsonify({
            'success': True,
            'risk_level': risk_level.value,
            'confidence': confidence,
            'triage_id': triage_log.id,
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro na API de triagem: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

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
