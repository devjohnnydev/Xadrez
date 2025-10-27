# Sistema de Torneio de Xadrez SENAI - Morvan Figueiredo

## Visão Geral
Sistema completo de gerenciamento de torneios de xadrez para o SENAI "Morvan Figueiredo", com geração automática de chaveamento baseada em compatibilidade de horários, autenticação administrativa, upload de fotos e identidade visual SENAI (vermelho e branco).

## Funcionalidades Principais

### ✅ Implementadas
1. **Cadastro de Competidores**
   - Formulário completo com nome, curso, telefone, período (manhã/tarde/integral)
   - Seleção de dias da semana disponíveis via checkboxes (seg, ter, qua, qui, sex)
   - Upload de fotos dos jogadores (armazenadas em `static/uploads/`)
   - Importação via CSV em massa

2. **Sistema de Autenticação**
   - Login administrativo com HTTP Basic Auth
   - Credenciais: `Biblioteca@senaimovanfigueiredo.com.br` / `biblioteca103103`
   - Área pública sem autenticação (visualização de resultados)
   - Área administrativa protegida (gerenciamento completo)

3. **Sorteio Inteligente**
   - Algoritmo que valida compatibilidade de horários (período + dias da semana)
   - Avanço automático de vencedores com BYE
   - Seed opcional para sorteios reproduzíveis
   - Detecção automática de fase inicial baseada no número de inscritos

4. **Gerenciamento de Partidas**
   - Agendamento com data, hora e local
   - Registro de resultados e vencedores
   - Avanço automático de vencedores para próximas fases
   - Visualização de chaveamento completo

5. **Área Pública**
   - Visualização de próximos jogos agendados
   - Resultados de partidas finalizadas
   - Chaveamento completo do torneio
   - Display de campeão ao final
   - Exibição de fotos dos jogadores

