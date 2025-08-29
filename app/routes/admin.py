
# ...existing code...
"""
Rotas administrativas
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, ChatSession
from app import db
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import or_
import json

admin = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator para rotas que requerem privilégios de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard administrativo"""
    # Estatísticas gerais
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_sessions': ChatSession.query.count(),
        'critical_alerts': 0
    }
    
    # Usuários recentes
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Alertas críticos recentes
    critical_alerts = []
    
    # Sessões ativas
    active_sessions = ChatSession.query.filter_by(status='active')\
        .order_by(ChatSession.started_at.desc()).limit(10).all()
    
    return render_template('dashboards/admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         critical_alerts=critical_alerts,
                         active_sessions=active_sessions)


@admin.route('/users')
@login_required
@admin_required
def users():
    """Gerenciamento de usuários"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = User.query
    
    if search:
        search_pattern = f'%{search}%'
        # pylint: disable=no-member  # SQLAlchemy dynamic attributes
        query = query.filter(or_(
            User.username.like(search_pattern),
            User.email.like(search_pattern),
            User.first_name.like(search_pattern),
            User.last_name.like(search_pattern)
        ))
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    users = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users, search=search, status_filter=status_filter)


@admin.route('/users/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    """Detalhes de um usuário específico"""
    user = User.query.get_or_404(user_id)
    
    # Estatísticas do usuário
    user_stats = {
        'total_sessions': ChatSession.query.filter_by(user_id=user.id).count(),
        'risk_assessments': 0
    }
    
    # Sessões recentes
    recent_sessions = ChatSession.query.filter_by(user_id=user.id)\
        .order_by(ChatSession.started_at.desc()).limit(5).all()
    
    # Avaliações de risco recentes
    recent_risks = []
    
    return render_template('admin/user_details.html',
                         user=user,
                         user_stats=user_stats,
                         recent_sessions=recent_sessions,
                         recent_risks=recent_risks)


@admin.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Ativar/desativar usuário"""
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'ativado' if user.is_active else 'desativado'
        return jsonify({
            'success': True,
            'message': f'Usuário {status} com sucesso',
            'is_active': user.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erro ao alterar status do usuário'
        }), 500


@admin.route('/alerts')
@login_required
@admin_required
def alerts():
    """Alertas de risco"""
    page = request.args.get('page', 1, type=int)
    risk_level = request.args.get('risk_level', '')
    
    alerts = []
    return render_template('admin/alerts.html', alerts=alerts, risk_level=risk_level)


@admin.route('/alerts/<int:alert_id>')
@login_required
@admin_required
def alert_details(alert_id):
    """Detalhes de um alerta específico"""
    alert = None
    user = None
    source_content = None
    return render_template('admin/alert_details.html',
                         alert=alert,
                         user=user,
                         source_content=source_content)


