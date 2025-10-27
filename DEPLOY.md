# 🚀 Guia de Deploy no Render

## Pré-requisitos

- Conta no [Render](https://render.com) (gratuita)
- Conta no GitHub/GitLab para hospedar o código
- Repositório Git do projeto

## 📋 Passos para Deploy

### 1. Preparar o Repositório

Certifique-se de que os seguintes arquivos estão no repositório:

- ✅ `requirements.txt` - Dependências Python
- ✅ `render.yaml` - Configuração do Render
- ✅ `build.sh` - Script de build (opcional)
- ✅ `.gitignore` - Arquivos a ignorar

### 2. Enviar Código para o GitHub

```bash
# Inicializar Git (se ainda não foi feito)
git init

# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "Preparar para deploy no Render"

# Adicionar remote do GitHub
git remote add origin https://github.com/seu-usuario/torneio-xadrez-senai.git

# Enviar para o GitHub
git push -u origin main
```

### 3. Criar Web Service no Render

#### Opção A: Deploy Manual (Recomendado para Iniciantes)

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +" → "Web Service"**
3. Conecte sua conta do GitHub
4. Selecione o repositório do projeto
5. Configure o serviço:

   **Configurações Básicas:**
   - **Name**: `torneio-xadrez-senai` (ou qualquer nome)
   - **Language**: Python 3
   - **Branch**: `main`
   - **Region**: Escolha a mais próxima (ex: Oregon, USA)

   **Comandos de Build e Start:**
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:10000
     ```

   **Configurações Avançadas:**
   - **Plan**: Free (0.5 CPU, 512MB RAM)
   - **Auto-Deploy**: Yes (recomendado)

6. Clique em **"Create Web Service"**

#### Opção B: Deploy Automático com Blueprint

1. O arquivo `render.yaml` já está configurado
2. Acesse https://dashboard.render.com/blueprints
3. Clique em **"New Blueprint Instance"**
4. Selecione seu repositório
5. Clique em **"Connect"**

O Render vai:
- Ler o `render.yaml`
- Configurar automaticamente o serviço
- Fazer o primeiro deploy

### 4. Configurar Variáveis de Ambiente (Opcional)

No dashboard do Render, vá em **Environment** e adicione:

```
SECRET_KEY=sua-chave-secreta-aqui
ENVIRONMENT=production
```

**Nota**: `SECRET_KEY` é gerada automaticamente no `render.yaml`

### 5. Aguardar o Deploy

O Render vai:
1. ⬇️ Baixar seu código
2. 📦 Instalar dependências (`pip install -r requirements.txt`)
3. 🚀 Iniciar o servidor Gunicorn
4. ✅ Seu app estará online!

**URL final**: `https://torneio-xadrez-senai.onrender.com`

---

## 🎯 Verificar Deploy

Após o deploy, teste:

- 🏠 **Home**: https://seu-app.onrender.com/
- 📖 **Documentação API**: https://seu-app.onrender.com/docs
- 🔐 **Login Admin**: https://seu-app.onrender.com/login

---

## ⚙️ Configurações Importantes

### Porta

O Render usa automaticamente a **porta 10000**. Não mude!

```bash
# Correto (já configurado)
--bind 0.0.0.0:10000
```

### Workers

Para melhor performance na camada gratuita:

```bash
--workers 4  # 4 workers Gunicorn
```

### Auto-Deploy

Sempre que você fizer `git push`, o Render automaticamente:
1. Detecta mudanças
2. Reconstrói a aplicação
3. Faz redeploy

---

## 🗄️ Banco de Dados (Opcional - PostgreSQL)

Se quiser migrar do SQLite para PostgreSQL:

### 1. Criar Banco no Render

1. No dashboard: **"New +" → "PostgreSQL"**
2. Nome: `torneio-xadrez-db`
3. Plan: **Free** (90 dias gratuito, depois expira)
4. Clique em **"Create Database"**

### 2. Copiar URL do Banco

Vá em **Info** e copie a **Internal Database URL**:

```
postgresql://user:password@host/database
```

### 3. Adicionar ao Web Service

No seu Web Service:
1. Vá em **Environment**
2. Adicione variável:
   ```
   DATABASE_URL=postgresql://user:password@host/database
   ```

### 4. Atualizar Código (se necessário)

O SQLite já funciona em produção, mas se quiser PostgreSQL:

```python
import os

# Use DATABASE_URL do ambiente ou SQLite como fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./torneio_xadrez.db")
```

---

## 📊 Monitoramento

### Ver Logs

No Render Dashboard:
1. Clique no seu serviço
2. Vá em **"Logs"** tab
3. Veja logs em tempo real

### Métricas

- **CPU Usage**
- **Memory Usage**
- **Request Latency**
- **HTTP Status Codes**

---

## ⚠️ Limitações do Plano Gratuito

- **Sleep Mode**: App "dorme" após 15 min de inatividade
  - Primeira requisição após dormir: ~30-60s (cold start)
- **750 horas/mês**: Suficiente para uso moderado
- **512MB RAM**: Adequado para apps pequenos
- **Banco PostgreSQL**: Expira após 90 dias

**Solução para Cold Starts**:
- Use serviço de ping (ex: UptimeRobot) para manter ativo
- Ou upgrade para plano pago ($7/mês)

---

## 🔧 Troubleshooting

### Problema: App não inicia

**Solução**: Verifique logs
```
Error: No module named 'fastapi'
```
→ Adicione `fastapi` ao `requirements.txt`

### Problema: Erro de porta

**Solução**: Use `0.0.0.0:10000` (não `localhost`)

### Problema: Banco de dados não encontrado

**Solução**: 
- SQLite funciona normalmente
- Certifique-se que `torneio_xadrez.db` está sendo criado
- Verifique permissões de escrita

### Problema: Fotos não aparecem

**Solução**: 
- O diretório `static/uploads/` é efêmero no Render
- Para produção, use serviço de storage (ex: AWS S3, Cloudinary)
- Ou adicione persistência de disco (plano pago)

---

## 🚀 Deploy Contínuo

Configurado automaticamente! Sempre que você fizer:

```bash
git add .
git commit -m "Nova feature"
git push origin main
```

O Render automaticamente:
1. ✅ Detecta mudanças
2. 📦 Reconstrói app
3. 🚀 Faz redeploy
4. 🎉 App atualizado!

---

## 📱 Domínio Personalizado (Opcional)

Para usar seu próprio domínio (ex: `torneio.suaescola.com.br`):

1. No Render Dashboard → Seu serviço → **Settings**
2. Em **Custom Domain**, clique **"Add Custom Domain"**
3. Digite: `torneio.suaescola.com.br`
4. Render fornece registros DNS para configurar
5. No seu provedor de domínio (Registro.br, GoDaddy), adicione:
   ```
   CNAME torneio → seu-app.onrender.com
   ```

---

## ✅ Checklist Final

- [ ] Código no GitHub
- [ ] `requirements.txt` completo
- [ ] `render.yaml` configurado
- [ ] Web Service criado no Render
- [ ] Deploy bem-sucedido
- [ ] App acessível via URL
- [ ] Login admin funcionando
- [ ] Cadastro de competidores OK
- [ ] Sistema de sorteio OK
- [ ] Avanço de partidas OK

---

## 🆘 Suporte

- **Documentação Render**: https://render.com/docs/deploy-fastapi
- **Comunidade Render**: https://community.render.com
- **GitHub Issues**: Reporte problemas no repositório

---

## 🎓 Recursos Úteis

- [Render FastAPI Docs](https://render.com/docs/deploy-fastapi)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

**Sucesso no deploy! 🎉**
