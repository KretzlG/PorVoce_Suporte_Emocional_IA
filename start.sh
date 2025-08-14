#!/usr/bin/env bash
# Script de inicialização para produção no Render

echo "🚀 Iniciando Por Você em produção..."

# Definir variável de ambiente Flask
export FLASK_APP=wsgi.py

# Executar migrações do banco de dados
echo "🔄 Executando migrações..."
flask db upgrade

# Inicializar dados básicos se necessário
echo "📊 Verificando dados iniciais..."
flask init-db || echo "Dados já existem ou erro na inicialização"

# Iniciar aplicação com Gunicorn
echo "🌐 Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 wsgi:app
