"""
Rotas do Diário Emocional
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import DiaryEntry, User
from app.services.ai_service import AIService
from app import db
from datetime import datetime, timedelta
import json
import math

diary = Blueprint('diary', __name__)

@diary.route('/diary')
@login_required
def diary_interface():
    """Interface principal do diário emocional"""
    if current_user.role.value == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    return render_template('diary/diary.html', user=current_user)

@diary.route('/api/diary/add', methods=['POST'])
@login_required
def add_entry():
    """Endpoint para adicionar nova entrada no diário"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Conteúdo da entrada é obrigatório'
            }), 400
        
        content = data['content'].strip()
        mood = data.get('mood', 'neutro')
        title = data.get('title', '').strip()
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Conteúdo não pode estar vazio'
            }), 400
        
        # Converter mood string para valor numérico
        mood_map = {
            'muito-triste': 1,
            'triste': 2,
            'neutro': 3,
            'feliz': 4,
            'muito-feliz': 5
        }
        
        mood_level = mood_map.get(mood, 3)  # Default: neutro
        
        # Criar nova entrada
        entry = DiaryEntry(
            user_id=current_user.id,
            title=title if title else None,
            content=content,
            mood_level=mood_level
        )
        
        # Analisar conteúdo
        entry.analyze_content()
        
        # Salvar no banco
        entry.save()
        
        # Análise com IA se disponível
        try:
            from app import ai_service
            if ai_service and hasattr(ai_service, 'analyze_diary_entry'):
                analysis = ai_service.analyze_diary_entry(content)
                if analysis:
                    entry.sentiment_score = analysis.get('sentiment_score', entry.sentiment_score)
                    entry.emotions = json.dumps(analysis.get('themes', []))
                    entry.risk_factors = json.dumps(analysis.get('risk_indicators', []))
                    entry.save()
        except Exception as ai_error:
            print(f"Erro na análise IA: {ai_error}")
            # Continuar mesmo se a IA falhar
        
        return jsonify({
            'success': True,
            'message': 'Entrada salva com sucesso',
            'entry': {
                'id': entry.id,
                'title': entry.title,
                'content': entry.content,
                'mood': mood,
                'mood_level': entry.mood_level,
                'created_at': entry.created_at.isoformat(),
                'word_count': entry.word_count
            }
        })
        
    except Exception as e:
        print(f"Erro ao adicionar entrada: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@diary.route('/api/diary/get')
@login_required
def get_entries():
    """Endpoint para recuperar entradas do diário"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        
        # Filtros
        period = request.args.get('period', '30')  # dias
        mood_filter = request.args.get('mood', 'all')
        
        query = DiaryEntry.query.filter_by(user_id=current_user.id)
        
        # Aplicar filtro de período
        if period != 'all':
            try:
                days = int(period)
                start_date = datetime.now() - timedelta(days=days)
                query = query.filter(DiaryEntry.created_at >= start_date)
            except ValueError:
                pass  # Ignorar erro de conversão
        
        # Aplicar filtro de humor
        if mood_filter != 'all':
            mood_map = {
                'muito-triste': 1,
                'triste': 2,
                'neutro': 3,
                'feliz': 4,
                'muito-feliz': 5
            }
            mood_level = mood_map.get(mood_filter)
            if mood_level:
                query = query.filter(DiaryEntry.mood_level == mood_level)
        
        # Ordenar por data mais recente e paginar
        pagination = query.order_by(DiaryEntry.created_at.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
        
        # Converter humor numérico para string
        def mood_to_string(mood_level):
            mood_map = {
                1: 'muito-triste',
                2: 'triste',
                3: 'neutro',
                4: 'feliz',
                5: 'muito-feliz'
            }
            return mood_map.get(mood_level, 'neutro')
        
        entries_data = []
        for entry in pagination.items:
            entries_data.append({
                'id': entry.id,
                'title': entry.title,
                'content': entry.content,
                'mood': mood_to_string(entry.mood_level),
                'mood_level': entry.mood_level,
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat() if entry.updated_at else entry.created_at.isoformat(),
                'word_count': entry.word_count,
                'sentiment_score': entry.sentiment_score
            })
        
        return jsonify({
            'success': True,
            'entries': entries_data,
            'pagination': {
                'current_page': pagination.page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'current_page': pagination.page,
            'total_pages': pagination.pages,
            'total_entries': pagination.total
        })
        
    except Exception as e:
        print(f"Erro ao recuperar entradas: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'entries': [],
            'current_page': 1,
            'total_pages': 1
        }), 500

@diary.route('/api/diary/insights')
@login_required
def get_insights():
    """Endpoint para recuperar insights do diário"""
    try:
        # Filtro de período
        period = request.args.get('period', '30')
        
        query = DiaryEntry.query.filter_by(user_id=current_user.id)
        
        # Aplicar filtro de período
        if period != 'all':
            try:
                days = int(period)
                start_date = datetime.now() - timedelta(days=days)
                query = query.filter(DiaryEntry.created_at >= start_date)
            except ValueError:
                pass  # Usar todas as entradas se erro na conversão
        
        entries = query.all()
        
        if not entries:
            return jsonify({
                'success': True,
                'insights': {
                    'total_entries': 0,
                    'total_words': 0,
                    'dominant_mood': 'N/A',
                    'mood_distribution': {},
                    'average_sentiment': 0,
                    'streak': 0
                }
            })
        
        # Calcular insights
        total_entries = len(entries)
        total_words = sum(entry.word_count or 0 for entry in entries)
        
        # Distribuição de humor
        mood_counts = {}
        mood_names = {1: 'Muito Triste', 2: 'Triste', 3: 'Neutro', 4: 'Feliz', 5: 'Muito Feliz'}
        
        for entry in entries:
            mood_name = mood_names.get(entry.mood_level, 'Neutro')
            mood_counts[mood_name] = mood_counts.get(mood_name, 0) + 1
        
        # Humor predominante
        dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else 'N/A'
        
        # Sentimento médio
        sentiments = [entry.sentiment_score for entry in entries if entry.sentiment_score is not None]
        average_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Sequência de dias (simplificado)
        recent_dates = [entry.created_at.date() for entry in entries[-7:]]  # Últimos 7 dias
        unique_dates = len(set(recent_dates))
        streak = unique_dates if unique_dates > 1 else 0
        
        return jsonify({
            'success': True,
            'insights': {
                'total_entries': total_entries,
                'total_words': total_words,
                'dominant_mood': dominant_mood,
                'mood_distribution': mood_counts,
                'average_sentiment': round(average_sentiment, 2),
                'streak': streak
            }
        })
        
    except Exception as e:
        print(f"Erro ao gerar insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'insights': {}
        }), 500

@diary.route('/api/diary/delete/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    """Endpoint para deletar uma entrada do diário"""
    try:
        entry = DiaryEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
        
        if not entry:
            return jsonify({
                'success': False,
                'error': 'Entrada não encontrada'
            }), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Entrada deletada com sucesso'
        })
        
    except Exception as e:
        print(f"Erro ao deletar entrada: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@diary.route('/api/diary/<int:entry_id>')
@login_required
def get_entry(entry_id):
    """Endpoint para recuperar uma entrada específica"""
    try:
        entry = DiaryEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
        
        if not entry:
            return jsonify({
                'success': False,
                'error': 'Entrada não encontrada'
            }), 404
        
        # Converter humor numérico para string
        mood_map = {1: 'muito-triste', 2: 'triste', 3: 'neutro', 4: 'feliz', 5: 'muito-feliz'}
        
        return jsonify({
            'success': True,
            'entry': {
                'id': entry.id,
                'title': entry.title,
                'content': entry.content,
                'mood': mood_map.get(entry.mood_level, 'neutro'),
                'mood_level': entry.mood_level,
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat() if entry.updated_at else entry.created_at.isoformat(),
                'word_count': entry.word_count,
                'sentiment_score': entry.sentiment_score
            }
        })
        
    except Exception as e:
        print(f"Erro ao recuperar entrada: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500
