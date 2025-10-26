# Torneio de Xadrez SENAI "Morvan Figueiredo"

Sistema web completo para gerenciamento de torneios de xadrez com sorteio automático baseado em compatibilidade de horários dos competidores.

## Funcionalidades

- ✅ **Cadastro de Competidores**: Formulário web e importação via CSV
- ✅ **Validação de Disponibilidade**: Sistema inteligente que valida compatibilidade de horários (períodos e dias da semana)
- ✅ **Sorteio Automático**: Algoritmo que forma pares apenas entre competidores com horários compatíveis
- ✅ **Chaveamento Estilo Copa**: Geração automática de quartas, semifinais e final
- ✅ **Gestão de Partidas**: Agendamento de datas, locais e registro de resultados
- ✅ **Dashboard Completo**: Visualização de inscrições, sorteio, partidas e ranking

## Tecnologias

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy
- **Frontend**: HTML + Tailwind CSS + JavaScript
- **Banco de Dados**: SQLite

## Como Usar

### 1. Executar o Sistema

O sistema já está configurado para rodar automaticamente. Basta acessar a interface web.

### 2. Cadastrar Competidores

**Opção 1 - Formulário Web:**
- Acesse a aba "Inscrição"
- Preencha os dados do competidor
- Clique em "Cadastrar Competidor"

**Opção 2 - Importar CSV:**
- Acesse a aba "Competidores"
- Clique em "Importar CSV"
- Selecione um arquivo CSV com o formato:
  ```
  nome,curso,telefone,periodo,dias_semana
  João Silva,LOG T1,11 98765-4321,manha,segunda a sexta
  Maria Santos,DEV S4,11 97654-3210,tarde,quarta e sexta
  ```

**Opção 3 - Script de Dados de Exemplo:**
```bash
python seed.py
```

### 3. Criar e Sortear Torneio

1. Acesse a aba "Sorteio"
2. Digite o nome do torneio (ex: "Torneio 2025 - Xadrez SENAI Morvan")
3. Clique em "Criar Torneio"
4. Opcionalmente, defina um seed para sorteio reprodutível
5. Clique em "Executar Sorteio"

O sistema irá:
- Agrupar competidores por compatibilidade de horários
- Formar pares válidos (com interseção de dias e períodos)
- Atribuir byes quando necessário
- Gerar o chaveamento completo

### 4. Gerenciar Partidas

1. Acesse a aba "Partidas"
2. Selecione o torneio
3. Para cada partida:
   - Clique em "Agendar Partida"
   - Defina data, hora e local
   - Opcionalmente, registre o resultado
   - O sistema avançará automaticamente o vencedor para a próxima fase

### 5. Visualizar Ranking

1. Acesse a aba "Ranking"
2. Selecione o torneio
3. Veja o chaveamento completo e o campeão (quando finalizado)

## Regras de Compatibilidade

### Períodos
- **Manhã**: disponível apenas no período da manhã
- **Tarde**: disponível apenas no período da tarde
- **Integral**: disponível manhã e tarde

### Dias da Semana
- **Segunda a Sexta**: seg, ter, qua, qui, sex
- **Segunda e Terça**: seg, ter
- **Quarta e Sexta**: qua, sex
- **Sexta**: sex

**Compatibilidade**: Dois competidores são compatíveis se tiverem ao menos um dia E um período em comum.

**Exemplos:**
- ✅ Manhã (seg-sex) x Integral (seg-ter) → Compatível (seg e ter pela manhã)
- ✅ Tarde (qua-sex) x Tarde (sexta) → Compatível (sexta à tarde)
- ❌ Manhã (seg-sex) x Tarde (seg-sex) → Incompatível (horários diferentes)
- ❌ Manhã (seg-ter) x Manhã (qua-sex) → Incompatível (sem dias em comum)

## Scripts Utilitários

### Adicionar Dados de Exemplo
```bash
python seed.py
```

### Exportar Partidas Agendadas
```bash
# Exportar todas as partidas
python export_csv.py

# Exportar partidas de um torneio específico
python export_csv.py 1
```

## Estrutura do Projeto

```
.
├── main.py              # Aplicação FastAPI principal
├── models.py            # Modelos do banco de dados
├── availability.py      # Lógica de compatibilidade
├── tournament.py        # Algoritmo de sorteio e chaveamento
├── seed.py             # Script para dados de exemplo
├── export_csv.py       # Exportação de partidas
├── templates/
│   └── index.html      # Interface web
└── torneio_xadrez.db   # Banco de dados SQLite (criado automaticamente)
```

## Formato CSV para Importação

```csv
nome,curso,telefone,periodo,dias_semana
Enner David Mamani Quispe,LOG T1,11 96549-8578,manha,segunda a sexta
Wellington de Jesus Andrade,LOG T1,11 94849-0469,manha,segunda a sexta
Vitor Antonio J. de Souza,DEV S4,11 94947-9289,tarde,segunda a sexta
Nicoly Kelly Villalba Gonsalez,2BT 4-6E,11 94880-6988,tarde,quarta e sexta
Gabriel Pedro de Souza,DEV SESI 4,11 98316-1432,integral,segunda e terca
Antonio Carlos Coelho Cajutio,AUTOCAD/Excel,11 99264-3674,tarde,sexta
```

**Valores válidos:**
- `periodo`: manha, tarde, integral
- `dias_semana`: segunda a sexta, segunda e terca, quarta e sexta, sexta

## Fluxo das Fases

O sistema gerencia automaticamente a progressão das fases:

1. **Fase Inicial** (determinada pelo número de participantes)
   - 2 jogadores: Final
   - 3-4 jogadores: Semifinal
   - 5-8 jogadores: Quartas
   - 9+ jogadores: Oitavas

2. **Avanço Automático**: Ao registrar o vencedor de uma partida, o sistema:
   - Marca o vencedor
   - Cria/atualiza a partida da próxima fase
   - Avança o vencedor automaticamente

3. **Final**: Ao registrar o vencedor da final, o torneio é marcado como finalizado e o campeão é exibido em destaque.

## Byes

Quando há número ímpar de competidores ou quando não há par compatível para um jogador:
- O jogador2_id fica NULL
- O jogador1 avança automaticamente para a próxima fase
- A partida é marcada como bye na interface

## Desenvolvido para

SENAI "Morvan Figueiredo"
