import os
import pytest
from app.services.ai_service import AIService

@pytest.fixture(scope="module")
def ai_service():
    # Garante que as variáveis de ambiente estejam setadas para o teste
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")
    os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "test-key")
    os.environ["GEMINI_MODEL"] = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return AIService()

def test_fallback_openai(ai_service):
    # Testa fluxo normal (OpenAI configurado)
    ai_service.openai_client = None  # Força fallback
    ai_service.gemini_client = None
    ai_service.bert_pipeline = None
    resp = ai_service.generate_response("Oi, tudo bem?", risk_level="low")
    assert resp["source"] == "fallback"
    assert "message" in resp

def test_fallback_gemini(ai_service):
    # Testa fallback para Gemini
    ai_service.openai_client = None
    ai_service.gemini_client = None  # Força fallback
    ai_service.bert_pipeline = None
    resp = ai_service.generate_response("Oi, tudo bem?", risk_level="low")
    assert resp["source"] == "fallback"

def test_fallback_bert(ai_service):
    # Testa fallback para BERT
    ai_service.openai_client = None
    ai_service.gemini_client = None
    ai_service.bert_pipeline = None  # Força fallback
    resp = ai_service.generate_response("Oi, tudo bem?", risk_level="low")
    assert resp["source"] == "fallback"

def test_fallback_resposta_fixa(ai_service):
    # Testa resposta fixa (todos indisponíveis)
    ai_service.openai_client = None
    ai_service.gemini_client = None
    ai_service.bert_pipeline = None
    resp = ai_service.generate_response("Oi, tudo bem?", risk_level="low")
    assert resp["source"] == "fallback"
    assert "message" in resp
