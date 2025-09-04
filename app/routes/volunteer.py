"""
Rotas do dashboard do voluntário
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import ChatSession, ChatMessage

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
