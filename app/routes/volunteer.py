from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from app.models import User, Volunteer
from app.models.chat1a1 import Chat1a1Session, Chat1a1Message
from app.models.triage import TriageLog
from app import db
from datetime import datetime
from datetime import datetime, timezone
import sqlalchemy as sa

volunteer = Blueprint('volunteer', __name__)

@volunteer.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """Estatísticas dinâmicas para dashboard do voluntário"""
    try:
        stats = {
            'sessions': 0,
            'users_helped': 0,
            'last_session': 'N/A',
        }
        recent_activities = []
        if hasattr(current_user, 'volunteer') and current_user.volunteer:
            volunteer_id = current_user.volunteer.id
            # Total de atendimentos
            stats['sessions'] = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).count()
            # Usuários únicos atendidos
            stats['users_helped'] = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).distinct(Chat1a1Session.user_id).count()
            # Último atendimento
            last_session = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).order_by(Chat1a1Session.started_at.desc()).first()
            if last_session and last_session.started_at:
                stats['last_session'] = last_session.started_at.strftime('%d/%m/%Y %H:%M')
            # Atividades recentes (últimas sessões)
            sessions = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).order_by(Chat1a1Session.started_at.desc()).limit(10).all()
            for s in sessions:
                user = s.user
                recent_activities.append(f"Atendimento a {user.first_name if user else 'Usuário'} em {s.started_at.strftime('%d/%m/%Y %H:%M') if s.started_at else ''}")
        return jsonify({
            'stats': stats,
            'recent_activities': recent_activities
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao buscar dados do dashboard', 'details': str(e)}), 500
@volunteer.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """Estatísticas dinâmicas para dashboard do voluntário"""
    try:
        stats = {
            'sessions': 0,
            'users_helped': 0,
            'last_session': 'N/A',
        }
        recent_activities = []
        if hasattr(current_user, 'volunteer') and current_user.volunteer:
            volunteer_id = current_user.volunteer.id
            # Total de atendimentos
            stats['sessions'] = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).count()
            # Usuários únicos atendidos
            stats['users_helped'] = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).distinct(Chat1a1Session.user_id).count()
            # Último atendimento
            last_session = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).order_by(Chat1a1Session.started_at.desc()).first()
            if last_session and last_session.started_at:
                stats['last_session'] = last_session.started_at.strftime('%d/%m/%Y %H:%M')
            # Atividades recentes (últimas sessões)
            sessions = Chat1a1Session.query.filter_by(volunteer_id=volunteer_id).order_by(Chat1a1Session.started_at.desc()).limit(10).all()
            for s in sessions:
                user = s.user
                recent_activities.append(f"Atendimento a {user.first_name if user else 'Usuário'} em {s.started_at.strftime('%d/%m/%Y %H:%M') if s.started_at else ''}")
        return jsonify({
            'stats': stats,
            'recent_activities': recent_activities
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao buscar dados do dashboard', 'details': str(e)}), 500

"""
Rotas do dashboard do voluntário
"""


from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from app.models import User, Volunteer
from app.models.chat1a1 import Chat1a1Session, Chat1a1Message
from app.models.triage import TriageLog
from app import db
from datetime import datetime
from datetime import datetime, timezone
import sqlalchemy as sa

volunteer = Blueprint('volunteer', __name__)

@volunteer.errorhandler(404)
def not_found_volunteer(error):
    return render_template('errors/404.html'), 404

@volunteer.errorhandler(500)
def internal_error_volunteer(error):
    return render_template('errors/500.html'), 500

@volunteer.route('/dashboard')
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
@login_required
def new_service():
    """Lista de clientes esperando atendimento"""
    # Buscar todas as sessões em espera, ordenadas por prioridade e data
    waiting_sessions = Chat1a1Session.query.filter(
        Chat1a1Session.status == 'WAITING',
        Chat1a1Session.volunteer_id == None
    ).order_by(
        # Prioridade: critical > high > normal
        sa.case(
            (Chat1a1Session.priority_level == 'critical', 1),
            (Chat1a1Session.priority_level == 'high', 2),
            else_=3
        ),
        Chat1a1Session.started_at.asc()  # Mais antigos primeiro
    ).all()
    
    # Criar lista com informações completas dos clientes
    clients_waiting = []
    for session in waiting_sessions:
        client = session.user
        
        # Buscar a triagem mais recente do cliente
        triage_log = TriageLog.query.filter_by(user_id=client.id).order_by(TriageLog.created_at.desc()).first()
        
        client_info = {
            'session': session,
            'client': client,
            'triage_log': triage_log,
            'waiting_time': datetime.now(timezone.utc) - session.started_at,
            'priority_label': {
                'critical': 'Urgente',
                'high': 'Alto',
                'normal': 'Normal'
            }.get(session.priority_level, 'Normal'),
            'priority_color': {
                'critical': '#d63031',
                'high': '#e17055', 
                'normal': '#00b894'
            }.get(session.priority_level, '#00b894')
        }
        clients_waiting.append(client_info)
    
    return render_template('volunteer/new_service_list.html', clients_waiting=clients_waiting)


@volunteer.route('/new_service/<int:session_id>')
@login_required
def view_client_details(session_id):
    """Visualizar detalhes de um cliente específico"""
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se a sessão ainda está em espera
    if session.status != 'WAITING':
        return redirect(url_for('volunteer.new_service'))
    
    client = session.user
    
    # Buscar a triagem mais recente do cliente
    triage_log = TriageLog.query.filter_by(user_id=client.id).order_by(TriageLog.created_at.desc()).first()
    
    return render_template('volunteer/client_details.html', 
                         session=session, 
                         client=client, 
                         triage_log=triage_log)


@volunteer.route('/accept_client/<int:session_id>')
@login_required
def accept_client(session_id):
    """Aceitar um cliente e iniciar chat 1a1"""
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se a sessão ainda está disponível
    if session.status != 'WAITING':
        return redirect(url_for('volunteer.new_service'))
    
    # Criar ou obter voluntário
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer:
        volunteer = Volunteer(user_id=current_user.id)
        db.session.add(volunteer)
        db.session.commit()
    
    # Atribuir voluntário à sessão
    session.volunteer_id = volunteer.id
    session.status = 'ACTIVE'
    db.session.commit()
    
    # Redirecionar para o chat
    return redirect(url_for('volunteer.client_chat', session_id=session_id))


@volunteer.route('/video_call/<int:session_id>')
@login_required
def video_call(session_id):
    """Iniciar chamada de vídeo com cliente"""
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se a sessão ainda está disponível
    if session.status != 'WAITING':
        return redirect(url_for('volunteer.new_service'))
    
    # Criar ou obter voluntário
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer:
        volunteer = Volunteer(user_id=current_user.id)
        db.session.add(volunteer)
        db.session.commit()
    
    # Atribuir voluntário à sessão e iniciar vídeo
    session.volunteer_id = volunteer.id
    session.status = 'ACTIVE'
    db.session.commit()
    
    # TODO: Implementar notificação para o cliente sobre chamada de vídeo
    # Por enquanto, redirecionar para o chat
    return redirect(url_for('volunteer.client_chat', session_id=session_id))


@volunteer.route('/reject_client/<int:session_id>')
@login_required
def reject_client(session_id):
    """Não aceitar um cliente específico"""
    # Por enquanto, apenas redirecionar de volta
    # TODO: Implementar lógica para marcar que este voluntário não pode atender este cliente
    return redirect(url_for('volunteer.new_service'))


@volunteer.route('/client_chat/<int:session_id>')
@login_required
def client_chat(session_id):
    """Chat 1a1 entre voluntário e cliente"""
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se a sessão está ativa
    if session.status != 'ACTIVE':
        return "Sessão não está ativa", 404
        
    # Verificar se o voluntário atual está atribuído a esta sessão
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer or session.volunteer_id != volunteer.id:
        return "Acesso negado a esta sessão", 403
    
    client = session.user
    messages = session.messages.order_by(Chat1a1Message.created_at.asc()).all()
    google_meet_url = 'https://meet.google.com/new'
    
    return render_template('chat/chat_1a1.html', 
                         client=client, 
                         google_meet_url=google_meet_url, 
                         messages=messages, 
                         session=session)


@volunteer.route('/client_chat/<int:session_id>/send', methods=['POST'])
@login_required
def client_send_message(session_id):
    """Enviar mensagem no chat 1a1"""
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se a sessão está ativa
    if session.status != 'ACTIVE':
        return {"error": "Sessão não está ativa"}, 404
        
    # Verificar se o usuário pode enviar mensagens nesta sessão
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    is_volunteer = volunteer and session.volunteer_id == volunteer.id
    is_client = session.user_id == current_user.id
    
    if not (is_volunteer or is_client):
        return {"error": "Acesso negado a esta sessão"}, 403
    
    data = request.get_json()
    content = data.get('content')
    
    if content:
        # Criar nova mensagem
        message = Chat1a1Message(
            session_id=session.id,
            sender_id=current_user.id,
            content=content,
            message_type='volunteer' if is_volunteer else 'client'
        )
        
        db.session.add(message)
        session.message_count += 1
        db.session.commit()
    
    return {"success": True}


@volunteer.route('/api/messages/<int:session_id>')
@login_required
def get_messages(session_id):
    """Buscar mensagens do chat 1a1"""
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se o usuário pode ver as mensagens
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    is_volunteer = volunteer and session.volunteer_id == volunteer.id
    is_client = session.user_id == current_user.id
    
    if not (is_volunteer or is_client):
        return {"error": "Acesso negado a esta sessão"}, 403
    
    messages = session.messages.order_by(Chat1a1Message.created_at.asc()).all()
    
    messages_data = []
    for message in messages:
        # Buscar o nome do usuário diretamente do banco
        sender = User.query.get(message.sender_id)
        sender_name = sender.first_name if sender else 'Desconhecido'
        
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender_type': message.message_type,
            'sender_name': sender_name,
            'created_at': message.created_at.isoformat()
        })
    
    return jsonify({
        'success': True,
        'messages': messages_data,
        'session_status': session.status
    })


@volunteer.route('/end_session/<int:session_id>')
@login_required
def end_session(session_id):
    """Encerrar sessão de chat 1a1"""
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se o voluntário atual está atribuído a esta sessão
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer or session.volunteer_id != volunteer.id:
        return "Acesso negado a esta sessão", 403
    
    # Encerrar a sessão
    session.status = 'COMPLETED'
    session.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Atendimento encerrado com sucesso!', 'success')
    return redirect(url_for('volunteer.new_service'))
