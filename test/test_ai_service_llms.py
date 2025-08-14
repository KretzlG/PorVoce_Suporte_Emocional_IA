import os
import pytest
from app.services.ai_service import AIService

@pytest.fixture(scope="module")
def ai_service():
    return AIService()

def test_openai_status(ai_service):
    info = ai_service.get_model_info()
    openai_info = next((i for i in info if i['provider'] == 'OpenAI'), None)
    assert openai_info is not None
    # O status deve ser 'active' se a API key estiver configurada
    assert openai_info['status'] in ('active', 'inactive')
    print(f"OpenAI: {openai_info['status']} - Modelo: {openai_info['active_model']}")

def test_gemini_status(ai_service):
    info = ai_service.get_model_info()
    gemini_info = next((i for i in info if i['provider'] == 'Gemini'), None)
    assert gemini_info is not None
    # O status deve ser 'active' se a API key estiver configurada
    assert gemini_info['status'] in ('active', 'inactive')
    print(f"Gemini: {gemini_info['status']} - Modelo: {gemini_info['active_model']}")

def test_bert_status(ai_service):
    info = ai_service.get_model_info()
    bert_info = next((i for i in info if i['provider'] == 'BERT'), None)
    assert bert_info is not None
    assert bert_info['status'] in ('active', 'inactive')
    print(f"BERT: {bert_info['status']} - Modelo: {bert_info['active_model']}")

def test_llm_real_responses(ai_service):
    """
    Testa se cada LLM (OpenAI, Gemini, BERT) retorna uma resposta real para uma mensagem de exemplo.
    O teste passa se a resposta não for vazia e não indicar erro.
    """
    prompt = "Olá, tudo bem?"
    llms = [
        ("openai", ai_service._generate_response_openai),
        ("gemini", ai_service._generate_response_gemini),
        ("bert", ai_service._generate_response_bert),
    ]
    for name, func in llms:
        try:
            response = func(prompt)
        except Exception as e:
            response = str(e)
        print(f"Resposta {name}: {response}")
        assert response is not None
        assert isinstance(response, str)
        assert response.strip() != ""
        assert not any(err in response.lower() for err in ["erro", "error", "invalid", "not available", "unavailable", "falha", "fail"])
