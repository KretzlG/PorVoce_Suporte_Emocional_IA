import pytest

from flask import Flask
from flask_jwt_extended import create_access_token
from flask_jwt_extended.exceptions import NoAuthorizationError
from app.routes.api import api as api_blueprint
from app.models.user import User, UserRole

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user():
    return User(id=1, email='api@teste.com', username='apiuser', first_name='Api', last_name='User', role=UserRole.CLIENT)

def test_api_chat_sessions_unauth(client):
    try:
        resp = client.get('/api/chat/sessions')
        # Se não lançar exceção, deve retornar 401
        assert resp.status_code == 401
    except NoAuthorizationError:
        # Se lançar, é o esperado para ausência de header
        assert True

# Para testar endpoints autenticados, seria necessário mockar o JWT e o banco.
# Exemplos reais dependem de setup de banco e contexto Flask completo.
