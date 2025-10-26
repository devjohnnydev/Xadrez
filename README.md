# 🏆 Sistema de Torneio de Xadrez SENAI - Morvan Figueiredo

Sistema completo de gerenciamento de torneios de xadrez com sorteio inteligente baseado em compatibilidade de horários, autenticação administrativa, upload de fotos e identidade visual SENAI.

## 🎯 Funcionalidades

### Para Administradores
- ✅ **Cadastro de Competidores** com foto, curso, telefone e disponibilidade
- ✅ **Seleção flexível de dias** via checkboxes (segunda a sexta)
- ✅ **Importação em massa** via CSV
- ✅ **Sorteio automático** com validação de compatibilidade de horários
- ✅ **Gerenciamento de partidas** com agendamento e resultados
- ✅ **Autenticação segura** com HTTP Basic Auth

### Para Alunos (Área Pública)
- 📅 **Visualização de próximos jogos** agendados
- 🏆 **Resultados** de partidas finalizadas
- 📊 **Chaveamento completo** do torneio
- 🎖️ **Display de campeão** ao final

## 🚀 Como Usar

### 1️⃣ Acesse o Sistema
- **Área Pública**: `/` (sem login necessário)
- **Área Admin**: `/admin` (requer login)

### 2️⃣ Login Administrativo
```
Usuário: Biblioteca@senaimovanfigueiredo.com.br
Senha: biblioteca103103
```

### 3️⃣ Cadastrar Competidores

**Opção A - Via Formulário:**
1. Acesse "Cadastrar Competidor"
2. Preencha: nome, curso, telefone
3. Selecione o período (manhã/tarde/integral)
4. Marque os dias disponíveis (checkboxes)
5. Opcionalmente, adicione uma foto
6. Clique em "Cadastrar"

**Opção B - Via CSV:**
1. Prepare um arquivo CSV com as colunas: `nome,curso,telefone,periodo,dias_semana`
2. Exemplo:
```csv
nome,curso,telefone,periodo,dias_semana
João Silva,LOG T1,11 98765-4321,manha,seg,ter,qua,qui,sex
Maria Santos,DEV S4,11 97654-3210,tarde,seg,qua,sex
```
3. Clique em "Importar CSV" na aba "Competidores"

**Opção C - Script de Dados de Exemplo:**
```bash
python seed.py
```

### 4️⃣ Criar e Sortear Torneio

1. Acesse "Sorteio"
2. Digite o nome do torneio e clique em "Criar Torneio"
3. Selecione o torneio criado
4. (Opcional) Defina uma seed para sorteio reproduzível
5. Clique em "Executar Sorteio"

**O sistema irá:**
- ✅ Verificar compatibilidade de horários entre jogadores
- ✅ Criar chaveamento automático
- ✅ Atribuir BYEs quando necessário
- ✅ Avançar vencedores de BYE automaticamente

### 5️⃣ Gerenciar Partidas

1. Acesse "Gerenciar Partidas"
2. Selecione o torneio
3. Para cada partida:
   - Clique em "Agendar Partida"
   - Defina data/hora (formato: YYYY-MM-DD HH:MM)
   - Defina o local
   - (Opcional) Registre o resultado
4. Vencedores avançam automaticamente para a próxima fase

## 🎨 Identidade Visual

- **Cores**: Vermelho SENAI (#E30613) e Branco
- **Layout**: Responsivo com Tailwind CSS
- **Fotos**: Exibição circular dos jogadores em toda interface

## 📋 Tecnologias

- **Backend**: Python 3.11 + FastAPI + SQLAlchemy
- **Frontend**: HTML + Tailwind CSS + JavaScript
- **Banco de Dados**: SQLite
- **Autenticação**: HTTP Basic Auth
- **Upload**: FastAPI File Upload

## 🎲 Como Funciona o Sorteio

### Compatibilidade de Horários
Dois jogadores são compatíveis se compartilham:
- **Pelo menos 1 dia** em comum (seg, ter, qua, qui, sex)
- **Pelo menos 1 período** em comum (manhã, tarde ou integral)

**Exemplos:**
```
✅ João (manhã, seg-ter-qua) vs Maria (manhã, ter-qui-sex) → Compatíveis (manhã + ter)
❌ Pedro (manhã, seg-ter) vs Ana (tarde, qua-qui) → Incompatíveis
✅ Carlos (integral, seg-sex) vs Lucia (tarde, sex) → Compatíveis (tarde + sex)
```

### Períodos
- **Manhã**: disponível apenas no período da manhã
- **Tarde**: disponível apenas no período da tarde
- **Integral**: disponível manhã e tarde

### BYEs Automáticos
- Quando o número de inscritos não é potência de 2 (4, 8, 16, 32...)
- BYEs são atribuídos na primeira fase
- Vencedores de BYE avançam automaticamente

## 📊 Fluxo das Fases

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

## 🗂️ Estrutura do Projeto

```
/
├── main.py                  # API FastAPI principal
├── models.py                # Modelos de dados
├── auth.py                  # Sistema de autenticação
├── availability.py          # Lógica de compatibilidade
├── tournament.py            # Algoritmo de sorteio
├── seed.py                  # Dados de exemplo
├── export_csv.py            # Exportação de partidas
├── exemplo_competidores.csv # Exemplo de CSV
├── templates/
│   ├── public.html         # Interface pública
│   └── admin.html          # Interface administrativa
└── static/
    └── uploads/            # Fotos dos jogadores
```

## 📝 Scripts Utilitários

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

## 🔐 Segurança

- ✅ Autenticação HTTP Basic para área administrativa
- ✅ Endpoints de modificação protegidos
- ✅ Área pública sem autenticação (apenas visualização)
- ✅ Upload de fotos com nomes únicos baseados em timestamp

**Para produção:**
- Considere hash de senhas (bcrypt)
- Adicione validação de tipo de arquivo em uploads
- Configure CORS adequadamente
- Migre para PostgreSQL

## 🆘 Solução de Problemas

**Erro ao sortear:**
- Verifique se há competidores cadastrados
- Certifique-se de que selecionou um torneio

**Partidas não aparecem:**
- Verifique se o sorteio foi executado
- Atualize a página

**Foto não aparece:**
- Verifique se o arquivo é JPG ou PNG
- Tamanho recomendado: até 5MB

**Não consigo acessar área admin:**
- Verifique usuário: `Biblioteca@senaimovanfigueiredo.com.br`
- Verifique senha: `biblioteca103103`

## 🎓 Sobre o SENAI Morvan Figueiredo

Este sistema foi desenvolvido especificamente para o SENAI "Morvan Figueiredo", respeitando a identidade visual da instituição (vermelho e branco) e as necessidades operacionais de torneios internos de xadrez com validação de compatibilidade de horários entre alunos de diferentes cursos e períodos.

---

**Desenvolvido para SENAI - Morvan Figueiredo** 🏆♟️
