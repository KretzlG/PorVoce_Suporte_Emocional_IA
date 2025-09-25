"""
Rotas do chat com IA - Versão corrigida usando mensagens em JSON
"""

import json
from flask import Blueprint, render_template, request, jsonify, session, current_app
import random
from flask_login import login_required, current_user
from app.models import ChatSession
from app.models.chat import ChatSessionStatus
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
    return render_template('chat/chat.html')


@chat.route('/new-session', methods=['POST'])
@login_required
def new_session():
    """Criar nova sessão de chat sempre"""
    try:
        from app.models import ChatSessionStatus
        
        # Encerrar qualquer sessão ativa existente
        active_sessions = ChatSession.query.filter_by(
            user_id=current_user.id,
            status=ChatSessionStatus.ACTIVE.value
        ).all()
        
        for session in active_sessions:
            session.status = ChatSessionStatus.COMPLETED.value
            session.last_activity = datetime.now(timezone.utc)
        
        # Sempre criar uma nova sessão
        new_chat_session = ChatSession(
            user_id=current_user.id,
            title=f"Chat {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')}",
            status=ChatSessionStatus.ACTIVE.value
        )
        db.session.add(new_chat_session)
        db.session.commit()
        
        # Não adicionar mensagem de boas-vindas automática
        # A primeira mensagem será gerada quando o usuário enviar algo
        
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
        chat_session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
            status=ChatSessionStatus.ACTIVE.value
        ).first()
        if not chat_session:
            return jsonify({'success': False, 'error': 'Sessão de chat não encontrada ou inativa'}), 404

        # Análise de sentimento e risco
        sentiment_analysis = None
        detected_risk_level = 'low'
        if AI_AVAILABLE and ai_service and ai_service.openai_client:
            try:
                sentiment_analysis = ai_service.analyze_with_risk_assessment(message_content)
                detected_risk_level = sentiment_analysis.get('risk_level', 'low')
            except Exception:
                detected_risk_level = ai_service.assess_risk_level(message_content)

        # Adicionar mensagem do usuário
        user_message = chat_session.add_message(
            content=message_content,
            message_type=ChatMessageType.USER,
            sender_id=current_user.id
        )
        if sentiment_analysis:
            user_message.sentiment_score = sentiment_analysis.get('score')
            user_message.risk_indicators = json.dumps({
                'risk_level': detected_risk_level,
                'emotion': sentiment_analysis.get('emotion'),
                'intensity': sentiment_analysis.get('intensity'),
                'confidence': sentiment_analysis.get('confidence'),
                'requires_attention': sentiment_analysis.get('requires_attention', False),
                'timestamp': sentiment_analysis.get('timestamp')
            }, ensure_ascii=False)

        # Atualizar o nível de risco inicial da sessão se necessário
        if chat_session.initial_risk_level is None:
            chat_session.initial_risk_level = detected_risk_level
        else:
            risk_levels = {'low': 1, 'moderate': 2, 'high': 3, 'critical': 4}
            current_level = risk_levels.get(chat_session.initial_risk_level, 1)
            new_level = risk_levels.get(detected_risk_level, 1)
            if new_level > current_level:
                chat_session.initial_risk_level = detected_risk_level

        # Memória contextual: contar encaminhamentos para triagem nesta sessão
        triage_count = 0
        if hasattr(chat_session, 'triage_context') and chat_session.triage_context:
            try:
                triage_ctx = json.loads(chat_session.triage_context)
                if isinstance(triage_ctx, dict) and 'triage_events' in triage_ctx:
                    triage_count = len(triage_ctx['triage_events'])
            except Exception:
                pass

        # Detectar perguntas objetivas do usuário
        pergunta_num_encaminhamentos = any(
            p in message_content.lower() for p in [
                'quantas vezes', 'quantas vezes vc me encaminhou', 'quantas vezes fui encaminhado', 'quantas vezes você me encaminhou', 'vc tem um numero', 'você tem um número']
        )
        pergunta_problema = any(
            p in message_content.lower() for p in [
                'qual era o meu problema', 'qual era meu problema', 'qual meu problema', 'qual era o motivo']
        )
        pergunta_contato = any(
            p in message_content.lower() for p in [
                'contato de emergência', 'telefone de emergência', 'cvv', 'preciso de ajuda urgente']
        )

        # Preparar contexto do usuário
        user_context = {
            'name': getattr(current_user, 'first_name', ''),
            'triage_triggered': getattr(chat_session, 'triage_triggered', False),
            'triage_status': getattr(chat_session, 'triage_status', None),
            'triage_declined_reason': getattr(chat_session, 'triage_declined_reason', None),
            'triage_count': triage_count
        }

        # Buscar histórico de mensagens para contexto
        from app.models import ChatMessage
        conversation_history = db.session.query(ChatMessage).filter_by(
            session_id=chat_session.id
        ).order_by(ChatMessage.created_at.asc()).limit(10).all()
        history_list = []
        for msg in conversation_history:
            history_list.append({
                'content': msg.content,
                'message_type': msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type,
                'created_at': msg.created_at.isoformat()
            })

        # Resposta personalizada para perguntas objetivas
        def limitar_resposta(texto, limite=220):
            if texto and len(texto) > limite:
                # Cortar no final da frase mais próxima
                corte = texto[:limite]
                for sep in ['.', '?', '!']:
                    idx = corte.rfind(sep)
                    if idx != -1 and idx > 50:
                        return corte[:idx+1].rstrip()
                return corte.rstrip() + '...'
            return texto

        # Detectar solicitação explícita de encaminhamento
        solicitacao_encaminhamento = any(
            p in message_content.lower() for p in [
                'quero atendimento', 'quero ajuda', 'preciso de atendimento', 'preciso de ajuda', 'me encaminhe', 'encaminhamento', 'falar com profissional', 'falar com alguém']
        )

        # Personalização contextual: reconhecer mudança de decisão
        mudou_de_ideia = False
        if hasattr(chat_session, 'triage_status') and chat_session.triage_status == 'declined' and solicitacao_encaminhamento:
            mudou_de_ideia = True

        # Referenciar histórico de perda
        historico_perda = None
        for msg in history_list:
            if 'perdi minha familia' in msg['content'].lower() or 'eles se foram' in msg['content'].lower():
                historico_perda = msg['content']

        if pergunta_num_encaminhamentos:
            resposta = f"Durante esta sessão, você foi encaminhado para triagem {triage_count} vez(es). Se quiser conversar sobre isso, estou aqui para te ouvir."
            resposta = limitar_resposta(resposta)
        elif pergunta_problema:
            problema = None
            for msg in history_list:
                if msg['message_type'] == 'user':
                    problema = msg['content']
            resposta = f"Você relatou: '{problema}'" if problema else "Não encontrei um relato específico, mas estou aqui para te apoiar."
            resposta = limitar_resposta(resposta)
        elif pergunta_contato:
            resposta = "Se você precisa de ajuda urgente, pode ligar para o CVV (Centro de Valorização da Vida) no número 188. O serviço é gratuito e funciona 24h."
            resposta = limitar_resposta(resposta)
        elif solicitacao_encaminhamento:
            # Encaminhamento imediato para triagem SEM bloqueio por histórico
            resposta = "Entendi seu pedido. Vou te encaminhar para um profissional agora mesmo. Aguarde um momento, por favor."
            resposta = limitar_resposta(resposta)
            requires_triage = True
            # Registrar evento de triagem na memória contextual (sempre adiciona)
            triage_ctx = {}
            if hasattr(chat_session, 'triage_context') and chat_session.triage_context:
                try:
                    triage_ctx = json.loads(chat_session.triage_context)
                except Exception:
                    triage_ctx = {}
            if 'triage_events' not in triage_ctx:
                triage_ctx['triage_events'] = []
            triage_ctx['triage_events'].append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'risk_level': detected_risk_level,
                'message': message_content,
                'solicitacao_usuario': True,
                'forcar_triagem': True
            })
            chat_session.triage_context = json.dumps(triage_ctx, ensure_ascii=False)

            # Criar registro real em TriageLog
            try:
                from app.models.triage import TriageLog, RiskLevel
                risk_enum_map = {
                    'low': RiskLevel.LOW,
                    'moderate': RiskLevel.MODERATE,
                    'high': RiskLevel.HIGH,
                    'critical': RiskLevel.CRITICAL
                }
                triage_log = TriageLog(
                    user_id=current_user.id,
                    chat_session_id=chat_session.id,
                    risk_level=risk_enum_map.get(detected_risk_level, RiskLevel.MODERATE),
                    confidence_score=sentiment_analysis.get('confidence', 0.5) if sentiment_analysis else 0.5,
                    trigger_content=message_content[:500],
                    context_type='chat_message',
                    triage_status='waiting'
                )
                db.session.add(triage_log)
                db.session.flush()
                session['triage_id'] = triage_log.id
                triage_id = triage_log.id
            except Exception as e:
                triage_id = None
        else:
            # Chamar IA para resposta empática e variada
            resposta = None
            if AI_AVAILABLE and ai_service and ai_service.openai_client:
                try:
                    ai_response = ai_service.generate_response(
                        user_message=message_content,
                        risk_level=detected_risk_level,
                        user_context=user_context,
                        conversation_history=history_list
                    )
                    resposta = ai_response['message']
                except Exception:
                    resposta = None
            # Fallback manual se IA indisponível ou erro
            if not resposta:
                frases_variadas = []
                if mudou_de_ideia:
                    frases_variadas.append("Fico feliz que tenha decidido buscar ajuda agora! Vou te encaminhar para um profissional, ok?")
                if historico_perda:
                    frases_variadas.append(f"Você mencionou que perdeu sua família. Se quiser falar sobre suas lembranças ou sentimentos, estou aqui para ouvir sem julgamentos.")
                if detected_risk_level == 'critical':
                    frases_variadas.append("Sinto muito que esteja se sentindo assim. É importante buscar ajuda profissional. Ligue para o CVV no 188. Estou aqui para te apoiar.")
                elif detected_risk_level == 'high':
                    frases_variadas.append("Percebo que está passando por um momento difícil. Se quiser conversar, estou aqui para te ouvir. Você não está sozinho(a).")
                elif detected_risk_level == 'moderate':
                    frases_variadas.append("Entendo que está enfrentando desafios. Quer compartilhar mais sobre como está se sentindo?")
                # Explorar sentimentos
                frases_variadas.append("Como você está lidando com tudo isso?")
                frases_variadas.append("Se quiser compartilhar como está, pode contar comigo.")
                frases_variadas.append("Lembre-se: seus sentimentos são importantes.")
                resposta = random.choice(frases_variadas)
            resposta = limitar_resposta(resposta)
        else:
            # Chamar IA para resposta empática e variada
            if AI_AVAILABLE and ai_service and ai_service.openai_client:
                try:
                    ai_response = ai_service.generate_response(
                        user_message=message_content,
                        risk_level=detected_risk_level,
                        user_context=user_context,
                        conversation_history=history_list
                    )
                    resposta = ai_response['message']
                except Exception:
                    resposta = None
            else:
                resposta = None
            # Fallback manual se IA indisponível ou erro
            if not resposta:
                frases_variadas = []
                if mudou_de_ideia:
                    frases_variadas.append("Fico feliz que tenha decidido buscar ajuda agora! Vou te encaminhar para um profissional, ok?")
                if historico_perda:
                    frases_variadas.append(f"Você mencionou que perdeu sua família. Se quiser falar sobre suas lembranças ou sentimentos, estou aqui para ouvir sem julgamentos.")
                if detected_risk_level == 'critical':
                    frases_variadas.append("Sinto muito que esteja se sentindo assim. É importante buscar ajuda profissional. Ligue para o CVV no 188. Estou aqui para te apoiar.")
                elif detected_risk_level == 'high':
                    frases_variadas.append("Percebo que está passando por um momento difícil. Se quiser conversar, estou aqui para te ouvir. Você não está sozinho(a).")
                elif detected_risk_level == 'moderate':
                    frases_variadas.append("Entendo que está enfrentando desafios. Quer compartilhar mais sobre como está se sentindo?")
                # Explorar sentimentos
                frases_variadas.append("Como você está lidando com tudo isso?")
                frases_variadas.append("Se quiser compartilhar como está, pode contar comigo.")
                frases_variadas.append("Lembre-se: seus sentimentos são importantes.")
                resposta = random.choice(frases_variadas)
            resposta = limitar_resposta(resposta)

        # Evitar encaminhamento repetitivo: só sugerir triagem se risco for moderado/alto/crítico e não sugerir se já foi sugerido nesta sessão
        requires_triage = False
        if detected_risk_level in ['moderate', 'high', 'critical'] and triage_count == 0:
            requires_triage = True
            # Registrar evento de triagem na memória contextual
            triage_ctx = {}
            if hasattr(chat_session, 'triage_context') and chat_session.triage_context:
                try:
                    triage_ctx = json.loads(chat_session.triage_context)
                except Exception:
                    triage_ctx = {}
            if 'triage_events' not in triage_ctx:
                triage_ctx['triage_events'] = []
            triage_ctx['triage_events'].append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'risk_level': detected_risk_level,
                'message': message_content
            })
            chat_session.triage_context = json.dumps(triage_ctx, ensure_ascii=False)

        # Salvar resposta da IA
        ai_message = chat_session.add_message(
            content=resposta,
            message_type=ChatMessageType.AI
        )
        db.session.commit()

        response_data = {
            'success': True,
            'user_message': {
                'content': message_content,
                'timestamp': user_message.created_at.isoformat(),
                'sender_type': 'user'
            },
            'ai_response': {
                'content': resposta,
                'timestamp': ai_message.created_at.isoformat(),
                'sender_type': 'ai'
            },
            'risk_assessment': {
                'risk_level': detected_risk_level,
                'requires_triage': requires_triage,
                'triage_count': triage_count,
                'triage_id': triage_id if requires_triage else None
            }
        }
        return jsonify(response_data)
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


