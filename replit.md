# Torneio de Xadrez SENAI "Morvan Figueiredo"

## Overview
Sistema web completo para gerenciamento de torneios de xadrez com sorteio automático baseado em compatibilidade de horários dos competidores.

## Recent Changes
- **2025-10-26**: Sistema completo implementado
  - Modelos de banco de dados (SQLAlchemy + SQLite)
  - Algoritmo de sorteio inteligente com validação de disponibilidade
  - API REST completa (FastAPI)
  - Interface web com Tailwind CSS
  - Scripts utilitários (seed.py, export_csv.py)

## Project Architecture

### Backend (Python + FastAPI)
- **models.py**: Modelos do banco de dados usando SQLAlchemy
  - Competidor: dados dos jogadores com período e dias disponíveis
  - Torneio: informações do torneio e status
  - Partida: jogos com fase, jogadores, resultado e vencedor

- **availability.py**: Lógica de compatibilidade
  - Mapeia períodos (manhã/tarde/integral) e dias da semana
  - Valida se dois competidores têm horários compatíveis
  - Verifica interseção de dias e períodos

- **tournament.py**: Algoritmo de sorteio
  - Agrupa competidores por disponibilidade
  - Cria pares compatíveis (com seed reprodutível)
  - Gera chaveamento automático (oitavas/quartas/semifinal/final)
  - Avança vencedores automaticamente

- **main.py**: Aplicação FastAPI
  - Endpoints RESTful para competidores, torneios, partidas
  - Importação de CSV
  - Templates Jinja2 para interface web

### Frontend (HTML + Tailwind CSS)
- **templates/index.html**: Interface web completa
  - Aba Inscrição: formulário de cadastro
  - Aba Competidores: listagem com filtros e importação CSV
  - Aba Sorteio: criação de torneio e execução de sorteio
  - Aba Partidas: agendamento e registro de resultados
  - Aba Ranking: visualização do chaveamento e campeão

### Utilities
- **seed.py**: Script para popular banco com dados de exemplo
- **export_csv.py**: Exporta partidas agendadas para CSV
- **exemplo_competidores.csv**: Arquivo CSV de exemplo para importação

## Key Features
1. **Validação de Compatibilidade**: Apenas competidores com horários compatíveis são pareados
2. **Sorteio Reprodutível**: Usa seed para gerar sempre o mesmo chaveamento
3. **Byes Automáticos**: Quando não há par compatível, o jogador passa automaticamente
4. **Avanço Automático**: Vencedores são movidos para a próxima fase automaticamente
5. **Chaveamento Dinâmico**: Fase inicial determinada pelo número de participantes

## Database Schema
- **competidores**: id, nome, curso, telefone, periodo, dias_semana
- **torneios**: id, nome, status, seed, created_at
- **partidas**: id, torneio_id, fase, jogador1_id, jogador2_id, data_hora, local, resultado, vencedor_id, observacoes, ordem

## How to Use
1. Execute `python seed.py` para adicionar dados de exemplo
2. Acesse a interface web
3. Crie um torneio na aba "Sorteio"
4. Execute o sorteio (com ou sem seed)
5. Agende partidas na aba "Partidas"
6. Registre resultados e acompanhe o ranking

## Technology Stack
- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Jinja2
- Tailwind CSS
- Uvicorn

## Development Guidelines
- O sistema valida compatibilidade baseada em interseção de dias E períodos
- Períodos: manhã, tarde, integral (manhã + tarde)
- Dias: segunda a sexta, segunda e terça, quarta e sexta, sexta
- Seed opcional para sorteios reprodutíveis
- Byes são atribuídos quando necessário
