"""
Rotas para treinamento da IA
"""

import os
import uuid
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import TrainingData, TrainingDataType, TrainingDataStatus
from app.services.training_validation import TrainingValidationService
from app import db
from functools import wraps
import logging

logger = logging.getLogger(__name__)

training = Blueprint('training', __name__)

def admin_or_volunteer_required(f):
    """Decorator para rotas que requerem privilégios de admin ou voluntário"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not (current_user.is_admin or current_user.role.value == 'volunteer'):
            flash('Acesso negado. Apenas administradores e voluntários podem acessar esta área.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Configurações de upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'odt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file):
    """Obtém o tamanho do arquivo"""
    file.seek(0, 2)  # Vai para o final do arquivo
    size = file.tell()
    file.seek(0)  # Volta para o início
    return size

@training.route('/training')
@login_required
@admin_or_volunteer_required
def index():
    """Página principal de treinamento"""
    # Buscar dados de treinamento do usuário
    user_trainings = TrainingData.query.filter_by(submitted_by=current_user.id)\
        .order_by(TrainingData.created_at.desc()).limit(10).all()
    
    # Estatísticas
    stats = {
        'total_submitted': TrainingData.query.filter_by(submitted_by=current_user.id).count(),
        'approved': TrainingData.query.filter_by(
            submitted_by=current_user.id, 
            status=TrainingDataStatus.APPROVED
        ).count(),
        'pending': TrainingData.query.filter_by(
            submitted_by=current_user.id, 
            status=TrainingDataStatus.PENDING
        ).count(),
        'rejected': TrainingData.query.filter_by(
            submitted_by=current_user.id, 
            status=TrainingDataStatus.REJECTED
        ).count()
    }
    
    return render_template('training.html', 
                         trainings=user_trainings, 
                         stats=stats,
                         user=current_user)

@training.route('/training/submit', methods=['GET', 'POST'])
@login_required
@admin_or_volunteer_required
def submit():
    if request.method == 'POST':
        try:
            data_type = request.form.get('data_type')
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            content = request.form.get('content', '').strip()

            if not title:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return '<div class="alert alert-danger">Título é obrigatório</div>', 400
                return jsonify({'success': False, 'message': 'Título é obrigatório'}), 400

            training_data = TrainingData(
                title=title,
                description=description,
                submitted_by=current_user.id,
                data_type=TrainingDataType.TEXT if data_type == 'text' else TrainingDataType.FILE
            )
            validation_service = TrainingValidationService()

            if data_type == 'text':
                if not content:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return '<div class="alert alert-danger">Conteúdo de texto é obrigatório</div>', 400
                    return jsonify({'success': False, 'message': 'Conteúdo de texto é obrigatório'}), 400
                training_data.content = content
                validation_result = validation_service.validate_content(content, title, description)
            elif data_type == 'file':
                file = request.files.get('file')
                if not file or file.filename == '':
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return '<div class="alert alert-danger">Arquivo é obrigatório</div>', 400
                    return jsonify({'success': False, 'message': 'Arquivo é obrigatório'}), 400
                if not allowed_file(file.filename):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return f'<div class="alert alert-danger">Tipo de arquivo não permitido. Tipos aceitos: {", ".join(ALLOWED_EXTENSIONS)}</div>', 400
                    return jsonify({'success': False, 'message': f'Tipo de arquivo não permitido. Tipos aceitos: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
                file_size = get_file_size(file)
                if file_size > MAX_FILE_SIZE:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return f'<div class="alert alert-danger">Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE // (1024*1024)}MB</div>', 400
                    return jsonify({'success': False, 'message': f'Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'training')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                training_data.file_name = filename
                training_data.file_path = file_path
                training_data.file_size = file_size
                training_data.file_type = filename.rsplit('.', 1)[1].lower()
                validation_result = validation_service.validate_file_content(file_path, training_data.file_type)
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return '<div class="alert alert-danger">Tipo de dados inválido</div>', 400
                return jsonify({'success': False, 'message': 'Tipo de dados inválido'}), 400

            training_data.validation_score = validation_result['score']
            training_data.validation_notes = validation_service.get_validation_summary(validation_result)
            if validation_result['is_valid']:
                training_data.status = TrainingDataStatus.APPROVED
            else:
                training_data.status = TrainingDataStatus.REJECTED
            training_data.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Retorna HTML parcial para AJAX
                return render_template('training/success.html', user=current_user)
            return jsonify({
                'success': True,
                'message': 'Conteúdo submetido com sucesso!',
                'data': {
                    'id': training_data.id,
                    'status': training_data.status.value,
                    'score': training_data.validation_score,
                    'validation_summary': training_data.validation_notes
                }
            })
        except Exception as e:
            logger.error(f"Erro ao submeter treinamento: {str(e)}")
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return f'<div class="alert alert-danger">Erro interno: {str(e)}</div>', 500
            return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500
    return render_template('training/submit.html', user=current_user)
    
    return render_template('training/submit.html', user=current_user)

@training.route('/training/list')
@login_required
@admin_or_volunteer_required
def list_trainings():
    """Listar dados de treinamento"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = TrainingData.query
    
    # Filtrar por status se especificado
    if status_filter != 'all':
        try:
            status_enum = TrainingDataStatus(status_filter)
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass  # Status inválido, ignorar filtro
    
    # Se não for admin, mostrar apenas os próprios dados
    if not current_user.is_admin:
        query = query.filter_by(submitted_by=current_user.id)
    
    trainings = query.order_by(TrainingData.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('training/list.html', 
                         trainings=trainings, 
                         status_filter=status_filter,
                         user=current_user)

@training.route('/training/<int:training_id>')
@login_required
@admin_or_volunteer_required
def view_training(training_id):
    """Visualizar detalhes de um treinamento"""
    training_data = TrainingData.query.get_or_404(training_id)
    
    # Verificar permissão
    if not current_user.is_admin and training_data.submitted_by != current_user.id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('training.index'))
    
    return render_template('training/view.html', 
                         training=training_data,
                         user=current_user)

