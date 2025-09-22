"""
ForYou - Plataforma de Suporte Emocional com IA
Aplicação Flask principal
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
    # Removido: mail = Mail()
login_manager = LoginManager()

def create_app():
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)


    # Tornar ai_service e AI_AVAILABLE globais
    from app.services.ai_service import AIService
    ai_service = AIService()
    AI_AVAILABLE = ai_service.openai_client is not None
    # Disponibilizar no pacote app
    import sys
    sys.modules['app'].ai_service = ai_service
    sys.modules['app'].AI_AVAILABLE = AI_AVAILABLE

    # Registrar todos os blueprints usando o novo sistema
    from app.routes import register_all_blueprints
    register_all_blueprints(app)

    return app
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



