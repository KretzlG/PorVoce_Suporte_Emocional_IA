# 🚀 Deploy no Render - Guia Completo

## Pré-requisitos

1. **Conta no GitHub** com seu repositório
2. **Conta no Render** (gratuita) - https://render.com
3. **Chave da OpenAI** (opcional, mas recomendado para IA)

## 📋 Passo a Passo

### 1. Preparar o Repositório

✅ **Arquivos criados automaticamente:**
- `render.yaml` - Configuração do Render
- `build.sh` - Script de build
- `start.sh` - Script de inicialização
- `runtime.txt` - Versão do Python
- `Procfile` - Comando de execução
- `.env.production` - Exemplo de variáveis de ambiente

### 2. Fazer Push para GitHub

```bash
# Adicionar arquivos ao Git
git add .

# Commit das alterações
git commit -m "Adicionar configurações para deploy no Render"

# Push para GitHub
git push origin main
```

### 3. Criar Conta no Render

1. Acesse https://render.com
2. Clique em "Get Started for Free"
3. Conecte com sua conta do GitHub

### 4. Criar Banco de Dados PostgreSQL

1. No dashboard do Render, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - **Name**: `porvoce-db`
   - **Database**: `porvoce`
   - **User**: `porvoce_user`
   - **Region**: escolha a mais próxima
   - **Plan**: Free (0$/mês)
4. Clique em "Create Database"
5. **IMPORTANTE**: Anote a URL de conexão que aparecerá

### 5. Criar Web Service

1. No dashboard, clique em "New +"
2. Selecione "Web Service"
3. Conecte ao seu repositório GitHub
4. Configure:
   - **Name**: `porvoce-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Plan**: Free (0$/mês)

### 6. Configurar Variáveis de Ambiente

Na seção "Environment Variables", adicione:

```
FLASK_ENV=production
SECRET_KEY=[deixe vazio - será gerado automaticamente]
JWT_SECRET_KEY=[deixe vazio - será gerado automaticamente]
DATABASE_URL=[cole a URL do PostgreSQL criado no passo 4]
OPENAI_API_KEY=sk-sua_chave_openai_aqui
```

**Variáveis opcionais:**
```
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

### 7. Deploy

1. Clique em "Create Web Service"
2. O Render começará o build automaticamente
3. Aguarde o processo completar (5-10 minutos)

### 8. Verificar Logs

1. No dashboard do serviço, vá em "Logs"
2. Verifique se não há erros
3. Procure por mensagens como "✅ Build concluído"

### 9. Acessar a Aplicação

1. O Render fornecerá uma URL como: `https://porvoce-app.onrender.com`
2. Acesse a URL para verificar se funciona
3. Teste o login com: `admin@foryou.com` / `admin123`

## 🔧 Troubleshooting

### Erro de Build
- Verifique se `requirements.txt` está correto
- Logs dirão qual dependência está falhando

### Erro de Banco
- Verifique se `DATABASE_URL` está correta
- Teste a conexão no dashboard do PostgreSQL

### Erro de IA
- Verifique se `OPENAI_API_KEY` está correta
- A aplicação funciona sem IA, mas com funcionalidade limitada

### App não responde
- Verifique se `gunicorn` está no `requirements.txt`
- Verifique logs para erros de inicialização

## 📱 URLs Importantes

- **Dashboard Render**: https://dashboard.render.com
- **Documentação**: https://render.com/docs
- **Status**: https://status.render.com

## 🔒 Segurança

- Nunca commite arquivos `.env` com dados reais
- Use variáveis de ambiente do Render para dados sensíveis
- Regenere chaves secretas periodicamente

## 💡 Próximos Passos

1. Configurar domínio customizado (opcional)
2. Configurar SSL (automático no Render)
3. Monitorar performance
4. Configurar backups do banco

## 🆘 Precisa de Ajuda?

1. Logs no Render dashboard
2. GitHub Issues do projeto
3. Documentação do Render
4. Stack Overflow com tag `render`
