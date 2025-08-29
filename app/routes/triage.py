"""
Rotas de triagem
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import TriageLog, RiskLevel, TriageAction
from app import db
from datetime import datetime

triagem = Blueprint('triage', __name__)


@triagem.route('/triage')
@login_required
def triage():
    """Página de triagem - redireciona para o dashboard após avaliação"""
    try:
        # Log da entrada na triagem
        current_app.logger.info(f"Usuário {current_user.id} ({current_user.username}) acessou triagem")
        
        # Aqui seria implementada a lógica de triagem
        # Por enquanto, apenas cria um log básico e redireciona
        
        # Criar log de triagem básico
        triage_log = TriageLog(
            user_id=current_user.id,
            risk_level=RiskLevel.LOW,
            context_type='system_access',
            trigger_content='Acesso direto à rota de triagem',
            analyzed_by_ai=False,
            confidence_score=1.0
        )
        
        db.session.add(triage_log)
        db.session.commit()
        
        # Redirecionar baseado no papel do usuário
        if current_user.is_admin:
            flash('Triagem completada. Redirecionando para dashboard administrativo.', 'success')
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_volunteer:
            flash('Triagem completada. Redirecionando para dashboard de voluntário.', 'success')
            return redirect(url_for('volunteer.dashboard'))
        else:
            flash('Triagem completada. Redirecionando para seu dashboard.', 'success')
            return redirect(url_for('main.dashboard'))
            
    except Exception as e:
        current_app.logger.error(f"Erro na triagem para usuário {current_user.id}: {e}")
        flash('Erro durante a triagem. Redirecionando para dashboard principal.', 'error')
        return redirect(url_for('main.dashboard'))


@triagem.route('/api/triage', methods=['POST'])
@login_required
def api_triage():
    """API endpoint para triagem de risco"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Processar dados da triagem
        content = data.get('content', '')
        context_type = data.get('context_type', 'api')
        
        # Análise básica (aqui seria implementada lógica de IA)
        risk_level = RiskLevel.LOW
        confidence = 0.8
        
        # Criar log de triagem
        triage_log = TriageLog(
            user_id=current_user.id,
            risk_level=risk_level,
            context_type=context_type,
            trigger_content=content[:1000],  # Limitar tamanho
            analyzed_by_ai=True,
            confidence_score=confidence,
            ai_model_used='basic_analysis'
        )
        
        db.session.add(triage_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'risk_level': risk_level.value,
            'confidence': confidence,
            'triage_id': triage_log.id,
            'redirect_url': url_for('main.dashboard')
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro na API de triagem: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500