@chat.route('/api/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Obter histórico de conversas do usuário"""
    try:
        from app.models import ChatSession, ChatMessage
        from sqlalchemy import desc
        
        # Buscar todas as sessões do usuário, incluindo as finalizadas
        sessions = ChatSession.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(ChatSession.created_at)).limit(50).all()
        
        conversations = []
        for session in sessions:
            # Buscar última mensagem para prévia
            last_message = ChatMessage.query.filter_by(
                session_id=session.id
            ).order_by(desc(ChatMessage.created_at)).first()
            
            conversations.append({
                'id': session.id,
                'title': session.title or f"Conversa {session.created_at.strftime('%d/%m/%Y')}",
                'created_at': session.created_at.isoformat(),
                'status': session.status.value if hasattr(session.status, 'value') else session.status,
                'message_count': session.message_count,
                'last_message': last_message.content[:100] + '...' if last_message and len(last_message.content) > 100 else (last_message.content if last_message else 'Conversa iniciada')
            })
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao carregar conversas: {str(e)}'
        }), 500


@chat.route('/api/end-session', methods=['POST'])
@login_required
def api_end_session():
    from datetime import timezone, datetime
    """Encerrar sessão de chat ativa"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'ID da sessão é obrigatório'
            }), 400
        
        # Buscar sessão do usuário
        chat_session = db.session.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not chat_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        # Encerrar sessão com valor correto do enum
        chat_session.status = 'COMPLETED'
        chat_session.ended_at = datetime.now(timezone.utc)
        
        if chat_session.started_at and chat_session.ended_at:
            from datetime import timezone, datetime
            ended_at = chat_session.ended_at
            started_at = chat_session.started_at
            # Converter para datetime se vier como string
            if isinstance(ended_at, str):
                try:
                    ended_at = datetime.fromisoformat(ended_at)
                except Exception:
                    ended_at = datetime.utcnow().replace(tzinfo=timezone.utc)
            if isinstance(started_at, str):
                try:
                    started_at = datetime.fromisoformat(started_at)
                except Exception:
                    started_at = datetime.utcnow().replace(tzinfo=timezone.utc)
            # Garantir timezone
            if ended_at.tzinfo is None:
                ended_at = ended_at.replace(tzinfo=timezone.utc)
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            try:
                duration = ended_at - started_at
                chat_session.duration_minutes = int(duration.total_seconds() / 60)
            except Exception as e:
                current_app.logger.error(f'Erro ao calcular duração da sessão: {e}')
                chat_session.duration_minutes = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sessão encerrada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao encerrar sessão: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Erro ao encerrar sessão: {str(e)}'
        }), 500


@chat.route('/api/delete-conversation', methods=['DELETE'])
@login_required
def delete_conversation():
    """Excluir uma conversa específica"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'ID da sessão é obrigatório'
            }), 400
        
        from app.models import ChatSession
        
        # Buscar sessão do usuário
        chat_session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        
        if not chat_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        # CORREÇÃO: Deletar logs de triagem relacionados primeiro
        try:
            from app.models.triage import TriageLog
            related_triage_logs = TriageLog.query.filter_by(chat_session_id=session_id).all()
            for triage_log in related_triage_logs:
                db.session.delete(triage_log)
        except ImportError:
            # Se o modelo de triagem não existir, continuar
            pass
        except Exception as triage_error:
            current_app.logger.warning(f"Erro ao deletar logs de triagem: {triage_error}")
            # Não falhar por causa dos logs de triagem
        
        # Excluir sessão (cascade irá excluir mensagens)
        db.session.delete(chat_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Conversa excluída com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao excluir conversa: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Erro ao excluir conversa: {str(e)}'
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


@chat.route('/triage/initiated', methods=['POST'])
@login_required
def triage_initiated():
    """Marca que a triagem foi iniciada para a sessão atual"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'ID da sessão é obrigatório'
            }), 400
        
        # Buscar sessão ativa do usuário
        chat_session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
            status=ChatSessionStatus.ACTIVE.value
        ).first()
        
        if not chat_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada ou inativa'
            }), 404
        
        # Marcar triagem como iniciada
        chat_session.triage_triggered = True
        chat_session.triage_status = 'initiated'
        
        # Opcional: salvar contexto adicional
        triage_context = data.get('context', {})
        if triage_context:
            import json
            chat_session.triage_context = json.dumps(triage_context, ensure_ascii=False)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Triagem marcada como iniciada',
            'triage_status': 'initiated'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao marcar triagem iniciada: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500


@chat.route('/triage/declined', methods=['POST'])
@login_required
def triage_declined():
    """Marca que o usuário recusou a triagem"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        reason = data.get('reason', 'Não informado')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'ID da sessão é obrigatório'
            }), 400
        
        # Buscar sessão ativa do usuário
        chat_session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
            status=ChatSessionStatus.ACTIVE.value
        ).first()
        
        if not chat_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada ou inativa'
            }), 404
        
        # Marcar triagem como recusada
        chat_session.triage_triggered = True
        chat_session.triage_status = 'declined'
        chat_session.triage_declined_reason = reason
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Triagem marcada como recusada',
            'triage_status': 'declined'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao marcar triagem recusada: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500


@chat.route('/triage/completed', methods=['POST'])
@login_required
def triage_completed():
    """Marca que a triagem foi completada"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'ID da sessão é obrigatório'
            }), 400
        
        # Buscar sessão ativa do usuário
        chat_session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
            status=ChatSessionStatus.ACTIVE.value
        ).first()
        
        if not chat_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada ou inativa'
            }), 404
        
        # Marcar triagem como completada
        chat_session.triage_triggered = True
        chat_session.triage_status = 'completed'
        
        # Opcional: salvar resultados da triagem
        triage_results = data.get('results', {})
        if triage_results:
            import json
            existing_context = {}
            if chat_session.triage_context:
                try:
                    existing_context = json.loads(chat_session.triage_context)
                except:
                    pass
            
            existing_context.update({
                'results': triage_results,
                'completed_at': datetime.now(timezone.utc).isoformat()
            })
            
            chat_session.triage_context = json.dumps(existing_context, ensure_ascii=False)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Triagem marcada como completada',
            'triage_status': 'completed'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao marcar triagem completada: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
