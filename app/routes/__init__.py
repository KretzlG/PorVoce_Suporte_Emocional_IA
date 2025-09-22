# Pacote de rotas da aplicação ForYou

def register_all_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    
    # Importar e registrar blueprints principais
    from .main import main as main_bp
    from .auth import auth as auth_bp
    from .chat import chat as chat_bp
    from .admin import admin as admin_bp
    from .api import api as api_bp
    from .training import training as training_bp
    from .training_api import register_training_api
    from .triage import triage as triage_bp
    from .volunteer import volunteer as volunteer_bp
    from .diary import diary as diary_bp
    
    # Registrar blueprints com prefixos apropriados
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(triage_bp)
    app.register_blueprint(volunteer_bp, url_prefix='/volunteer')
    app.register_blueprint(diary_bp)
    
    # Registrar API de treinamento avançada
    register_training_api(app)
