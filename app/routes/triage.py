"""
Rotas para fluxo de triagem psicológica integrado ao chat
"""
from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required, current_user
from app import db
from app.models.triage import TriageLog, RiskLevel
from datetime import datetime

triage = Blueprint('triage', __name__)

@triage.route('/triage/popup', methods=['POST'])
@login_required
def triage_popup():
    """
    Exibe PopUp de triagem no chat como mensagem (nível médio/grave)
    """
    data = request.get_json()
    risk_level = data.get('risk_level')
    if risk_level not in ['moderate', 'high', 'critical']:
        return jsonify({'show_popup': False})
    # Renderiza mensagem de triagem como HTML para o chat
    html = render_template('triage/triage_popup.html', risk_level=risk_level)
    return jsonify({'show_popup': True, 'html': html})

@triage.route('/triage/images', methods=['GET', 'POST'])
@login_required
def triage_images():
    """
    Exibe tela de seleção de imagens e registra escolhas
    """
    if request.method == 'GET':
        # Renderiza tela de imagens para triagem
        return render_template('triage/triage_images.html')
    data = request.get_json()
    images_selected = data.get('images_selected', [])
    # Salva seleção no banco (exemplo simplificado)
    triage_id = session.get('triage_id')
    triage_log = TriageLog.query.get(triage_id)
    if triage_log:
        triage_log.action_details = f"Imagens selecionadas: {images_selected}"
        db.session.commit()
    return jsonify({'success': True})

@triage.route('/triage/compile', methods=['POST'])
@login_required
def triage_compile():
    """
    Compila dados da triagem e encaminha para profissional
    """
    data = request.get_json()
    triage_id = session.get('triage_id')
    triage_log = TriageLog.query.get(triage_id)
    if not triage_log:
        return jsonify({'success': False, 'error': 'Triagem não encontrada'}), 404
    user_data = data.get('user')
    chat_messages = data.get('chat_messages', [])
    images_selected = data.get('images_selected', [])
    resumo_contexto = data.get('resumo_contexto', '')
    triage_json = triage_log.compile_triage_json(user_data, chat_messages, images_selected, resumo_contexto)
    # Atualiza status para waiting e notifica profissional
    triage_log.triage_status = 'waiting'
    db.session.commit()
    # Aqui você pode integrar com o chat1a1 ou sistema de notificação
    return jsonify({'success': True, 'triage_json': triage_json})

@triage.route('/triage/forward', methods=['POST'])
@login_required
def triage_forward():
    """
    Botão: Posso te encaminhar para um profissional? Sim/Não
    """
    data = request.get_json()
    answer = data.get('answer')
    triage_id = session.get('triage_id')
    triage_log = TriageLog.query.get(triage_id)
    if not triage_log:
        return jsonify({'success': False, 'error': 'Triagem não encontrada'}), 404
    if answer == 'sim':
        triage_log.triage_status = 'waiting'
        db.session.commit()
        # INTEGRAÇÃO: Criar sessão no chat1a1 e retornar URL para frontend
        from app.models import Chat1a1Session
        chat1a1_session = Chat1a1Session(
            user_id=triage_log.user_id,
            volunteer_id=None,  # Será atribuído pelo sistema de distribuição
            status='waiting',
            started_at=datetime.utcnow()
        )
        db.session.add(chat1a1_session)
        db.session.commit()
        chat1a1_url = f"/volunteer/chat1a1/{chat1a1_session.id}"
        return jsonify({'success': True, 'forwarded': True, 'chat1a1_url': chat1a1_url})
    return jsonify({'success': True, 'forwarded': False})

# Telas (templates) para triagem
# triage_popup.html: mensagem pop-up no chat
# triage_images.html: seleção de imagens
# triage_forward.html: botão encaminhar para profissional
