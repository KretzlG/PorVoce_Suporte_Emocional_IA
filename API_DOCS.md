# API de Suporte Emocional com IA

## Descrição
Esta API integra OpenAI GPT-3.5-turbo para fornecer suporte emocional através de chat, com classificação automática de risco e respostas de emergência.

## Endpoints Disponíveis

### 1. Chat com IA Emocional
**POST** `/api/chat`

Processa mensagem do usuário e retorna resposta da IA com classificação de risco.

**Request Body:**
```json
{
    "message": "Estou me sentindo muito triste hoje"
}
```

**Response:**
```json
{
    "response": "Entendo que você está passando por um momento difícil...",
    "risk_level": "moderado",
    "timestamp": null
}
```

**Níveis de Risco:**
- `baixo`: Situações normais, tristeza comum, ansiedade leve
- `moderado`: Ansiedade persistente, humor deprimido, problemas relacionais
- `alto`: Pensamentos de autolesão, ideação suicida, crises severas

### 2. Limpar Conversa
**POST** `/api/chat/clear`

Limpa o histórico da conversa atual.

**Response:**
```json
{
    "message": "Conversa limpa com sucesso"
}
```

### 3. Health Check
**GET** `/api/health`

Verifica se a API está funcionando.

**Response:**
```json
{
    "status": "ok",
    "service": "PorVoce Suporte Emocional IA",
    "ai_service": "OpenAI GPT-3.5-turbo"
}
```

## Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` com:

```env
OPENAI_API_KEY=sua_chave_api_aqui
FLASK_SECRET_KEY=sua_chave_secreta_flask_aqui
FLASK_ENV=development
```

### Como obter chave da OpenAI
1. Acesse: https://platform.openai.com/api-keys
2. Faça login/cadastro
3. Clique em "Create new secret key"
4. Copie a chave e cole no arquivo `.env`

## Instalação e Execução

### Windows (PowerShell)
```powershell
# Instalar dependências
.\setup.ps1

# Ou manualmente:
pip install -r requirements.txt

# Configurar .env com sua chave OpenAI
# Executar aplicação
python app.py
```

### Linux/Mac
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env com sua chave OpenAI
# Executar aplicação
python app.py
```

## Recursos de Segurança

### Classificação de Risco
O sistema analisa automaticamente as mensagens do usuário em busca de:

**Alto Risco:**
- Palavras relacionadas a suicídio
- Menções de autolesão
- Expressões de desistência da vida

**Risco Moderado:**
- Sintomas de depressão/ansiedade
- Sentimentos de desespero
- Problemas de sono/apetite

### Resposta de Emergência
Para casos de alto risco, o sistema:
1. Adiciona informações de contatos de emergência
2. Exibe banner de alerta na interface
3. Encoraja busca imediata por ajuda profissional

### Contatos de Emergência Incluídos
- **SAMU:** 192
- **Bombeiros:** 193  
- **CVV:** 188
- **Chat CVV:** https://www.cvv.org.br/

## Limitações e Ética

### O que a IA NÃO faz:
- Não substitui atendimento profissional
- Não fornece diagnósticos médicos
- Não prescreve medicamentos
- Não garante confidencialidade total

### Diretrizes Éticas:
- Sempre encoraja busca por ajuda profissional
- Mantém tom empático e não-julgamental
- Identifica e responde a situações de crise
- Usa linguagem acessível e inclusiva

## Desenvolvimento e Testes

### Estrutura do Projeto
```
PorVoce_Suporte_Emocional_IA/
├── app.py                 # Aplicação Flask principal
├── ai_service.py          # Serviço de IA/OpenAI
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente
├── setup.ps1             # Script de instalação Windows
├── templates/
│   └── chat.html         # Interface do chat
└── API_DOCS.md           # Esta documentação
```

### Testando a API

**Teste básico com curl:**
```bash
curl -X POST http://localhost:5000/api/health
```

**Teste do chat:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, como você pode me ajudar?"}'
```

## Próximos Passos

### Para Produção:
1. Configurar HTTPS
2. Implementar autenticação
3. Adicionar rate limiting
4. Configurar logging estruturado
5. Implementar monitoramento

### Melhorias Futuras:
1. Integração com banco de dados
2. Sistema de usuários e sessões
3. Dashboard administrativo
4. Análise de sentimentos mais avançada
5. Integração com serviços de saúde mental

## Suporte

Para dúvidas sobre a implementação:
1. Verifique os logs da aplicação
2. Confirme se a chave da OpenAI está configurada
3. Teste a conectividade com a API da OpenAI
4. Verifique se todas as dependências estão instaladas
