"""
Rotas para fluxo de triagem psicológica integrado ao chat
"""
from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required, current_user
from app import db
from app.models.triage import TriageLog, RiskLevel, TriageAction
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
    Compila dados da triagem coletados na interface
    """
    try:
        data = request.get_json()
        triage_id = data.get('triage_id')
        
        if not triage_id:
            triage_id = session.get('triage_id')
        
        if not triage_id:
            return jsonify({'success': False, 'error': 'Triagem não encontrada'}), 404
        
        triage_log = TriageLog.query.get(triage_id)
        if not triage_log or triage_log.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Triagem não encontrada'}), 404
        
        # Extrair dados coletados
        selected_emotions = data.get('selected_emotions', [])
        main_concern = data.get('main_concern', '')
        previous_help = data.get('previous_help', 'nao-informado')
        urgency_level = data.get('urgency_level', 'moderate')
        
        # Preparar dados compilados
        compiled_data = {
            'selected_emotions': selected_emotions,
            'main_concern': main_concern,
            'previous_help': previous_help,
            'urgency_level': urgency_level,
            'collection_timestamp': data.get('timestamp', datetime.utcnow().isoformat())
        }
        
        # Atualizar log de triagem
        triage_log.action_details = f"Dados coletados: {len(selected_emotions)} emoções selecionadas, " \
                                  f"preocupação principal: {'sim' if main_concern else 'não informada'}, " \
                                  f"ajuda anterior: {previous_help}"
        
        # Armazenar dados compilados como JSON
        import json
        triage_log.risk_factors = json.dumps(compiled_data, ensure_ascii=False)
        
        # Atualizar status
        triage_log.triage_status = 'compiled'
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'compiled_data': compiled_data,
            'message': 'Dados coletados com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao compilar dados: {str(e)}'}), 500

@triage.route('/triage/forward', methods=['POST'])
@login_required
def triage_forward():
    """
    Botão: Posso te encaminhar para um profissional? Sim/Não
    """
    try:
        data = request.get_json()
        print(f"[DEBUG TRIAGE] Dados recebidos: {data}")
        
        answer = data.get('answer')
        triage_id = data.get('triage_id')
        urgency_level = data.get('urgency_level', 'moderate')

        # Corrigir id 'undefined' ou string inválida
        if not triage_id or triage_id == 'undefined' or not str(triage_id).isdigit():
            triage_id = session.get('triage_id')

        if not triage_id or not str(triage_id).isdigit():
            print("[DEBUG TRIAGE] Triagem ID não encontrado ou inválido")
            return jsonify({'success': False, 'error': 'Triagem não encontrada'}), 404

        triage_log = TriageLog.query.get(int(triage_id))
        if not triage_log or triage_log.user_id != current_user.id:
            print(f"[DEBUG TRIAGE] Log não encontrado ou usuário incorreto. Log: {triage_log}, User: {current_user.id}")
            return jsonify({'success': False, 'error': 'Triagem não encontrada'}), 404
        
        print(f"[DEBUG TRIAGE] Resposta: {answer}, Urgência: {urgency_level}")
        
        if answer == 'sim':
            # Atualizar status da triagem
            triage_log.triage_status = 'waiting'
            triage_log.action_taken = TriageAction.PROFESSIONAL_REFERRAL
            triage_log.action_details = f"Usuário aceitou encaminhamento profissional (urgência: {urgency_level})"
            db.session.commit()
            
            print(f"[DEBUG TRIAGE] Encaminhamento aceito para urgência: {urgency_level}")
            
            # Determinar a URL de redirecionamento baseada na urgência
            if urgency_level == 'emergency' or urgency_level == 'critical':
                # Para emergências, redirecionar para página de contatos de emergência
                redirect_url = "/emergency-contacts"
                message = "Encaminhamento de emergência ativado - você será redirecionado para contatos de emergência"
                print(f"[DEBUG TRIAGE] Redirecionamento de emergência: {redirect_url}")
            elif urgency_level == 'high':
                # Para risco alto, redirecionar para formulário de agendamento prioritário
                redirect_url = "/triage/priority-form"
                message = "Encaminhamento prioritário - você será redirecionado para agendamento"
                print(f"[DEBUG TRIAGE] Redirecionamento prioritário: {redirect_url}")
            else:
                # Para risco moderado, redirecionar para formulário de encaminhamento normal
                redirect_url = "/triage/referral-form"
                message = "Encaminhamento registrado - você será redirecionado para formulário"
                print(f"[DEBUG TRIAGE] Redirecionamento normal: {redirect_url}")
            
            return jsonify({
                'success': True, 
                'forwarded': True, 
                'redirect_url': redirect_url,
                'urgency_level': urgency_level,
                'message': message
            })
        else:
            # Usuário não quer encaminhamento
            triage_log.action_taken = TriageAction.MONITORED
            triage_log.action_details = "Usuário optou por continuar sem encaminhamento"
            db.session.commit()
            
            print("[DEBUG TRIAGE] Usuário recusou encaminhamento")
            return jsonify({
                'success': True, 
                'forwarded': False,
                'message': 'Continuando chat sem encaminhamento'
            })
            
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR TRIAGE] Erro no encaminhamento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erro no encaminhamento: {str(e)}'}), 500


@triage.route('/emergency-contacts')
@login_required
def emergency_contacts():
    """Página de contatos de emergência para casos críticos"""
    return render_template('triage/emergency_contacts.html')


@triage.route('/triage/priority-form')
@login_required
def priority_form():
    """Formulário de agendamento prioritário para risco alto"""
    return render_template('triage/priority_form.html')


@triage.route('/triage/referral-form')
@login_required
def referral_form():
    """Formulário de encaminhamento para risco moderado"""
    return render_template('triage/referral_form.html')


@triage.route('/api/triage/waiting')
@login_required
def api_waiting_clients():
    """API para verificar clientes aguardando atendimento de triagem"""
    try:
        # Importar models necessários
        from app.models.chat1a1 import Chat1a1Session
        from app.models.volunteer import Volunteer
        
        # Verificar se o usuário atual é voluntário
        volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
        if not volunteer:
            return jsonify({'waiting_count': 0, 'message': 'Usuário não é voluntário'})
        
        # Contar sessões 1a1 aguardando voluntário com prioridade alta/crítica
        waiting_sessions = Chat1a1Session.query.filter(
            Chat1a1Session.status == 'WAITING',
            Chat1a1Session.volunteer_id.is_(None),
            Chat1a1Session.priority_level.in_(['high', 'critical'])
        ).count()
        
        # Contar triagens aguardando encaminhamento
        waiting_triage = TriageLog.query.filter(
            TriageLog.triage_status == 'waiting',
            TriageLog.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).count()
        
        total_waiting = waiting_sessions + waiting_triage
        
        return jsonify({
            'success': True,
            'waiting_count': total_waiting,
            'sessions_waiting': waiting_sessions,
            'triage_waiting': waiting_triage,
            'message': f'{total_waiting} clientes aguardando atendimento prioritário'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'waiting_count': 0,
            'error': f'Erro ao buscar clientes aguardando: {str(e)}'
        }), 500


# Telas (templates) para triagem
# triage_popup.html: mensagem pop-up no chat
# triage_images.html: seleção de imagens
# triage_forward.html: botão encaminhar para profissional
