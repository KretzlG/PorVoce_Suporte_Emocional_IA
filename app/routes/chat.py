"""
Rotas do chat com IA - Versão corrigida usando mensagens em JSON
"""

from flask import Blueprint, render_template, request, jsonify, session, current_app
from flask_login import login_required, current_user
from app.models import ChatSession
from app import db
from datetime import datetime, timezone, timedelta

# Importar ai_service condicionalmente
try:
    from app import ai_service, AI_AVAILABLE
except ImportError:
    ai_service = None
    AI_AVAILABLE = False

chat = Blueprint('chat', __name__)


@chat.route('/')
@login_required
def chat_interface():
    """Interface principal do chat"""
    return render_template('chat/interface.html')


@chat.route('/new-session', methods=['POST'])
@login_required
def new_session():
    """Criar nova sessão de chat ou retornar a ativa"""
    try:
        from app.models import ChatSessionStatus
        # Procurar sessão ativa
        active_session = ChatSession.query.filter_by(
            user_id=current_user.id,
            status=ChatSessionStatus.ACTIVE.value
        ).first()
        if active_session:
            return jsonify({
                'success': True,
                'session_id': active_session.id,
                'session_uuid': active_session.uuid,
                'message': 'Sessão ativa já existente'
            })
        # Se não houver, criar nova sessão
        new_chat_session = ChatSession(
            user_id=current_user.id,
            title=f"Chat {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}",
            status=ChatSessionStatus.ACTIVE.value
        )
        db.session.add(new_chat_session)
        db.session.commit()
        # Adicionar mensagem de boas-vindas
        from app.models import ChatMessageType
        welcome_text = "Olá! Sou seu assistente de apoio emocional. Como você está se sentindo hoje?"
        new_chat_session.add_message(
            content=welcome_text,
            message_type=ChatMessageType.AI
        )
        db.session.commit()
        return jsonify({
            'success': True,
            'session_id': new_chat_session.id,
            'session_uuid': new_chat_session.uuid,
            'message': 'Nova sessão criada com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500



# Endpoint padronizado para envio de mensagem e resposta da IA (OpenAI only)
@chat.route('/api/chat/send', methods=['POST'])
@login_required
def api_chat_send():
    """Enviar mensagem e receber resposta da IA (OpenAI only)"""
    data = request.get_json()
    message_content = data.get('message', '').strip()
    session_id = data.get('session_id')
    if not message_content:
        return jsonify({'success': False, 'error': 'Mensagem não pode estar vazia'}), 400
    if not session_id:
        return jsonify({'success': False, 'error': 'ID da sessão é obrigatório'}), 400
    from app.models import ChatMessageType, ChatSessionStatus
    try:
        # OTIMIZAÇÃO: Query mais eficiente
        chat_session = ChatSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id, 
            status=ChatSessionStatus.ACTIVE.value
        ).first()
        
        if not chat_session:
            return jsonify({'success': False, 'error': 'Sessão de chat não encontrada ou inativa'}), 404
        
        # OTIMIZAÇÃO: Uma única transação para tudo
        try:
            # Adicionar mensagem do usuário
            user_message = chat_session.add_message(
                content=message_content, 
                message_type=ChatMessageType.USER, 
                sender_id=current_user.id
            )
            
            # Gerar resposta da IA (OpenAI only)
            if AI_AVAILABLE and ai_service and ai_service.openai_client:
                # OTIMIZAÇÃO: Buscar apenas mensagens recentes
                recent_messages = chat_session.get_recent_messages(10)
                
                ai_response = ai_service.generate_response(
                    user_message=message_content,
                    risk_level='low',  # Ajustar se necessário
                    user_context={'name': current_user.first_name}
                )
                
                # Adicionar resposta da IA
                ai_message = chat_session.add_message(
                    content=ai_response['message'], 
                    message_type=ChatMessageType.AI
                )
                
                # OTIMIZAÇÃO: Commit único para ambas as mensagens
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'user_message': {
                        'content': message_content,
                        'timestamp': user_message.created_at.isoformat(),
                        'sender_type': 'user'
                    },
                    'ai_response': {
                        'content': ai_response['message'],
                        'timestamp': ai_message.created_at.isoformat(),
                        'sender_type': 'ai'
                    }
                })
            else:
                # Só mensagem do usuário
                db.session.commit()
                return jsonify({'success': False, 'error': 'OpenAI não configurado ou indisponível'}), 503
                
        except Exception as e:
            db.session.rollback()
            raise e
    except Exception as e:
        current_app.logger.error(f"Erro ao processar mensagem: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500



# Endpoint padronizado para recuperar histórico de mensagens
@chat.route('/api/chat/receive', methods=['GET'])
@login_required
def api_chat_receive():
    """Recuperar histórico de mensagens - OTIMIZADO"""
    session_id = request.args.get('session_id', type=int)
    limit = request.args.get('limit', default=50, type=int)  # Limitar mensagens
    offset = request.args.get('offset', default=0, type=int)
    
    if not session_id:
        return jsonify({'success': False, 'error': 'ID da sessão é obrigatório'}), 400
    
    # Limitar o número máximo de mensagens para evitar sobrecarga
    limit = min(limit, 100)  # Máximo 100 mensagens por request
    
    try:
        chat_session = ChatSession.query.filter_by(
            id=session_id, 
            user_id=current_user.id
        ).first()
        
        if not chat_session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        # OTIMIZAÇÃO: Usar método paginado
        messages = chat_session.get_messages(limit=limit, offset=offset)
        
        # Se não houver mensagens, adiciona mensagem de boas-vindas temporária
        if not messages and offset == 0:
            messages = [{
                'id': 0,
                'session_id': chat_session.id,
                'sender_id': None,
                'content': 'Olá! Sou seu assistente de apoio emocional. Como você está se sentindo hoje?',
                'message_type': 'ai',
                'sentiment_score': None,
                'ai_model_used': None,
                'ai_confidence': None,
                'processing_time_ms': None,
                'created_at': chat_session.started_at.isoformat() if chat_session.started_at else None,
                'is_anonymized': False
            }]
        
        return jsonify({
            'success': True, 
            'messages': messages,
            'total_messages': chat_session.message_count,
            'has_more': (offset + len(messages)) < chat_session.message_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar mensagens: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@chat.route('/end-session/<int:session_id>', methods=['POST'])
@login_required
def end_session(session_id):
    """Finalizar sessão de chat"""
    from app.models import ChatSessionStatus, ChatMessageType
    try:
        chat_session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
            status=ChatSessionStatus.ACTIVE.value
        ).first()
        if not chat_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada ou já finalizada'
            }), 404
        # Finalizar sessão
        chat_session.status = ChatSessionStatus.COMPLETED.value
        chat_session.ended_at = datetime.now(timezone.utc)
        chat_session.calculate_duration()
        # Adicionar mensagem de despedida
        farewell_text = "Obrigado por conversar comigo hoje. Cuide-se bem e lembre-se: você nunca está sozinho(a)."
        chat_session.add_message(
            content=farewell_text,
            message_type=ChatMessageType.AI
        )
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Sessão finalizada com sucesso',
            'duration_minutes': chat_session.duration_minutes
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao finalizar sessão: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
@chat.route('/sessions')
@login_required
def user_sessions():
    """Listar sessões do usuário - OTIMIZADO"""
    try:
        # OTIMIZAÇÃO: Adicionar limit para evitar sobrecarga
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        limit = min(limit, 50)  # Máximo 50 sessões por request
        
        sessions = ChatSession.query.filter_by(user_id=current_user.id)\
            .order_by(ChatSession.started_at.desc())\
            .limit(limit).offset(offset).all()
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'uuid': session.uuid,
                'title': session.title,
                'status': session.status,
                'risk_level': session.initial_risk_level,  # Usar campo direto
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                'duration_minutes': session.duration_minutes,
                'message_count': session.message_count  # OTIMIZAÇÃO: Usar campo calculado
            })
        
        # Contar total de sessões para paginação
        total_sessions = ChatSession.query.filter_by(user_id=current_user.id).count()
        
        return jsonify({
            'success': True,
            'sessions': sessions_data,
            'total_sessions': total_sessions,
            'has_more': (offset + len(sessions_data)) < total_sessions
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar sessões: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@chat.route('/check-session-status/<int:session_id>', methods=['GET'])
@login_required
def check_session_status(session_id):
    """Verifica se a sessão ainda está ativa"""
    try:
        from app.models import ChatSessionStatus
        chat_session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not chat_session:
            return jsonify({
                'success': False,
                'status': 'not_found',
                'message': 'Sessão não encontrada'
            }), 404
        
        is_active = chat_session.status == ChatSessionStatus.ACTIVE.value
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'status': chat_session.status,
            'is_active': is_active,
            'last_activity': chat_session.last_activity.isoformat() if chat_session.last_activity else None,
            'message': 'Sessão ativa' if is_active else 'Sessão foi encerrada por inatividade'
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar status da sessão: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500


def close_inactive_sessions(minutes=3):
    """Encerra sessões inativas há mais de X minutos - OTIMIZADO"""
    from app.models import ChatSession, ChatSessionStatus
    from sqlalchemy import update
    
    now = datetime.now(timezone.utc)
    limit = now - timedelta(minutes=minutes)
    
    # OTIMIZAÇÃO: Update em massa ao invés de carregar objetos
    result = db.session.execute(
        update(ChatSession)
        .where(
            (ChatSession.status == ChatSessionStatus.ACTIVE.value) &
            (ChatSession.last_activity < limit)
        )
        .values(
            status=ChatSessionStatus.COMPLETED.value,
            ended_at=now
        )
    )
    
    db.session.commit()
    return result.rowcount
