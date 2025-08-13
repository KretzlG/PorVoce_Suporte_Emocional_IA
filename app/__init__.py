"""
ForYou - Plataforma de Suporte Emocional com IA
Aplicação Flask principal
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Extensões
db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()

# Serviços
try:
    from app.services.ai_service import AIService
    ai_service = AIService()
    AI_AVAILABLE = True
except Exception as e:
    print(f"⚠️  AI Service não disponível: {e}")
    ai_service = None
    AI_AVAILABLE = False


def configure_logging(app):
    """Configura sistema de logging da aplicação"""
    
    # Nível de log baseado na configuração
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # Silenciar logs desnecessários
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('transformers.pipelines').setLevel(logging.WARNING)
    
    # Formato dos logs
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Log para arquivo se habilitado
    if app.config.get('LOG_TO_FILE', False):
        # Criar diretório de logs se não existir
        log_dir = os.path.dirname(app.config.get('LOG_FILE_PATH', 'logs/foryou.log'))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE_PATH', 'logs/foryou.log'),
            maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),  # 10MB
            backupCount=app.config.get('LOG_BACKUP_COUNT', 5)
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    
    # Log para console em desenvolvimento (apenas WARNING e acima)
    if app.config.get('DEBUG', False):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.WARNING)  # Apenas warnings e erros no console
        app.logger.addHandler(stream_handler)


def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    # Importar explicitamente todos os modelos para garantir que o Alembic detecte as tabelas
    from app.models import (
        User, UserRole, ChatSession, ChatMessage, DiaryEntry,
        Volunteer, VolunteerSkill, VolunteerAvailability,
        TriageLog, RiskLevel, AdminLog, AdminAction
    )
    migrate.init_app(app, db, directory='migrations')
    
    # Configurar logging
    configure_logging(app)
    
    # Inicializar serviços
    if AI_AVAILABLE and ai_service:
        try:
            ai_service.init_app(app)
            print("✅ AI Service inicializado com sucesso")
        except Exception as e:
            print(f"⚠️  Erro ao inicializar AI Service: {e}")
    else:
        print("⚠️  AI Service desabilitado - funcionando sem IA")
    
    # Inicializar agendador de tarefas
    try:
        from app.services.scheduler import init_scheduler
        init_scheduler(app)
        print("✅ Agendador de tarefas inicializado com sucesso")
    except Exception as e:
        print(f"⚠️  Erro ao inicializar agendador: {e}")
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # Chat blueprint - Sistema de chat com IA
    from app.routes.chat import chat as chat_blueprint
    app.register_blueprint(chat_blueprint, url_prefix='/chat')

    # Diary blueprint - Diário emocional
    from app.routes.diary import diary as diary_blueprint
    app.register_blueprint(diary_blueprint, url_prefix='/diary')

    from app.routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # Volunteer blueprint - Dashboard do voluntário
    from app.routes.volunteer import volunteer as volunteer_blueprint
    app.register_blueprint(volunteer_blueprint, url_prefix='/volunteer')

    # API blueprint - APIs para integração
    from app.routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')    # Handler de erros
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Context processors
    @app.context_processor
    def inject_config():
        return dict(config=app.config)
    
    # Headers de segurança para produção
    @app.after_request
    def security_headers(response):
        if config_name == 'production':
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Printar todas as rotas registradas para depuração
    print("[DEBUG] Rotas registradas no Flask:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    return app
