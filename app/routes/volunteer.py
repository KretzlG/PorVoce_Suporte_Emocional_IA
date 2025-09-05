"""
Rotas do dashboard do voluntário
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Volunteer
from app.models.chat1a1 import Chat1a1Session, Chat1a1Message

volunteer = Blueprint('volunteer', __name__)

@volunteer.route('/volunteer/dashboard')
@login_required
def dashboard():
    # Estatísticas básicas do voluntário
    stats = {
        'sessions': 0,
        'messages': 0,
        'active_sessions': 0,
        'total_time': 0
    }
    
    # Se o usuário atual for um voluntário, calcular estatísticas reais
    if hasattr(current_user, 'volunteer') and current_user.volunteer:
        stats['sessions'] = Chat1a1Session.query.filter_by(volunteer_id=current_user.volunteer.id).count()
        stats['messages'] = Chat1a1Message.query.join(Chat1a1Session).filter(
            Chat1a1Session.volunteer_id == current_user.volunteer.id
        ).count()
        stats['active_sessions'] = Chat1a1Session.query.filter_by(
            volunteer_id=current_user.volunteer.id,
            status='ACTIVE'
        ).count()
    
    return render_template('dashboards/volunteer/dashboard.html', user=current_user, stats=stats)

@volunteer.route('/new_service')
@volunteer.route('/new_service/<int:triage_id>')
@login_required
def new_service(triage_id=None):
    from app.models import User, Volunteer, ChatSession, ChatSessionStatus, TriageLog, RiskLevel
    from app import db
    from datetime import datetime
    
    # Buscar triagem específica ou a mais recente
    if triage_id:
        triage_log = TriageLog.query.get(triage_id)
        if not triage_log:
            return "Triagem não encontrada", 404
    else:
        # Buscar a triagem mais recente que precisa de atendimento
        triage_log = TriageLog.query.filter_by(
            triage_status='waiting'
        ).order_by(TriageLog.created_at.desc()).first()
        
        if not triage_log:
            # Se não há triagens em espera, criar dados de exemplo para teste
            client = User.query.first()
            if not client:
                return "Nenhum usuário encontrado no sistema", 404
                
            volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
            if not volunteer:
                volunteer = Volunteer(user_id=current_user.id)
                db.session.add(volunteer)
                db.session.commit()
            
            triage = {
                'reason': 'Ansiedade e estresse',
                'date': '04/09/2025'
            }
            ai_analysis = {
                'emotional_state': 'Ansioso',
                'risk_level': 'Baixo',
                'notes': 'Cliente demonstra preocupação com trabalho e rotina.'
            }
            
            session = ChatSession.query.filter_by(
                user_id=client.id, 
                volunteer_id=volunteer.id, 
                status=ChatSessionStatus.ACTIVE.value
            ).first()
            if not session:
                session = ChatSession(
                    user_id=client.id, 
                    volunteer_id=volunteer.id, 
                    status=ChatSessionStatus.ACTIVE.value
                )
                session.title = f"Atendimento {client.first_name} {client.last_name}"
                db.session.add(session)
                db.session.commit()
            
            return render_template('chat/service_intake.html', 
                                 client=client, 
                                 triage=triage, 
                                 ai_analysis=ai_analysis, 
                                 session=session,
                                 is_example=True)
    
    # Dados reais da triagem
    client = triage_log.user
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer:
        volunteer = Volunteer(user_id=current_user.id)
        db.session.add(volunteer)
        db.session.commit()
    
    # Montar dados da triagem
    triage = {
        'reason': triage_log.action_details or 'Apoio emocional solicitado',
        'date': triage_log.created_at.strftime('%d/%m/%Y') if triage_log.created_at else 'Não informado'
    }
    
    # Montar análise da IA baseada nos dados reais
    risk_level_map = {
        RiskLevel.LOW: 'Baixo',
        RiskLevel.MODERATE: 'Moderado', 
        RiskLevel.HIGH: 'Alto',
        RiskLevel.CRITICAL: 'Crítico'
    }
    
    ai_analysis = {
        'emotional_state': triage_log.emotional_state or 'A avaliar',
        'risk_level': risk_level_map.get(triage_log.risk_level, 'Não avaliado'),
        'notes': triage_log.notes or 'Cliente solicita apoio profissional.'
    }
    
    # Buscar sessão ativa ou criar nova
    session = ChatSession.query.filter_by(
        user_id=client.id, 
        volunteer_id=volunteer.id, 
        status=ChatSessionStatus.ACTIVE.value
    ).first()
    if not session:
        session = ChatSession(
            user_id=client.id, 
            volunteer_id=volunteer.id, 
            status=ChatSessionStatus.ACTIVE.value
        )
        session.title = f"Atendimento {client.first_name} {client.last_name}"
        db.session.add(session)
        db.session.commit()
    
    # Atualizar status da triagem para 'em_atendimento'
    triage_log.triage_status = 'em_atendimento'
    triage_log.volunteer_assigned = volunteer.id
    db.session.commit()
    
    return render_template('chat/service_intake.html', 
                         client=client, 
                         triage=triage, 
                         ai_analysis=ai_analysis, 
                         session=session,
                         triage_log=triage_log)

@volunteer.route('/start_chat/<int:client_id>')
@login_required
def start_chat(client_id):
    from app.models import User, Volunteer, ChatSession, ChatSessionStatus, ChatMessage, ChatMessageType
    from app import db
    client = User.query.get(client_id)
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer:
        volunteer = Volunteer(user_id=current_user.id)
        db.session.add(volunteer)
        db.session.commit()
    # Buscar sessão ativa ou criar nova
    session = ChatSession.query.filter_by(user_id=client.id, volunteer_id=volunteer.id, status=ChatSessionStatus.ACTIVE.value).first()
    if not session:
        session = ChatSession(user_id=client.id, volunteer_id=volunteer.id, status=ChatSessionStatus.ACTIVE.value)
        session.title = f"Atendimento {client.first_name} {client.last_name}"
        db.session.add(session)
        db.session.commit()
    # Buscar mensagens
    messages = session.get_messages()
    google_meet_url = 'https://meet.google.com/new'
    return render_template('chat/chat_1a1.html', client=client, google_meet_url=google_meet_url, messages=messages, session=session)

@volunteer.route('/send_message/<int:session_id>', methods=['POST'])
@login_required
def send_message(session_id):
    from app.models import ChatSession, ChatMessageType
    from app import db
    session = ChatSession.query.get(session_id)
    if not session or not session.is_active:
        return "Sessão não encontrada ou encerrada", 404
    content = request.form.get('content')
    if content:
        session.add_message(content, message_type=ChatMessageType.VOLUNTEER, sender_id=current_user.id)
        db.session.commit()
    return redirect(url_for('volunteer.start_chat', client_id=session.user_id))

@volunteer.route('/api/messages/<int:session_id>')
@login_required
def api_get_messages(session_id):
    from app.models import ChatSession
    session = ChatSession.query.get(session_id)
    if not session:
        return {"messages": []}, 404
    messages = session.get_messages()
    client_name = session.user.name if hasattr(session.user, 'name') else 'Cliente'
    return {"messages": messages, "client_name": client_name}

@volunteer.route('/api/send_message/<int:session_id>', methods=['POST'])
@login_required
def api_send_message(session_id):
    from app.models import ChatSession, ChatMessageType
    from app import db
    import json
    session = ChatSession.query.get(session_id)
    if not session:
        return {"error": "Sessão não encontrada"}, 404
    # Permite envio mesmo se não estiver ativa, mas retorna aviso
    if not session.is_active:
        # Ainda salva a mensagem, mas marca como encerrada
        data = request.get_json()
        content = data.get('content')
        if content:
            session.add_message(f"[ATENÇÃO: Sessão encerrada] {content}", message_type=ChatMessageType.VOLUNTEER, sender_id=current_user.id)
            db.session.commit()
        return {"warning": "Sessão está encerrada, mensagem registrada apenas para histórico."}, 200
    data = request.get_json()
    content = data.get('content')
    if content:
        session.add_message(content, message_type=ChatMessageType.VOLUNTEER, sender_id=current_user.id)
        db.session.commit()
    return {"success": True}

@volunteer.route('/client_chat/<int:session_id>')
@login_required
def client_chat(session_id):
    from app.models import ChatSession, User
    session = ChatSession.query.get(session_id)
    if not session or not session.is_active:
        return "Sessão não encontrada ou encerrada", 404
    client = session.user
    google_meet_url = 'https://meet.google.com/new'
    messages = session.get_messages()
    return render_template('chat/chat_1a1.html', client=client, google_meet_url=google_meet_url, messages=messages, session=session)

@volunteer.route('/client_chat/<int:session_id>/send', methods=['POST'])
@login_required
def client_send_message(session_id):
    from app.models import ChatSession, ChatMessageType
    from app import db
    session = ChatSession.query.get(session_id)
    if not session or not session.is_active:
        return {"error": "Sessão não encontrada ou encerrada"}, 404
    data = request.get_json()
    content = data.get('content')
    if content:
        session.add_message(content, message_type=ChatMessageType.USER, sender_id=current_user.id)
        db.session.commit()
    return {"success": True}
