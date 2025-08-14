"""
Rotas do dashboard do voluntário
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

volunteer = Blueprint('volunteer', __name__)

@volunteer.route('/volunteer/dashboard')
@login_required
def dashboard():
    # Aqui você pode adicionar métricas específicas do voluntário, se desejar
    return render_template('dashboards/volunteer/dashboard.html', user=current_user)
