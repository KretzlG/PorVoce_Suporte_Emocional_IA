"""
Rotas principais da aplicação ForYou
"""

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app.models import User
from app.models import ChatSession
from app import db

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def index():
    """Página inicial"""
    return render_template('landing.html')


@main.route('/chat1a1')
@main.route('/chat1a1/<priority>')
@login_required
def chat1a1(priority='normal'):
    """Interface de chat cliente-voluntário (1a1)"""
    from app.models.chat1a1 import Chat1a1Session, Chat1a1Message
    from app.models.triage import TriageLog
    
    # Verificar se há uma sessão ativa para o cliente
    active_session = Chat1a1Session.query.filter_by(
        user_id=current_user.id,
        status='ACTIVE'
    ).first()
    
    if active_session:
        # Se há sessão ativa, redirecionar para a interface do cliente
        return redirect(url_for('main.client_chat_1a1', session_id=active_session.id))
    
    # Verificar se há uma sessão em espera
    waiting_session = Chat1a1Session.query.filter_by(
        user_id=current_user.id,
        status='WAITING'
    ).first()
    
    # Determinar prioridade baseada na URL ou parâmetro
    if priority not in ['normal', 'high', 'critical']:
        priority = 'normal'
    
    if waiting_session:
        # Atualizar prioridade se necessário
        if priority != 'normal' and waiting_session.priority_level == 'normal':
            waiting_session.priority_level = priority
            db.session.commit()
        
        # Se há sessão em espera, mostrar página de espera
        return render_template('chat/chat_1a1_waiting.html', session=waiting_session)
    
    # Buscar a última triagem do usuário para vincular
    latest_triage = TriageLog.query.filter_by(user_id=current_user.id).order_by(TriageLog.created_at.desc()).first()
    
    # Se não há sessão, criar uma nova solicitação
    new_session = Chat1a1Session(
        user_id=current_user.id,
        status='WAITING',
        title=f"Solicitação de apoio - {current_user.first_name}",
        priority_level=priority
    )
    
    db.session.add(new_session)
    db.session.commit()
    
    # Renderizar página de espera
    return render_template('chat/chat_1a1_waiting.html', session=new_session)


@main.route('/health')
def health_check():
    """Health check para testes"""
    try:
        # Verificar se o banco está acessível
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = True
    except:
        db_status = False
        
    return jsonify({
        'status': 'ok' if db_status else 'error',
        'database': 'connected' if db_status else 'disconnected',
        'timestamp': request.environ.get('REQUEST_TIME', 'unknown')
    }), 200 if db_status else 503


@main.route('/chat1a1/status/<int:session_id>')
@login_required
def chat1a1_status(session_id):
    """Verificar status da sessão 1a1"""
    from app.models.chat1a1 import Chat1a1Session
    
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se a sessão pertence ao usuário atual
    if session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'status': session.status,
        'volunteer_connected': session.volunteer_id is not None
    })


@main.route('/client_chat_1a1/<int:session_id>')
@login_required
def client_chat_1a1(session_id):
    """Interface do cliente para chat 1a1"""
    from app.models.chat1a1 import Chat1a1Session, Chat1a1Message
    
    session = Chat1a1Session.query.get_or_404(session_id)
    
    # Verificar se o usuário é o dono da sessão
    if session.user_id != current_user.id:
        return "Acesso negado", 403
    
    # Se a sessão ainda está esperando, mostrar página de espera
    if session.status == 'WAITING':
        return render_template('chat/chat_1a1_waiting.html', session=session)
    
    # Se a sessão está ativa, mostrar interface de chat
    if session.status == 'ACTIVE':
        volunteer = session.volunteer
        messages = session.messages.order_by(Chat1a1Message.created_at.asc()).all()
        
        return render_template('chat/chat_1a1_client.html', 
                             session=session, 
                             volunteer=volunteer, 
                             messages=messages)
    
    # Sessão completada
    return render_template('chat/chat_1a1_completed.html', session=session)


@main.route('/about')
def about():
    """Página sobre o projeto"""
    return render_template('about.html')


@main.route('/help')
def help_page():
    """Página de ajuda e recursos"""
    emergency_contacts = [
        {
            'name': 'CVV - Centro de Valorização da Vida',
            'phone': '188',
            'description': 'Apoio emocional e prevenção ao suicídio 24h'
        },
        {
            'name': 'SAMU',
            'phone': '192',
            'description': 'Emergências médicas'
        },
        {
            'name': 'Polícia Militar',
            'phone': '190',
            'description': 'Emergências policiais'
        },
        {
            'name': 'Bombeiros',
            'phone': '193',
            'description': 'Emergências de resgate'
        }
    ]
    
    return render_template('help.html', emergency_contacts=emergency_contacts)



@main.route('/dashboard')
@login_required
def dashboard():
    """Redireciona para o dashboard correto conforme o papel do usuário"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_volunteer:
        return redirect(url_for('volunteer.dashboard'))
    elif current_user.is_client:
        try:
            # Buscar dados do usuário
            total_chats = ChatSession.query.filter_by(user_id=current_user.id).count()
            
            # Preparar dados com valores seguros (sem None)
            user_stats = {
                'total_chats': total_chats,
                'total_assessments': 0,  # Funcionalidade futura
                'last_activity': current_user.last_login or current_user.created_at
            }
            
            # Buscar atividades recentes (sessões de chat)
            recent_sessions = ChatSession.query.filter_by(user_id=current_user.id)\
                .order_by(ChatSession.created_at.desc()).limit(5).all()
            
            recent_entries = []
            for session in recent_sessions:
                if session.title:
                    recent_entries.append({
                        'title': session.title,
                        'text': f"Conversa realizada em {session.created_at.strftime('%d/%m/%Y')}"
                    })
                else:
                    recent_entries.append({
                        'title': f"Conversa de {session.created_at.strftime('%d/%m/%Y')}",
                        'text': "Sessão de apoio emocional"
                    })
            
            return render_template('dashboards/client/dashboard.html', 
                                 user_stats=user_stats,
                                 recent_entries=recent_entries,
                                 last_assessment=None)
        except Exception as e:
            current_app.logger.error(f"Erro no dashboard: {e}")
            # Valores padrão seguros em caso de erro
            user_stats = {
                'total_chats': 0,
                'total_assessments': 0,
                'last_activity': datetime.now()
            }
            return render_template('dashboards/client/dashboard.html', 
                                 user_stats=user_stats,
                                 recent_entries=[],
                                 last_assessment=None)
    else:
        # Se não for nenhum papel conhecido, faz logout ou mostra erro
        return redirect(url_for('auth.logout'))





# Error handlers específicos para este blueprint
@main.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@main.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@main.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500



@main.errorhandler(429)
def rate_limit_exceeded(error):
    return render_template('errors/429.html'), 429
