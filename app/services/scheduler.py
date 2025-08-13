"""
Serviço de agendamento de tarefas para a aplicação ForYou
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import current_app
import atexit
import logging

# Configurar logger para o scheduler
logging.getLogger('apscheduler').setLevel(logging.WARNING)

scheduler = BackgroundScheduler()

def close_inactive_chat_sessions():
    """Job para fechar sessões de chat inativas"""
    try:
        with current_app.app_context():
            from app.routes.chat import close_inactive_sessions
            closed_count = close_inactive_sessions(minutes=3)
            if closed_count > 0:
                current_app.logger.info(f"📝 {closed_count} sessões inativas foram fechadas automaticamente")
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao fechar sessões inativas: {str(e)}")

def init_scheduler(app):
    """Inicializa o agendador de tarefas"""
    try:
        # Job para fechar sessões inativas a cada 2 minutos
        scheduler.add_job(
            func=close_inactive_chat_sessions,
            trigger=IntervalTrigger(minutes=2),
            id='close_inactive_sessions',
            name='Fechar sessões inativas',
            replace_existing=True
        )
        
        if not scheduler.running:
            scheduler.start()
            app.logger.info("✅ Agendador de tarefas iniciado com sucesso")
            
            # Garantir que o scheduler seja fechado quando a aplicação for encerrada
            atexit.register(lambda: scheduler.shutdown(wait=False))
        
        return True
    except Exception as e:
        app.logger.error(f"❌ Erro ao inicializar agendador: {str(e)}")
        return False

def shutdown_scheduler():
    """Desliga o agendador de tarefas"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        current_app.logger.info("🔄 Agendador de tarefas finalizado")