@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics e relatórios"""
    # Período para análise (últimos 30 dias)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Estatísticas por período
    daily_stats = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        daily_data = {
            'date': current_date.strftime('%Y-%m-%d'),
            'new_users': User.query.filter(
                User.created_at >= current_date,
                User.created_at < next_date
            ).count(),
            'new_sessions': ChatSession.query.filter(
                ChatSession.started_at >= current_date,
                ChatSession.started_at < next_date
            ).count(),
            'risk_alerts': 0
        }
        daily_stats.append(daily_data)
        current_date = next_date
    # Distribuição de níveis de risco
    risk_distribution = {level: 0 for level in ['low', 'moderate', 'high', 'critical']}
    
    # Top emoções removido
    return render_template('admin/analytics.html',
                         daily_stats=daily_stats,
                         risk_distribution=risk_distribution,
                         start_date=start_date,
                         end_date=end_date)


@admin.route('/settings')
@login_required
@admin_required
def settings():
    """Configurações do sistema"""
    return render_template('admin/settings.html')


@admin.route('/export/users')
@login_required
@admin_required
def export_users():
    """Exportar dados de usuários (anonimizados)"""
    users = User.query.all()
    
    export_data = {
        'export_date': datetime.utcnow().isoformat(),
        'total_users': len(users),
        'users': []
    }
    
    for user in users:
        export_data['users'].append({
            'id': user.id,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'consent_data_usage': user.consent_data_usage,
            'consent_ai_analysis': user.consent_ai_analysis
        })
    
    return jsonify(export_data)


@admin.route('/export/analytics')
@login_required
@admin_required
def export_analytics():
    """Exportar dados de analytics (anonimizados)"""
    # Estatísticas gerais
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_sessions': ChatSession.query.count(),
        'total_messages': sum(len(session.get_messages()) for session in ChatSession.query.all()),
    # 'total_diary_entries' removido
        'total_risk_assessments': 0
    }
    # Distribuição de risco
    risk_stats = {level: 0 for level in ['low', 'moderate', 'high', 'critical']}
    # Estatísticas por mês (últimos 12 meses)
    monthly_stats = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        monthly_data = {
            'month': month_start.strftime('%Y-%m'),
            'new_users': User.query.filter(
                User.created_at >= month_start,
                User.created_at <= month_end
            ).count(),
            'sessions': ChatSession.query.filter(
                ChatSession.started_at >= month_start,
                ChatSession.started_at <= month_end
            ).count(),
            'risk_alerts': 0
        }
        monthly_stats.append(monthly_data)
    export_data = {
        'export_date': datetime.utcnow().isoformat(),
        'general_stats': stats,
        'risk_distribution': risk_stats,
        'monthly_trends': monthly_stats
    }
    return jsonify(export_data)


# API endpoints para dashboard em tempo real
@admin.route('/api/dashboard-stats')
@login_required
@admin_required
def api_dashboard_stats():
    """Estatísticas em tempo real para dashboard"""
    # Alertas críticos nas últimas 24h
    yesterday = datetime.utcnow() - timedelta(days=1)
    critical_alerts_24h = 0
    
    # Sessões ativas
    active_sessions = ChatSession.query.filter_by(status='active').count()
    
    # Novos usuários hoje
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_users_today = User.query.filter(User.created_at >= today).count()
    
    return jsonify({
        'critical_alerts_24h': critical_alerts_24h,
        'active_sessions': active_sessions,
        'new_users_today': new_users_today,
        'timestamp': datetime.utcnow().isoformat()
    })


# Rotas de gerenciamento de voluntários
@admin.route('/volunteers')
@login_required
@admin_required
def volunteers():
    """Gerenciamento de voluntários"""
    from app.models import Volunteer
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    specialty_filter = request.args.get('specialty', '')
    
    query = Volunteer.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if specialty_filter:
        query = query.filter(Volunteer.specialization.contains([specialty_filter]))
    
    volunteers = query.order_by(Volunteer.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Estatísticas
    stats = {
        'total': Volunteer.query.count(),
        'active': Volunteer.query.filter_by(status='active').count(),
        'pending': Volunteer.query.filter_by(status='pending').count(),
        'inactive': Volunteer.query.filter_by(status='inactive').count(),
    }
    
    return render_template('admin/volunteers.html', 
                         volunteers=volunteers, 
                         stats=stats,
                         status_filter=status_filter,
                         specialty_filter=specialty_filter)


@admin.route('/volunteers/<int:volunteer_id>')
@login_required
@admin_required
def volunteer_details(volunteer_id):
    """Detalhes de um voluntário específico"""
    from app.models import Volunteer
    volunteer = Volunteer.query.get_or_404(volunteer_id)
    assignments = []
    return render_template('admin/volunteer_details.html',
                         volunteer=volunteer,
                         assignments=assignments)


@admin.route('/volunteers/new', methods=['POST'])
@login_required
@admin_required
def create_volunteer():
    """Criar novo voluntário"""
    from app.models import Volunteer
    
    data = request.get_json()
    
    try:
        volunteer = Volunteer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            specialization=data.get('specialties', []),  # Corrigido para specialization
            profession=data.get('profession', 'Voluntário'),
            status='pending'
        )
        
        db.session.add(volunteer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Voluntário criado com sucesso',
            'volunteer_id': volunteer.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erro ao criar voluntário'
        }), 500


@admin.route('/volunteers/<int:volunteer_id>/status', methods=['POST'])
@login_required
@admin_required
def update_volunteer_status(volunteer_id):
    """Atualizar status do voluntário"""
    from app.models import Volunteer
    
    volunteer = Volunteer.query.get_or_404(volunteer_id)
    data = request.get_json()
    
    try:
        volunteer.status = data['status']
        volunteer.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Status do voluntário atualizado para {data["status"]}',
            'status': volunteer.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erro ao atualizar status do voluntário'
        }), 500
