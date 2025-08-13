

import pytest
from flask import Flask
from app.routes.main import main as main_blueprint
import tempfile
import os

@pytest.fixture
def app(tmp_path):
    app = Flask(__name__)
    app.register_blueprint(main_blueprint)
    app.config['TESTING'] = True
    # Mock templates
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "index.html").write_text("index")
    (templates_dir / "about.html").write_text("about")
    app.template_folder = str(templates_dir)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    resp = client.get('/')
    assert resp.status_code in (200, 302)  # 302 se redirecionar para login

def test_health_route(client):
    resp = client.get('/health')
    assert resp.status_code in (200, 503)
    assert 'status' in resp.get_json()

def test_about_route(client):
    resp = client.get('/about')
    assert resp.status_code in (200, 302)
