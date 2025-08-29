"""
Rotas de triagem
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify

triagem = Blueprint('triage', __name__)


@triagem.route('/triage')
def triage():
    return "bomdia"  # Placeholder para a página de triagem