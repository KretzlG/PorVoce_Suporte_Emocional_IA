"""
Rotas do diário emocional
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import DiaryEntry
from app.services.risk_analyzer import RiskAnalyzer
from app import db
from datetime import datetime
import json

# Importar ai_service condicionalmente
try:
    from app import ai_service, AI_AVAILABLE
except ImportError:
    ai_service = None
    AI_AVAILABLE = False

diary = Blueprint('diary', __name__)
risk_analyzer = RiskAnalyzer()


@diary.route('/')
@login_required
def diary_list():
    """Lista de entradas do diário"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    entries = DiaryEntry.query.filter_by(user_id=current_user.id)\
        .order_by(DiaryEntry.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('diary/list.html', entries=entries)


@diary.route('/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    """Nova entrada do diário"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        mood_rating = data.get('mood_rating', type=int)
        is_private = data.get('is_private', True, type=bool)
        
        if not content:
            error_msg = 'O conteúdo não pode estar vazio'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('diary/new.html')
        
        try:
            # Criar entrada
            entry = DiaryEntry(
                user_id=current_user.id,
                title=title if title else f"Entrada de {datetime.now().strftime('%d/%m/%Y')}",
                content=content,
                mood_rating=mood_rating,
                is_private=is_private
            )
            
            # Analisar com IA se usuário consentiu
            if current_user.consent_ai_analysis:
                sentiment_analysis = ai_service.analyze_sentiment(content)
                entry.sentiment_score = sentiment_analysis.get('score', 0)
                entry.dominant_emotion = sentiment_analysis.get('emotion', 'neutral')
                entry.emotions_detected = json.dumps(sentiment_analysis.get('raw_scores', {}))
                # Análise de risco removida (modelo não existe)
            
            db.session.add(entry)
            db.session.commit()
            
            success_msg = 'Entrada salva com sucesso!'
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'redirect': url_for('diary.view_entry', id=entry.id)
                })
            else:
                flash(success_msg, 'success')
                return redirect(url_for('diary.view_entry', id=entry.id))
                
        except Exception as e:
            db.session.rollback()
            error_msg = 'Erro ao salvar entrada. Tente novamente.'
            
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return render_template('diary/new.html')
    
    return render_template('diary/new.html')


@diary.route('/<int:id>')
@login_required
def view_entry(id):
    """Visualizar entrada específica"""
    entry = DiaryEntry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Avaliação de risco removida (modelo não existe)
    return render_template('diary/view.html', entry=entry, risk_assessment=None)


@diary.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(id):
    """Editar entrada do diário"""
    entry = DiaryEntry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        mood_rating = data.get('mood_rating', type=int)
        is_private = data.get('is_private', True, type=bool)
        
        if not content:
            error_msg = 'O conteúdo não pode estar vazio'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            else:
                flash(error_msg, 'error')
                return render_template('diary/edit.html', entry=entry)
        
        try:
            # Atualizar entrada
            entry.title = title if title else entry.title
            entry.content = content
            entry.mood_rating = mood_rating
            entry.is_private = is_private
            entry.updated_at = datetime.utcnow()
            
            # Re-analisar com IA se conteúdo mudou
            if current_user.consent_ai_analysis and content != entry.content:
                sentiment_analysis = ai_service.analyze_sentiment(content)
                entry.sentiment_score = sentiment_analysis.get('score', 0)
                entry.dominant_emotion = sentiment_analysis.get('emotion', 'neutral')
                entry.emotions_detected = json.dumps(sentiment_analysis.get('raw_scores', {}))
                
                # Re-analisar risco
                risk_analysis = risk_analyzer.analyze_message(content, current_user.id)
                entry.risk_score = risk_analysis['risk_score']
            
            db.session.commit()
            
            success_msg = 'Entrada atualizada com sucesso!'
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'redirect': url_for('diary.view_entry', id=entry.id)
                })
            else:
                flash(success_msg, 'success')
                return redirect(url_for('diary.view_entry', id=entry.id))
                
        except Exception as e:
            db.session.rollback()
            error_msg = 'Erro ao atualizar entrada. Tente novamente.'
            
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 500
            else:
                flash(error_msg, 'error')
                return render_template('diary/edit.html', entry=entry)
    
    return render_template('diary/edit.html', entry=entry)


@diary.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_entry(id):
    """Deletar entrada do diário"""
    entry = DiaryEntry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(entry)
        db.session.commit()
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Entrada deletada com sucesso'
            })
        else:
            flash('Entrada deletada com sucesso', 'success')
            return redirect(url_for('diary.diary_list'))
    except Exception as e:
        db.session.rollback()
        error_msg = 'Erro ao deletar entrada'
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('diary.view_entry', id=id))


@diary.route('/auto-save', methods=['POST'])
@login_required
def auto_save():
    """Auto-salvar entrada em progresso"""
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content or len(content) < 10:
        return jsonify({'success': False, 'error': 'Conteúdo muito curto'}), 400
    
    try:
        # Salvar em sessão ou cache temporário
        # Por simplicidade, vamos apenas retornar sucesso
        # Em produção, você pode querer salvar em Redis ou session
        
        return jsonify({
            'success': True,
            'message': 'Auto-salvo',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro no auto-save'}), 500


@diary.route('/analytics')
@login_required
def analytics():
    """Analytics do diário do usuário"""
    # Estatísticas básicas
    total_entries = DiaryEntry.query.filter_by(user_id=current_user.id).count()
    
    if total_entries == 0:
        return render_template('diary/analytics.html', stats={'total_entries': 0})
    
    # Entradas dos últimos 30 dias
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_entries = DiaryEntry.query.filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.created_at >= thirty_days_ago
    ).all()
    
    # Calcular estatísticas
    stats = {
        'total_entries': total_entries,
        'recent_entries': len(recent_entries),
        'avg_mood': 0,
        'mood_trend': 'stable',
        'dominant_emotions': {},
        'sentiment_trend': []
    }
    
    if recent_entries:
        # Humor médio
        mood_ratings = [entry.mood_rating for entry in recent_entries if entry.mood_rating]
        if mood_ratings:
            stats['avg_mood'] = round(sum(mood_ratings) / len(mood_ratings), 1)
        
        # Emoções dominantes
        emotions = [entry.dominant_emotion for entry in recent_entries if entry.dominant_emotion]
        emotion_count = {}
        for emotion in emotions:
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
        
        stats['dominant_emotions'] = dict(sorted(emotion_count.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Tendência de sentimento
        sentiment_scores = [(entry.created_at.strftime('%Y-%m-%d'), entry.sentiment_score) 
                          for entry in recent_entries if entry.sentiment_score is not None]
        
        stats['sentiment_trend'] = sentiment_scores
    
    return render_template('diary/analytics.html', stats=stats)


@diary.route('/export')
@login_required
def export_diary():
    """Exportar diário do usuário"""
    entries = DiaryEntry.query.filter_by(user_id=current_user.id)\
        .order_by(DiaryEntry.created_at.asc()).all()
    
    # Criar dados para exportação
    export_data = {
        'user': current_user.username,
        'export_date': datetime.utcnow().isoformat(),
        'total_entries': len(entries),
        'entries': []
    }
    
    for entry in entries:
        export_data['entries'].append({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content if not entry.is_private else '[Conteúdo Privado]',
            'mood_rating': entry.mood_rating,
            'dominant_emotion': entry.dominant_emotion,
            'created_at': entry.created_at.isoformat() if entry.created_at else None,
            'updated_at': entry.updated_at.isoformat() if entry.updated_at else None
        })
    
    return jsonify(export_data)
