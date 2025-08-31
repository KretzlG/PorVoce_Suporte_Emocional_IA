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
    return render_template('triage/triage.html')


@triagem.route('/api/triage', methods=['POST'])
@login_required
def api_triage():
    """API endpoint para triagem de risco"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        selected_images = data.get('selectedImages', [])
        if not selected_images:
            return jsonify({'error': 'Nenhuma imagem selecionada'}), 400
        
        #print de teste da data -> ESSE FOR LOOP PRINTA TODOS OS NOMES, VAI SER IMPORTANTE PRA FAZER O JSON DO NGC.
        for img in selected_images:
            print(f"Nome da imagem: {img.get('name')}")

        return jsonify({
            'success': True,
            'risk_level': 'low',
            'confidence': 0.9,
            'triage_id': 123,
            'redirect_url': url_for('main.dashboard')
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro na API de triagem: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500