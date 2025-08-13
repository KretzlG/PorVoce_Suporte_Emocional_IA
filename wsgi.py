"""
WSGI entry point for ForYou application
Ponto de entrada principal para produção
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from app import create_app, db
from app.models import (
    User, ChatSession, DiaryEntry, AdminLog, TriageLog, 
    Volunteer, ChatMessage, VolunteerSkill, VolunteerAvailability,
    UserRole, VolunteerStatus, SkillLevel, AdminAction
)
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

# Criar aplicação - Esta é a variável que o gunicorn e outros servidores WSGI procuram
app = create_app()

# Comando para inserir dados de teste
@app.cli.command()
@with_appcontext  
def init_db():
    """Inicializa o banco de dados com dados de teste."""
    try:
        # Verificar se dados já existem
        if User.query.filter_by(email='admin@foryou.com').first():
            click.echo('⚠️  Dados de teste já existem!')
            click.echo('Para recriar, delete os dados existentes primeiro.')
            return

        click.echo('🚀 Criando dados de teste...')

        # Criar usuário Admin
        admin_user = User(
            email='admin@foryou.com',
            username='admin',
            password_hash=generate_password_hash('admin123'),
            first_name='Administrador',
            last_name='Sistema',
            role=UserRole.ADMIN,
            terms_accepted=True,
            privacy_policy_accepted=True,
            data_processing_consent=True
        )
        db.session.add(admin_user)
        db.session.commit()

        click.echo('✅ Dados de teste criados com sucesso!')
        click.echo('')
        click.echo('👤 Usuários criados:')
        click.echo(f'   Admin: admin@foryou.com / admin123')
        click.echo('')
        click.echo('🎯 Sistema pronto para uso!')

    except Exception as e:
        db.session.rollback()
        click.echo(f'❌ Erro ao criar dados de teste: {str(e)}')
        raise

@app.shell_context_processor
def make_shell_context():
    """Context para Flask shell"""
    return {
        'db': db,
        'User': User,
        'ChatSession': ChatSession,
        'ChatMessage': ChatMessage,
        'DiaryEntry': DiaryEntry,
        'AdminLog': AdminLog,
        'TriageLog': TriageLog,
        'Volunteer': Volunteer,
        'VolunteerSkill': VolunteerSkill,
        'VolunteerAvailability': VolunteerAvailability
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Para desenvolvimento local
    if debug:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
    else:
        # Para produção, deixar o Gunicorn gerenciar
        print(f"🚀 ForYou pronto para produção na porta {port}")
