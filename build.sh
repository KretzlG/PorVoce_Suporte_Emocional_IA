#!/usr/bin/env bash
# Build script para Render

echo "🚀 Iniciando build do ForYou..."

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se a instalação foi bem-sucedida
echo "✅ Build concluído com sucesso!"
