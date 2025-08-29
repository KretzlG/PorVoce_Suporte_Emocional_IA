"""
Rotas principais da aplicação ForYou
"""

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from app.models import User
from app.models import ChatSession
from app import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')


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
            user_stats = {
                'total_chats': ChatSession.query.filter_by(user_id=current_user.id).count(),
                'total_assessments': 0,
                'last_activity': getattr(current_user, 'last_seen', None)
            }
            recent_entries = []
            last_assessment = None
            return render_template('dashboards/client/dashboard.html', 
                                 user_stats=user_stats,
                                 recent_entries=recent_entries,
                                 last_assessment=last_assessment)
        except Exception as e:
            current_app.logger.error(f"Erro no dashboard: {e}")
            user_stats = {
                'total_chats': 0,
                'total_assessments': 0,
                'last_activity': None
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


@main.errorhandler(429)
def rate_limit_exceeded(error):
    return render_template('errors/429.html'), 429
