"""
API para Gerenciamento e Monitoramento do Sistema de Treinamento de IA
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Importar serviços
from app.services.ai_service import AIService
from app.services.advanced_rag_service import advanced_rag_service
from app.services.advanced_prompt_engineer import advanced_prompt_engineer
from app.services.finetuning_preparator import finetuning_preparator
from app.services.training_usage_logger import training_usage_logger

logger = logging.getLogger(__name__)

# Criar blueprint para API de treinamento
training_api_bp = Blueprint('training_api', __name__, url_prefix='/api/training')


@training_api_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica saúde de todos os sistemas de treinamento"""
    try:
        ai_service = AIService()
        
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'systems': {
                'ai_service': {
                    'status': 'active',
                    'version': '3.0',
                    'capabilities': ai_service.get_system_capabilities()
                },
                'advanced_rag': {
                    'status': 'active' if advanced_rag_service else 'inactive',
                    'cache_size': len(getattr(advanced_rag_service, 'cache', {})) if advanced_rag_service else 0
                },
                'prompt_engineer': {
                    'status': 'active' if advanced_prompt_engineer else 'inactive',
                    'templates_count': len(getattr(advanced_prompt_engineer, 'prompt_templates', {})) if advanced_prompt_engineer else 0
                },
                'finetuning_preparator': {
                    'status': 'active' if finetuning_preparator else 'inactive',
                    'supported_formats': ['openai_chat', 'jsonl', 'csv'] if finetuning_preparator else []
                },
                'training_logger': {
                    'status': 'active' if training_usage_logger else 'inactive'
                }
            }
        }
        
        # Verificar se algum sistema está com problema
        inactive_systems = [name for name, info in health_status['systems'].items() if info['status'] == 'inactive']
        if inactive_systems:
            health_status['overall_status'] = 'degraded'
            health_status['warnings'] = f"Sistemas inativos: {', '.join(inactive_systems)}"
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'error',
            'error': str(e)
        }), 500