@training.route('/training/<int:training_id>/validate', methods=['POST'])
@login_required
def validate_training(training_id):
    """Validar/revalidar um treinamento (apenas admins)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    training_data = TrainingData.query.get_or_404(training_id)
    action = request.json.get('action')  # 'approve' ou 'reject'
    notes = request.json.get('notes', '')
    
    try:
        if action == 'approve':
            training_data.approve(current_user.id, notes)
            message = 'Treinamento aprovado com sucesso!'
        elif action == 'reject':
            if not notes:
                return jsonify({
                    'success': False, 
                    'message': 'Notas são obrigatórias para rejeição'
                }), 400
            training_data.reject(current_user.id, notes)
            message = 'Treinamento rejeitado.'
        else:
            return jsonify({
                'success': False, 
                'message': 'Ação inválida'
            }), 400
        
        return jsonify({
            'success': True, 
            'message': message,
            'new_status': training_data.status.value
        })
        
    except Exception as e:
        logger.error(f"Erro ao validar treinamento: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Erro interno: {str(e)}'
        }), 500

@training.route('/training/api/stats')
@login_required
@admin_or_volunteer_required
def api_stats():
    """API para estatísticas de treinamento"""
    if current_user.is_admin:
        # Admin vê estatísticas globais
        stats = {
            'total': TrainingData.query.count(),
            'approved': TrainingData.query.filter_by(status=TrainingDataStatus.APPROVED).count(),
            'pending': TrainingData.query.filter_by(status=TrainingDataStatus.PENDING).count(),
            'rejected': TrainingData.query.filter_by(status=TrainingDataStatus.REJECTED).count(),
            'processed': TrainingData.query.filter_by(status=TrainingDataStatus.PROCESSED).count()
        }
    else:
        # Usuário normal vê apenas suas estatísticas
        stats = {
            'total': TrainingData.query.filter_by(submitted_by=current_user.id).count(),
            'approved': TrainingData.query.filter_by(
                submitted_by=current_user.id, 
                status=TrainingDataStatus.APPROVED
            ).count(),
            'pending': TrainingData.query.filter_by(
                submitted_by=current_user.id, 
                status=TrainingDataStatus.PENDING
            ).count(),
            'rejected': TrainingData.query.filter_by(
                submitted_by=current_user.id, 
                status=TrainingDataStatus.REJECTED
            ).count(),
            'processed': TrainingData.query.filter_by(
                submitted_by=current_user.id, 
                status=TrainingDataStatus.PROCESSED
            ).count()
        }
    
    return jsonify(stats)
