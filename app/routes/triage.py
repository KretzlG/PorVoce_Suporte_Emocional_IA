"""
Rotas de triagem
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import TriageLog, RiskLevel, TriageAction
from app import db
from datetime import datetime

triagem = Blueprint('triage', __name__)

# Mapeamento das strings para o ENUM RiskLevel
RISK_LEVEL_MAP = {
    "low": RiskLevel.LOW,
    "moderate": RiskLevel.MODERATE,
    "high": RiskLevel.HIGH,
    "critical": RiskLevel.CRITICAL
}

from app.services.ai_service import AIService

def call_ia_for_summary(image_names):
    """
    Usa o serviço de IA para analisar os nomes das imagens e retornar um resumo emocional.
    Retorna também o nível de risco, confiança e um resumo detalhado.
    """

    texto = (
        "O usuário selecionou as seguintes imagens: " + ", ".join(image_names) +
        ". Analise o que ele pode estar sentindo com base nessas escolhas."
    )

    ai_service = AIService()
    try:
        result = ai_service.analyze_sentiment(texto)
        emotion = result.get('emotion', 'indefinido')
        intensity = result.get('intensity', 'indefinida')
        score = result.get('score', 0)
        confidence = result.get('confidence', 0.5)

        # Definir risk_level simples baseado no score
        if score <= -0.7:
            risk_level = "high"
        elif score <= -0.3:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Resumo detalhado
        resumo = (
            f"Imagens selecionadas: {', '.join(image_names)}.\n"
            f"Análise da IA: O usuário pode estar sentindo {emotion} com intensidade {intensity}.\n"
            f"Nível de risco identificado: {risk_level} (score: {score}, confiança: {confidence})."
        )

        return {
            "summary": resumo,
            "risk_level": risk_level,
            "confidence": confidence,
            "result": result
        }
    except Exception as e:
        return {
            "summary": f"Não foi possível analisar os sentimentos. Erro: {str(e)}",
            "risk_level": "low",
            "confidence": 0.5,
            "result": {}
        }

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
        
        image_names = [img.get('name') for img in selected_images if 'name' in img]
        
        ia_result = call_ia_for_summary(image_names)

        # O Resumo que a IA gerou, nao sei bem aonde guardar e enviar isso, mas espero decidir isso em uma reunião.
        # print(f'{ia_result["summary"]}')

        # Mapeia o risk_level para o ENUM
        risk_level_enum = RISK_LEVEL_MAP.get(ia_result["risk_level"], RiskLevel.LOW)

        triage_log = TriageLog(
            user_id=current_user.id,
            risk_level=risk_level_enum,
            confidence_score=ia_result["confidence"],
            context_type="profile",  # ou outro contexto adequado
            created_at=datetime.utcnow()
        )
        db.session.add(triage_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'risk_level': triage_log.risk_level.value,
            'confidence': triage_log.confidence_score,
            'triage_id': triage_log.id,
            'summary': ia_result["summary"],
            'redirect_url': url_for('main.dashboard')
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro na API de triagem: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500