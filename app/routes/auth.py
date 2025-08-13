"""
Rotas de autenticação
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash
from app.models import User
from app import db
import re

auth = Blueprint('auth', __name__)


def validate_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Valida força da senha"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r'[0-9]', password):
        return False, "A senha deve conter pelo menos um número"
    
    return True, "Senha válida"


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        data = request.form
        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirm = data.get('confirm_password', '')
        role = data.get('role', 'cliente')

        errors = []
        if not email or not validate_email(email):
            errors.append('Email inválido')
        if not username or len(username) < 3:
            errors.append('Nome de usuário deve ter pelo menos 3 caracteres')
        if User.query.filter_by(email=email).first():
            errors.append('Email já está em uso')
        if User.query.filter_by(username=username).first():
            errors.append('Nome de usuário já está em uso')
        if len(password) < 6:
            errors.append('A senha deve ter pelo menos 6 caracteres')
        if password != confirm:
            errors.append('As senhas não coincidem')
        if role not in ['cliente', 'voluntario']:
            errors.append('Tipo de usuário inválido')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')

        from werkzeug.security import generate_password_hash
        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            role=role
        )
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('main.dashboard'))
        except Exception:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'danger')
            return render_template('auth/register.html')

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário"""
    if current_user.is_authenticated:
        # Redireciona conforme o papel
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif hasattr(current_user, 'is_volunteer') and current_user.is_volunteer:
            return redirect(url_for('volunteer.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        data = request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            flash('Preencha todos os campos.', 'danger')
            return render_template('auth/login.html')

        from werkzeug.security import check_password_hash
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # Redireciona conforme o papel
            if hasattr(user, 'is_admin') and user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif hasattr(user, 'is_volunteer') and user.is_volunteer:
                return redirect(url_for('volunteer.dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('main.index'))


@auth.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    return render_template('auth/profile.html', user=current_user)


@auth.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Editar perfil do usuário"""
    data = request.get_json() if request.is_json else request.form
    
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    phone = data.get('phone', '').strip()
    age = data.get('age')
    
    # Validações
    errors = []
    
    if age:
        try:
            age = int(age)
            if age < 13 or age > 120:
                errors.append('Idade deve estar entre 13 e 120 anos')
        except ValueError:
            errors.append('Idade deve ser um número válido')
    
    if phone and not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', phone):
        errors.append('Telefone deve estar no formato (XX) XXXXX-XXXX')
    
    if errors:
        if request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400
        else:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('auth.profile'))
    
    # Atualizar dados
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.phone = phone
    current_user.age = age
    current_user.updated_at = db.func.now()
    
    try:
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Perfil atualizado com sucesso!',
                'user': current_user.to_dict()
            })
        else:
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('auth.profile'))
            
    except Exception:
        db.session.rollback()
        error_msg = 'Erro ao atualizar perfil. Tente novamente.'
        
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('auth.profile'))


@auth.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Renovar token de acesso"""
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': new_token
    })


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Recuperação de senha"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Email é obrigatório', 'error')
            return render_template('auth/forgot_password.html')
        
        if not validate_email(email):
            flash('Email inválido', 'error')
            return render_template('auth/forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        if user:
            # TODO: Implementar envio de email com token de reset
            flash('Se o email existir em nossa base, você receberá instruções para recuperar sua senha.', 'info')
        else:
            # Por segurança, sempre mostrar a mesma mensagem
            flash('Se o email existir em nossa base, você receberá instruções para recuperar sua senha.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth.route('/api/me')
@jwt_required()
def get_current_user():
    """Obter dados do usuário atual via API"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify({
        'user': user.to_dict()
    })


@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Configurações do usuário"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Atualizar preferências de notificação
        if 'notification_preferences' in data:
            current_user.notification_preferences = data['notification_preferences']
        
        # Atualizar configurações de privacidade
        if 'privacy_consent' in data:
            current_user.privacy_consent = bool(data['privacy_consent'])
        
        db.session.commit()
        flash('Configurações atualizadas com sucesso!', 'success')
        
        if request.is_json:
            return jsonify({'message': 'Configurações atualizadas'})
        
        return redirect(url_for('auth.settings'))
    
    return render_template('auth/settings.html')


@auth.route('/export-data')
@login_required
def export_data():
    """Exportar dados do usuário (LGPD)"""
    from app.services.anonymization import DataAnonymizer
    import json
    from flask import make_response
    
    # Coletar todos os dados do usuário
    user_data = {
        'user_info': current_user.to_dict(),
        'chat_sessions': [session.to_dict() for session in current_user.chat_sessions],
        'diary_entries': [entry.to_dict() for entry in current_user.diary_entries],
        'risk_assessments': [assessment.to_dict() for assessment in current_user.risk_assessments]
    }
    
    # Criar resposta JSON para download
    response = make_response(json.dumps(user_data, indent=2, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=foryou_dados_{current_user.username}.json'
    
    return response


@auth.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Exclusão de conta (LGPD)"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirmation = request.form.get('confirmation', '')
        
        if not current_user.check_password(password):
            flash('Senha incorreta', 'error')
            return render_template('auth/delete_account.html')
        
        if confirmation != 'EXCLUIR':
            flash('Digite "EXCLUIR" para confirmar', 'error')
            return render_template('auth/delete_account.html')
        
        # Anonimizar dados antes de excluir (conformidade LGPD)
        from app.services.anonymization import DataAnonymizer
        anonymizer = DataAnonymizer()
        
        # Anonimizar dados em chat sessions
        for session in current_user.chat_sessions:
            for message in session.messages:
                message.content = anonymizer.anonymize_text_content(message.content)
        
        # Anonimizar entradas do diário
        for entry in current_user.diary_entries:
            entry.title = anonymizer.anonymize_text_content(entry.title)
            entry.content = anonymizer.anonymize_text_content(entry.content)
        
        # Marcar usuário como deletado em vez de excluir (auditoria)
        current_user.is_active = False
        current_user.email = anonymizer.anonymize_email(current_user.email)
        current_user.username = f"deleted_user_{current_user.id}"
        current_user.first_name = "Usuário"
        current_user.last_name = "Excluído"
        current_user.phone = None
        
        db.session.commit()
        logout_user()
        
        flash('Sua conta foi excluída com sucesso. Seus dados foram anonimizados conforme a LGPD.', 'info')
        return redirect(url_for('main.index'))
    
    return render_template('auth/delete_account.html')
