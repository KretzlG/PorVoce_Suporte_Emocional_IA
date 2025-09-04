"""
Rotas do dashboard do voluntário
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import ChatSession, ChatMessage, User, Volunteer, ChatSessionStatus, ChatMessageType

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
        # Contar sessões atendidas pelo voluntário (implementar quando tiver a lógica)
        stats['sessions'] = ChatSession.query.filter_by(volunteer_id=current_user.volunteer.id).count()
        stats['messages'] = ChatMessage.query.join(ChatSession).filter(
            ChatSession.volunteer_id == current_user.volunteer.id
        ).count()
        stats['active_sessions'] = ChatSession.query.filter_by(
            volunteer_id=current_user.volunteer.id,
            status='active'
        ).count()
    
    return render_template('dashboards/volunteer/dashboard.html', user=current_user, stats=stats)

@volunteer.route('/new_service')
@login_required
def new_service():
    from app.models import User, Volunteer, ChatSession, ChatSessionStatus
    client = User.query.first()  # Exemplo: pega o primeiro usuário
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer:
        # Cria o registro de voluntário se não existir
        volunteer = Volunteer(user_id=current_user.id)
        volunteer.save()
    triage = {
        'reason': 'Ansiedade e estresse',
        'date': '04/09/2025'
    }
    ai_analysis = {
        'emotional_state': 'Ansioso',
        'risk_level': 'Baixo',
        'notes': 'Cliente demonstra preocupação com trabalho e rotina.'
    }
    # Buscar sessão ativa ou criar nova
    session = ChatSession.query.filter_by(user_id=client.id, volunteer_id=volunteer.id, status=ChatSessionStatus.ACTIVE.value).first()
    if not session:
        session = ChatSession(user_id=client.id, volunteer_id=volunteer.id, status=ChatSessionStatus.ACTIVE.value)
        session.title = f"Atendimento {client.first_name} {client.last_name}"
        session.save()
    return render_template('chat/service_intake.html', client=client, triage=triage, ai_analysis=ai_analysis, session=session)

@volunteer.route('/start_chat/<int:client_id>')
@login_required
def start_chat(client_id):
    from app.models import User, Volunteer, ChatSession, ChatSessionStatus, ChatMessage, ChatMessageType
    client = User.query.get(client_id)
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer:
        volunteer = Volunteer(user_id=current_user.id)
        volunteer.save()
    # Buscar sessão ativa ou criar nova
    session = ChatSession.query.filter_by(user_id=client.id, volunteer_id=volunteer.id, status=ChatSessionStatus.ACTIVE.value).first()
    if not session:
        session = ChatSession(user_id=client.id, volunteer_id=volunteer.id, status=ChatSessionStatus.ACTIVE.value)
        session.title = f"Atendimento {client.first_name} {client.last_name}"
        session.save()
    # Buscar mensagens
    messages = session.get_messages()
    google_meet_url = 'https://meet.google.com/new'
    return render_template('chat/chat_1a1.html', client=client, google_meet_url=google_meet_url, messages=messages, session=session)

@volunteer.route('/send_message/<int:session_id>', methods=['POST'])
@login_required
def send_message(session_id):
    from app.models import ChatSession, ChatMessageType
    session = ChatSession.query.get(session_id)
    if not session or not session.is_active:
        return "Sessão não encontrada ou encerrada", 404
    content = request.form.get('content')
    if content:
        session.add_message(content, message_type=ChatMessageType.VOLUNTEER, sender_id=current_user.id)
        session.save()
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
            session.save()
        return {"warning": "Sessão está encerrada, mensagem registrada apenas para histórico."}, 200
    data = request.get_json()
    content = data.get('content')
    if content:
        session.add_message(content, message_type=ChatMessageType.VOLUNTEER, sender_id=current_user.id)
        session.save()
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
    session = ChatSession.query.get(session_id)
    if not session or not session.is_active:
        return {"error": "Sessão não encontrada ou encerrada"}, 404
    data = request.get_json()
    content = data.get('content')
    if content:
        session.add_message(content, message_type=ChatMessageType.USER, sender_id=current_user.id)
        session.save()
    return {"success": True}
