# PorVocê - Suporte Emocional com IA

## 🎯 Visão Geral
Web app responsivo que oferece suporte emocional imediato em situações de crise, com triagem por IA de linguagem natural (OpenAI GPT-3.5-turbo) e encaminhamento automatizado. Baseado em Flask (Python) como backend principal.

## ✨ Funcionalidades Implementadas

### 🤖 Chat de Apoio com IA
- ✅ Interface de chat web responsiva e moderna
- ✅ Integração completa com OpenAI GPT-3.5-turbo
- ✅ Agente emocional especializado em suporte psicológico
- ✅ API REST Flask para comunicação com frontend

### 🚨 Triagem e Encaminhamento Automático
- ✅ Classificação automática de risco emocional (baixo/moderado/alto)
- ✅ Detecção de palavras-chave de crise e autolesão
- ✅ Resposta automática de emergência para situações críticas
- ✅ Contatos de emergência integrados (SAMU, CVV, etc.)

### 🔒 Segurança e Ética
- ✅ Diretrizes éticas para IA de suporte emocional
- ✅ Disclaimers sobre não substituição de atendimento profissional
- ✅ Identificação proativa de situações de crise
- ✅ Encaminhamento para serviços especializados

## ⚙️ Tecnologias Implementadas

| Camada | Stack | Status |
|--------|--------|--------|
| Frontend | HTML/CSS, Bootstrap 5, JavaScript | ✅ Implementado |
| Backend | Python + Flask | ✅ Implementado |
| IA / NLP | OpenAI GPT-3.5-turbo | ✅ Implementado |
| API | Flask REST API | ✅ Implementado |

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+
- Chave API da OpenAI

### Instalação Rápida (Windows)
```powershell
# 1. Clone o repositório
git clone https://github.com/KretzlG/PorVoce_Suporte_Emocional_IA.git
cd PorVoce_Suporte_Emocional_IA

# 2. Execute o script de instalação
.\setup.ps1

# 3. Configure sua chave da OpenAI no arquivo .env
# Edite: OPENAI_API_KEY=sua_chave_api_aqui

# 4. Execute a aplicação
python app.py
```

### Instalação Manual
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com sua chave da OpenAI

# 3. Executar aplicação
python app.py
```

### Obter Chave da OpenAI
1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave e adicione no arquivo `.env`

## 📱 Como Usar

1. **Acesse a aplicação:** http://localhost:5000
2. **Navegue para o chat:** /chat
3. **Digite sua mensagem** e receba suporte da IA
4. **Monitore o nível de risco** exibido com cada resposta
5. **Em caso de crise**, contatos de emergência são exibidos automaticamente

## 🔌 API Endpoints

### Chat com IA
```http
POST /api/chat
Content-Type: application/json

{
    "message": "Estou me sentindo muito triste"
}
```

**Resposta:**
```json
{
    "response": "Entendo que você está passando por um momento difícil...",
    "risk_level": "moderado",
    "timestamp": null
}
```

### Verificar Status
```http
GET /api/health
```

**Documentação completa:** [API_DOCS.md](API_DOCS.md)

## 🧩 Módulos Funcionais

### ✅ Implementados
- **Chat de Apoio com IA:** Interface completa + backend OpenAI
- **Triagem e Encaminhamento:** Classificação de risco automática
- **Sistema de Emergência:** Detecção e resposta a crises

### 🔄 Em Desenvolvimento
- **Diário Emocional:** Análise de texto para detecção de padrões
- **Dashboard Administrativo:** Visualização de métricas e alertas
- **Sistema de Autenticação:** Flask-Login + JWT
- **Banco de Dados:** PostgreSQL + SQLAlchemy

## 📊 Níveis de Risco

| Nível | Descrição | Ação Automática |
|-------|-----------|----------------|
| **Baixo** | Tristeza comum, ansiedade leve | Suporte padrão da IA |
| **Moderado** | Ansiedade persistente, humor deprimido | Encorajamento a buscar ajuda |
| **Alto** | Pensamentos suicidas, autolesão | **Exibição de contatos de emergência** |

## 🆘 Contatos de Emergência Integrados

- **SAMU:** 192
- **Bombeiros:** 193
- **CVV (Centro de Valorização da Vida):** 188
- **Chat CVV:** https://www.cvv.org.br/

## 🧱 Arquitetura Técnica

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│   Flask API      │────│   OpenAI API    │
│   (HTML/CSS/JS) │    │   (Python)       │    │   (GPT-3.5)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │   AI Service     │
                       │   (Risk Classify)│
                       └──────────────────┘
```

## 🧪 Roadmap

### ✅ Sprint 1 - CONCLUÍDO
- ✅ Estrutura base do Flask + interface de chat
- ✅ Integração completa com OpenAI GPT-3.5-turbo
- ✅ Sistema de classificação de risco
- ✅ Resposta automática de emergência

### 🔄 Sprint 2 - EM ANDAMENTO
- 🔄 Sistema de autenticação e usuários
- 🔄 Banco de dados PostgreSQL
- 🔄 Diário emocional com análise de padrões

### 📋 Sprint 3 - PLANEJADO
- 📋 Dashboard administrativo
- 📋 Estatísticas e métricas
- 📋 Deploy em produção (AWS/Heroku)

## 🔒 Considerações Éticas e Legais

### Limitações da IA
- **NÃO substitui** atendimento psicológico profissional
- **NÃO fornece** diagnósticos médicos
- **NÃO deve ser** a única fonte de apoio em crises

### Responsabilidades
- Sempre incentiva busca por ajuda profissional
- Identifica proativamente situações de risco
- Fornece contatos de emergência quando necessário
- Mantém tom empático e não-julgamental

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Contato

Para dúvidas sobre implementação ou contribuições, abra uma issue no GitHub.

---

**⚠️ AVISO IMPORTANTE:** Este sistema fornece apoio emocional inicial mas não substitui atendimento psicológico profissional. Em caso de emergência, procure ajuda imediatamente pelos canais oficiais de saúde mental.
