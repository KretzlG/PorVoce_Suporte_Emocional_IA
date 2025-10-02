from flask import Blueprint, render_template, request, flash, redirect, url_for

bp_contato = Blueprint('contato', __name__)

@bp_contato.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        # Aqui você pode adicionar lógica para enviar email, salvar no banco, etc.
        flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('contato.contato'))
    return render_template('contato.html')
