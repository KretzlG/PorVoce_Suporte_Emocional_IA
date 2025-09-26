import os
from datetime import timedelta


class Config:
    """Configurações base da aplicação"""
    
    # Chave secreta para sessões e tokens
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Configuração do banco de dados - prioriza PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or \
    os.environ.get('DEV_DATABASE_URL') or \
    'postgresql://postgres:141520@localhost:5433/foryou_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False,
        'connect_args': {
            'client_encoding': 'utf8',
            'options': '-c client_encoding=utf8'
        }
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Upload de arquivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configurações de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurações da IA
    AI_MODEL_PATH = os.environ.get('AI_MODEL_PATH') or 'models/'
    SPACY_MODEL = 'pt_core_news_sm'  # Modelo em português
    HUGGINGFACE_MODEL = 'neuralmind/bert-base-portuguese-cased'
    
    # OpenAI Configuration - Motor principal de IA
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', '500'))
    OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', '0.5'))
    USE_LOCAL_MODELS = os.environ.get('USE_LOCAL_MODELS', 'true').lower() in ['true', 'on', '1']
    
    # Níveis de risco
    RISK_LEVELS = {
        'low': {'threshold': 0.3, 'color': 'green'},
        'moderate': {'threshold': 0.6, 'color': 'yellow'},
        'high': {'threshold': 0.8, 'color': 'orange'},
        'critical': {'threshold': 1.0, 'color': 'red'}
    }
    
    # APIs externas
    CVV_API_URL = os.environ.get('CVV_API_URL')
    CAPS_API_URL = os.environ.get('CAPS_API_URL')
    
    # Configurações de cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    LOG_TO_FILE = os.environ.get('LOG_TO_FILE', 'true').lower() in ['true', 'on', '1']
    LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH', 'logs/foryou.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
    
    # Configurações de conformidade LGPD/GDPR
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', '2555'))  # 7 anos
    ANONYMIZATION_ENABLED = os.environ.get('ANONYMIZATION_ENABLED', 'true').lower() in ['true', 'on', '1']
    AUTO_ANONYMIZE_AFTER_DAYS = int(os.environ.get('AUTO_ANONYMIZE_AFTER_DAYS', '365'))  # 1 ano


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    TESTING = False

    # ...existing code...
class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    DEBUG = True
    
    # Banco de dados em memória para testes
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Desabilita CSRF protection durante testes
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    TESTING = False
    
    # Configurações mais rigorosas para produção
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(24).hex()
    
    # SSL/HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_TO_FILE = False  # Render usa logs próprios


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
