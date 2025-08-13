# Por Você - Plataforma de Apoio Emocional

Uma plataforma web para apoio emocional com chat por IA e voluntários qualificados.

## 🚀 Setup Rápido

### 1. Clonar e Instalar

```bash
git clone https://github.com/GianKretzl/PorVoce.git
cd PorVoce

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

```bash
# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações do PostgreSQL

# Criar migrações (só na primeira vez)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Inserir dados de teste
flask init-db
```

### 3. Executar

```bash
python wsgi.py
```

## 🛠️ Comandos Úteis

```bash
# Criar nova migração
flask db migrate -m "Descrição da mudança"

# Aplicar migrações
flask db upgrade

# Inserir dados de teste
flask init-db

# Shell interativo com contexto
flask shell
```

## 👥 Usuários de Teste

- **Admin**: `admin@porvoce.com` / `admin123`
- **Cliente**: `cliente@teste.com` / `cliente123`
- **Voluntário**: `voluntario@teste.com` / `voluntario123`
- **Voluntária**: `ana.voluntaria@teste.com` / `ana123`

## 🏗️ Estrutura do Projeto

```
PorVoce/
├── app/
│   ├── models/          # Modelos do banco de dados
│   ├── routes/          # Rotas da aplicação
│   ├── services/        # Serviços (IA, análise de risco)
│   ├── static/          # CSS, JS, imagens
│   ├── templates/       # Templates HTML
│   └── commands.py      # Comandos Flask CLI
├── migrations/          # Migrações do banco
├── config.py           # Configurações
├── requirements.txt    # Dependências
└── wsgi.py             # Ponto de entrada WSGI
```

## 📊 Modelos de Dados

- **User**: Usuários (Admin, Cliente, Voluntário)
- **ChatSession**: Sessões de chat
- **ChatMessage**: Mensagens individuais
- **DiaryEntry**: Entradas do diário
- **Volunteer**: Perfis de voluntários
- **VolunteerSkill**: Habilidades dos voluntários
- **VolunteerAvailability**: Disponibilidade
- **TriageLog**: Logs de triagem de risco
- **AdminLog**: Logs administrativos


## 🤖 Inteligência Artificial com Fallback LLM

O sistema de IA do PorVocê utiliza um fluxo de fallback para garantir respostas automáticas mesmo em caso de falha de algum provedor:

1. **OpenAI** (GPT-3.5-turbo ou outro modelo configurado)
2. **Gemini** (Google, modelo gratuito gemini-1.5-flash)
3. **BERT** (modelo neuralmind/bert-base-portuguese-cased)
4. **Respostas fixas** (mensagens empáticas pré-definidas)

O fallback é automático: se o provedor principal estiver indisponível, o sistema tenta o próximo da lista, garantindo robustez e disponibilidade.

Para usar Gemini, configure as variáveis no seu `.env`:

```
GEMINI_API_KEY=...sua chave...
GEMINI_MODEL=gemini-1.5-flash
```

## 🔧 Tecnologias

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Migrações**: Flask-Migrate (Alembic)
- **Autenticação**: Werkzeug Security
- **Frontend**: HTML, CSS, JavaScript
- **IA**: OpenAI, Gemini, BERT, fallback automático

## 📝 Desenvolvimento

### Adicionar Nova Funcionalidade

1. Criar/modificar modelos em `app/models/`
2. Gerar migração: `flask db migrate -m "Descrição"`
3. Aplicar migração: `flask db upgrade`
4. Implementar rotas em `app/routes/`
5. Criar templates em `app/templates/`

### Deploy em Nova Máquina

```bash
# 1. Clonar repositório
git clone https://github.com/GianKretzl/PorVoce.git
cd PorVoce

# 2. Configurar ambiente
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configurar .env com PostgreSQL

# 4. Aplicar migrações
flask db upgrade

# 5. Inserir dados de teste
flask init-db

# 6. Executar
python wsgi.py
```

## 🎯 Sistema de Migrações

O projeto usa **Flask-Migrate** para gerenciar mudanças no banco:

- ✅ **Portabilidade**: Funciona em qualquer máquina
- ✅ **Versionamento**: Controle de versão do schema
- ✅ **Automação**: Comandos simples para atualizar
- ✅ **Rollback**: Pode desfazer migrações se necessário

### Comandos de Migração

```bash
# Ver status das migrações
flask db current

# Ver histórico
flask db history

# Fazer rollback
flask db downgrade

# Atualizar para versão específica
flask db upgrade <revision>
```

## 🛡️ Conformidade LGPD

- ✅ Consentimento explícito
- ✅ Anonimização automática
- ✅ Logs de auditoria
- ✅ Direito ao esquecimento
- ✅ Exportação de dados

## 🎯 Próximos Passos

- [ ] Implementar autenticação nas rotas
- [ ] Criar interfaces para cada tipo de usuário
- [ ] Integrar serviços de IA
- [ ] Testes automatizados
- [ ] Deploy em produção