6. **Identidade Visual SENAI**
   - Cores: vermelho (#E30613) e branco
   - Layout responsivo com Tailwind CSS
   - Fotos circulares dos jogadores em toda a interface

## Estrutura do Projeto

```
/
├── main.py                     # API FastAPI principal
├── models.py                   # Modelos SQLAlchemy (Competidor, Torneio, Partida)
├── auth.py                     # Sistema de autenticação
├── availability.py             # Lógica de compatibilidade de horários
├── tournament.py               # Algoritmo de sorteio e chaveamento
├── seed.py                     # Script para popular banco com dados de exemplo
├── export_csv.py               # Script para exportar dados
├── exemplo_competidores.csv    # Exemplo de CSV para importação
├── templates/
│   ├── public.html            # Interface pública (sem autenticação)
│   └── admin.html             # Interface administrativa (com autenticação)
├── static/
│   └── uploads/               # Diretório para fotos dos jogadores
└── torneio_xadrez.db          # Banco SQLite
```

## Tecnologias

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: HTML + JavaScript + Tailwind CSS
- **Autenticação**: HTTP Basic Auth
- **Upload de Arquivos**: FastAPI File Upload

## Mudanças Recentes (27 de outubro de 2025)

### ✨ Novas Funcionalidades Implementadas

#### 1. Sistema de Autenticação Moderno
- **Tela de login dedicada** com design moderno e responsivo
- **Sessões JWT** com cookies HttpOnly (proteção contra XSS)
- **Hash de senhas** com bcrypt para segurança
- **Botão de logout** na área administrativa
- **Redirecionamento automático** para login se não autenticado

**Credenciais de Login:**
- Email: `Biblioteca@senaimovanfigueiredo.com.br`
- Senha: `biblioteca103103`

#### 2. Calendário Moderno para Agendamento
- **Date-time picker HTML5** nativo para selecionar data e hora
- **Modal bonito** substituindo prompts simples
- **Registro de resultados** diretamente no agendamento
- **Validação de campos** obrigatórios

#### 3. Histórico de Campeões
- **Nova aba "Histórico de Campeões"** na área pública
- **Visualização de todos os campeões** de torneios finalizados
- **Medalhas** para os 3 primeiros (🥇🥈🥉)
- **Fotos e informações** completas dos campeões
- **Data do torneio** para cada conquista

#### 4. Sistema de Eliminatórias Completo
- Sistema já existia e continua funcionando perfeitamente
- **Múltiplas rodadas** até definir o campeão
- **Avanço automático** de vencedores
- **BYEs** tratados corretamente

### Mudanças de Segurança
- **JWT Secret Key**: Agora estável (não muda a cada reinício)
- **Senhas hasheadas**: Bcrypt com custo 12
- **Cookies seguros**: HttpOnly, SameSite=Lax, Secure em produção
- **Sem plaintext**: Senhas nunca armazenadas em texto puro

## Como Usar

### 1. Acesso
- **Área Pública**: Acesse `/` para ver resultados e próximos jogos
- **Área Admin**: Acesse `/admin` e faça login com as credenciais

### 2. Cadastrar Competidores
- Vá em "Cadastrar Competidor"
- Preencha todos os campos obrigatórios
- Selecione os dias da semana disponíveis
- Opcionalmente, adicione uma foto
- Clique em "Cadastrar"

### 3. Criar e Sortear Torneio
- Vá em "Sorteio"
- Crie um novo torneio ou selecione um existente
- Opcionalmente, defina uma seed para reproduzibilidade
- Clique em "Executar Sorteio"
- O sistema criará o chaveamento automaticamente

### 4. Gerenciar Partidas
- Vá em "Gerenciar Partidas"
- Selecione o torneio
- Para cada partida, clique em "Agendar" ou "Editar"
- Defina data/hora, local e resultado
- Vencedores avançam automaticamente

## Preferências do Usuário

- **Cores**: Sempre usar vermelho (#E30613) e branco (identidade SENAI)
- **Autenticação**: Admin usa `Biblioteca@senaimovanfigueiredo.com.br`
- **Disponibilidade**: Dias como checkboxes para máxima flexibilidade
- **Fotos**: Opcional mas recomendado para melhor experiência

## Arquitetura

### Modelo de Dados
- **Competidor**: nome, curso, telefone, período, dias_semana (string), foto_url
- **Torneio**: nome, status, seed
- **Partida**: torneio, fase, jogadores, resultado, vencedor, data/hora, local

### Lógica de Compatibilidade
- Jogadores são compatíveis se compartilham pelo menos 1 dia E 1 período em comum
- Sistema valida compatibilidade antes de criar partidas
- BYEs são atribuídos quando número de inscritos não é potência de 2

### Segurança
- **Autenticação JWT** com sessões baseadas em cookies
- **Hash bcrypt** para armazenamento seguro de senhas (custo 12)
- **Cookies HttpOnly** para proteção contra XSS
- **SameSite=Lax** para proteção contra CSRF
- **Secure flag** habilitado automaticamente em produção
- **Upload de fotos** com nomes únicos baseados em timestamp
- **Variáveis de ambiente** para configurações sensíveis

## Scripts Úteis

```bash
# Popular banco com dados de exemplo
python seed.py

# Exportar dados para CSV (se necessário)
python export_csv.py
```

## Desenvolvimento Futuro (Sugestões)

1. **Segurança**
   - Hash de senhas (bcrypt)
   - Validação de tipo de arquivo em uploads
   - CORS configurado corretamente

2. **Funcionalidades**
   - Sistema de ELO/ranking
   - Histórico de torneios por jogador
   - Notificações automáticas (e-mail/SMS)
   - Geração de certificados

3. **Performance**
   - Migração para PostgreSQL para produção
   - Cache de resultados
   - Otimização de queries

## Notas Importantes

- Banco SQLite para desenvolvimento (trocar para PostgreSQL em produção)
- Tailwind CDN usado para prototipação rápida (build para produção)
- Fotos armazenadas localmente (considerar cloud storage para produção)
- Autenticação básica adequada para ambiente interno SENAI
