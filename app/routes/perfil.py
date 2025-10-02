
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html', user=current_user)


@perfil_bp.route('/perfil/editar', methods=['POST'])
@login_required
def editar_perfil():
    nome = request.form.get('nome', '').strip()
    phone = request.form.get('phone', '').strip()
    age = request.form.get('age', '').strip()

    errors = []
    if not nome or len(nome) < 2:
        errors.append('Nome deve ter pelo menos 2 caracteres.')
    if age:
        try:
            age_int = int(age)
            if age_int < 13 or age_int > 120:
                errors.append('Idade deve estar entre 13 e 120 anos.')
        except ValueError:
            errors.append('Idade inválida.')

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('perfil.perfil'))

    current_user.nome = nome
    current_user.phone = phone
    current_user.age = int(age) if age else None
    db.session.commit()
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('perfil.perfil'))
