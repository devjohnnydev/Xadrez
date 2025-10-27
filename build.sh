#!/usr/bin/env bash
set -o errexit

echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "✅ Build concluído com sucesso!"