@training_api_bp.route('/statistics', methods=['GET'])
@login_required
def get_training_statistics():
    """Retorna estatísticas completas do sistema de treinamento"""
    try:
        ai_service = AIService()
        
        # Obter estatísticas de todos os sistemas
        stats = {
            'general': ai_service.get_service_statistics(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Estatísticas específicas do RAG
        if advanced_rag_service:
            try:
                stats['rag'] = advanced_rag_service.get_training_data_statistics()
            except Exception as e:
                stats['rag_error'] = str(e)
        
        # Estatísticas do prompt engineering
        if advanced_prompt_engineer:
            try:
                stats['prompt_engineering'] = advanced_prompt_engineer.get_prompt_statistics()
            except Exception as e:
                stats['prompt_engineering_error'] = str(e)
        
        # Recomendações de fine-tuning
        if finetuning_preparator:
            try:
                stats['finetuning_recommendations'] = finetuning_preparator.get_dataset_recommendations()
            except Exception as e:
                stats['finetuning_error'] = str(e)
        
        # Estatísticas de uso de treinamento
        if training_usage_logger:
            try:
                stats['training_usage'] = training_usage_logger.get_usage_statistics()
            except Exception as e:
                stats['training_usage_error'] = str(e)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/search', methods=['POST'])
@login_required
def search_training_content():
    """Busca conteúdo nos dados de treinamento"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Query é obrigatória'}), 400
        
        ai_service = AIService()
        result = ai_service.search_training_content(query, limit)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/context', methods=['POST'])
@login_required
def get_advanced_context():
    """Obtém contexto avançado usando RAG"""
    try:
        data = request.get_json()
        user_message = data.get('user_message', '')
        risk_level = data.get('risk_level', 'low')
        context_type = data.get('context_type', 'all')
        
        if not user_message:
            return jsonify({'error': 'user_message é obrigatória'}), 400
        
        ai_service = AIService()
        result = ai_service.get_advanced_context(user_message, risk_level, context_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro no contexto avançado: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/prompt/analyze', methods=['POST'])
@login_required
def analyze_prompt_context():
    """Analisa contexto para prompt engineering"""
    try:
        data = request.get_json()
        user_message = data.get('user_message', '')
        risk_level = data.get('risk_level', 'low')
        user_context = data.get('user_context', {})
        
        if not user_message:
            return jsonify({'error': 'user_message é obrigatória'}), 400
        
        ai_service = AIService()
        result = ai_service.analyze_prompt_context(user_message, risk_level, user_context)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na análise do prompt: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/finetuning/dataset/create', methods=['POST'])
@login_required
def create_finetuning_dataset():
    """Cria dataset para fine-tuning"""
    try:
        data = request.get_json()
        dataset_type = data.get('dataset_type', 'hybrid')
        format_type = data.get('format_type', 'openai_chat')
        max_samples = data.get('max_samples', 1000)
        
        # Validar parâmetros
        valid_types = ['conversations', 'training_data', 'hybrid']
        valid_formats = ['openai_chat', 'openai_completion', 'jsonl', 'csv']
        
        if dataset_type not in valid_types:
            return jsonify({'error': f'dataset_type deve ser um de: {valid_types}'}), 400
        
        if format_type not in valid_formats:
            return jsonify({'error': f'format_type deve ser um de: {valid_formats}'}), 400
        
        if not isinstance(max_samples, int) or max_samples < 1 or max_samples > 10000:
            return jsonify({'error': 'max_samples deve ser um inteiro entre 1 e 10000'}), 400
        
        ai_service = AIService()
        result = ai_service.create_finetuning_dataset(dataset_type, format_type, max_samples)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na criação do dataset: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/finetuning/dataset/save', methods=['POST'])
@login_required
def save_finetuning_dataset():
    """Salva dataset de fine-tuning em arquivo"""
    try:
        data = request.get_json()
        dataset_result = data.get('dataset_result', {})
        file_path = data.get('file_path')
        
        if not dataset_result:
            return jsonify({'error': 'dataset_result é obrigatório'}), 400
        
        ai_service = AIService()
        result = ai_service.save_finetuning_dataset(dataset_result, file_path)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao salvar dataset: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/finetuning/recommendations', methods=['GET'])
@login_required
def get_finetuning_recommendations():
    """Obtém recomendações para fine-tuning"""
    try:
        if not finetuning_preparator:
            return jsonify({'error': 'Preparador de fine-tuning não disponível'}), 503
        
        recommendations = finetuning_preparator.get_dataset_recommendations()
        return jsonify(recommendations)
        
    except Exception as e:
        logger.error(f"Erro nas recomendações: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/usage/report', methods=['GET'])
@login_required
def get_training_usage_report():
    """Obtém relatório de uso de dados de treinamento"""
    try:
        ai_service = AIService()
        report = ai_service.get_training_usage_report()
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Erro no relatório: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/usage/clear-cache', methods=['POST'])
@login_required
def clear_training_cache():
    """Limpa cache de dados de treinamento"""
    try:
        ai_service = AIService()
        result = ai_service.clear_training_cache()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/test/response', methods=['POST'])
@login_required
def test_ai_response():
    """Testa resposta da IA com sistema completo"""
    try:
        data = request.get_json()
        user_message = data.get('user_message', '')
        risk_level = data.get('risk_level', 'low')
        user_context = data.get('user_context', {})
        conversation_history = data.get('conversation_history', [])
        
        if not user_message:
            return jsonify({'error': 'user_message é obrigatória'}), 400
        
        # Validar risk_level
        valid_risks = ['low', 'moderate', 'high', 'critical']
        if risk_level not in valid_risks:
            return jsonify({'error': f'risk_level deve ser um de: {valid_risks}'}), 400
        
        ai_service = AIService()
        
        # Gerar resposta usando sistema completo
        result = ai_service.generate_response(
            user_message=user_message,
            risk_level=risk_level,
            user_context=user_context,
            conversation_history=conversation_history
        )
        
        # Adicionar informações de teste
        result['test_mode'] = True
        result['request_timestamp'] = datetime.utcnow().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro no teste de resposta: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/test/sentiment', methods=['POST'])
@login_required
def test_sentiment_analysis():
    """Testa análise de sentimento"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'text é obrigatório'}), 400
        
        ai_service = AIService()
        
        # Análise de sentimento
        sentiment_result = ai_service.analyze_sentiment(text)
        
        # Análise de risco
        risk_level = ai_service.assess_risk_level(text, sentiment_result)
        
        # Análise completa
        complete_analysis = ai_service.analyze_with_risk_assessment(text)
        
        result = {
            'text': text,
            'sentiment': sentiment_result,
            'risk_level': risk_level,
            'complete_analysis': complete_analysis,
            'test_timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro no teste de sentimento: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/config', methods=['GET'])
@login_required
def get_system_config():
    """Retorna configuração atual do sistema"""
    try:
        ai_service = AIService()
        
        config = {
            'timestamp': datetime.utcnow().isoformat(),
            'ai_service': {
                'openai_model': ai_service.openai_model,
                'max_tokens': ai_service.max_tokens,
                'temperature': ai_service.temperature,
                'rag_enabled': ai_service.rag_enabled,
                'log_training_usage': ai_service.log_training_usage
            },
            'advanced_systems': {
                'rag_cache_size': len(getattr(advanced_rag_service, 'cache', {})) if advanced_rag_service else 0,
                'prompt_templates': len(getattr(advanced_prompt_engineer, 'prompt_templates', {})) if advanced_prompt_engineer else 0,
                'supported_formats': ['openai_chat', 'jsonl', 'csv'] if finetuning_preparator else []
            },
            'capabilities': ai_service.get_system_capabilities()
        }
        
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"Erro na configuração: {e}")
        return jsonify({'error': str(e)}), 500


@training_api_bp.route('/debug/logs', methods=['GET'])
@login_required
def get_debug_logs():
    """Retorna logs recentes para debug"""
    try:
        # Ler logs recentes do training_usage_logger
        if training_usage_logger:
            try:
                logs = training_usage_logger.get_recent_logs(limit=50)
                return jsonify({
                    'success': True,
                    'logs': logs,
                    'timestamp': datetime.utcnow().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro ao acessar logs: {str(e)}'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Sistema de logging não disponível'
            })
        
    except Exception as e:
        logger.error(f"Erro nos logs de debug: {e}")
        return jsonify({'error': str(e)}), 500


# Adicionar headers CORS se necessário
@training_api_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


# Registrar blueprint
def register_training_api(app):
    """Registra a API de treinamento na aplicação Flask"""
    app.register_blueprint(training_api_bp)
    
    logger.info("API de treinamento registrada com sucesso")