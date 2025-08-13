# Explicação dos Testes Automatizados

Este arquivo documenta o propósito de cada teste presente na pasta `test/` do projeto PorVocê.


## test_ai_service_fallback.py
Testa o fallback do serviço de IA:
- Garante que, se OpenAI, Gemini ou BERT estiverem indisponíveis, o sistema retorna respostas fixas.
- Valida o fluxo de fallback entre as LLMs e a robustez do serviço de IA.

## test_ai_service_llms.py
Testa o status e as respostas reais das LLMs disponíveis no sistema:
- Verifica se OpenAI, Gemini e BERT estão corretamente configurados e ativos ou inativos.
- Garante que o sistema reconhece corretamente o status de cada LLM.
- Testa se cada LLM retorna uma resposta real para um prompt de exemplo, validando que não retorna erro nem resposta vazia.

## test_db_connection.py
Testa a conexão com o banco de dados:
- Verifica se a conexão com o PostgreSQL está funcionando.
- Testa a conexão via SQLAlchemy.
- Garante que o ambiente está pronto para operações de banco.

## test_models.py
Testa o modelo User:
- Criação de usuário.
- Métodos de senha (set/check password).
- Propriedades como full_name, is_client, is_admin.
- Serve de exemplo para expandir testes de outros modelos.

## test_routes.py
Testa rotas principais do sistema:
- `/` (index): verifica se a rota principal responde.
- `/health`: verifica se o health check responde e retorna status do banco.
- `/about`: verifica se a página sobre responde.
- Usa templates mockados para evitar dependência do frontend.

## test_api.py
Testa endpoints da API protegidos por JWT:
- `/api/chat/sessions`: garante que endpoints protegidos exigem autenticação.
- O teste espera erro de autenticação (401 ou exceção NoAuthorizationError) quando não há JWT.
- Serve de base para expandir testes de API autenticada.

## test_services.py
Template para testes de outros serviços (ex: análise de risco, agendamento, etc).

## test_utils.py
Template para testes de funções utilitárias do projeto.

---

Para expandir a cobertura, basta seguir os exemplos e criar novos testes para cada funcionalidade implementada.
