# 📁 ÍNDICE DE ARQUIVOS DO PROJETO

Guia completo de todos os arquivos e suas funções.

---

## 📋 ARQUIVOS PRINCIPAIS

### `main.py` ⭐
**O que faz:** Arquivo principal da aplicação FastAPI  
**Quando usar:** Executar para iniciar o servidor  
**Comando:** `python main.py`

### `requirements.txt`
**O que faz:** Lista todas as dependências Python  
**Quando usar:** Instalação inicial do projeto  
**Comando:** `pip install -r requirements.txt`

### `.env.example`
**O que faz:** Template das variáveis de ambiente  
**Quando usar:** Configuração inicial  
**Ação:** Copiar para `.env` e preencher com suas credenciais

---

## 📚 DOCUMENTAÇÃO

### `README.md` 📖
**O que faz:** Documentação completa do projeto  
**Conteúdo:** Instalação, uso da API, integração N8N, deploy  
**Para quem:** Desenvolvedores e novos usuários

### `GUIA_RAPIDO.md` 🚀
**O que faz:** Tutorial rápido de 5 minutos  
**Conteúdo:** Setup mínimo para começar  
**Para quem:** Quem quer começar RÁPIDO

### `CHECKLIST_DEPLOY.md` ✅
**O que faz:** Lista de verificação para produção  
**Conteúdo:** Todos os passos antes de ir ao ar  
**Para quem:** Responsável pelo deploy

### `TROUBLESHOOTING.md` 🔧
**O que faz:** Solução de problemas comuns  
**Conteúdo:** Erros frequentes e como resolver  
**Para quem:** Quando algo dá errado

---

## 🗄️ BANCO DE DADOS

### `database_schema.sql`
**O que faz:** Cria estrutura do banco no Supabase  
**Conteúdo:** Tabelas, índices, views, políticas de segurança  
**Como usar:** Colar no SQL Editor do Supabase e executar

---

## 🧪 ARQUIVOS DE TESTE

### `test_api.py` 🐍
**O que faz:** Script Python para testar a API  
**Testa:** Health, criar proposta, estatísticas  
**Comando:** `python test_api.py`

### `test_curl.sh` 🔄
**O que faz:** Script Bash com exemplos de curl  
**Testa:** Todos os endpoints da API  
**Comando:** `./test_curl.sh`

### `example_request.json`
**O que faz:** Exemplo de JSON para criar proposta  
**Como usar:** Copiar/adaptar para seus dados

---

## 🏗️ CÓDIGO DA APLICAÇÃO

### `/app` (Pasta principal)

#### `/app/__init__.py`
**O que faz:** Torna `app` um pacote Python  
**Conteúdo:** Vazio (só precisa existir)

---

### `/app/models` (Modelos de dados)

#### `/app/models/__init__.py`
**O que faz:** Torna `models` um pacote Python

#### `/app/models/schemas.py` 📊
**O que faz:** Define estruturas de dados (Pydantic)  
**Conteúdo:**
- `ClienteInput` - Dados do cliente
- `PropostaInput` - Request completo
- `PropostaResponse` - Resposta da API
- `EstatisticasResponse` - Stats de visualizações

---

### `/app/db` (Banco de dados)

#### `/app/db/__init__.py`
**O que faz:** Torna `db` um pacote Python

#### `/app/db/database.py` 🗄️
**O que faz:** Gerencia conexão com Supabase  
**Funções principais:**
- `salvar_proposta()` - Salva nova proposta
- `buscar_proposta()` - Busca por ID
- `registrar_visualizacao()` - Tracking
- `listar_visualizacoes()` - Histórico

---

### `/app/web` (Interface web)

#### `/app/web/__init__.py`
**O que faz:** Torna `web` um pacote Python

#### `/app/web/html_generator.py` 🎨
**O que faz:** Gera HTML das propostas  
**Funções principais:**
- `extrair_dados()` - Processa dados da planilha
- `calcular_payback()` - Calcula retorno
- `gerar_proposta_html()` - Renderiza template

#### `/app/web/templates/proposta_template.html` 📄
**O que faz:** Template visual da proposta  
**Conteúdo:**
- Design responsivo
- Dados do cliente
- Informações do sistema
- Tabelas de payback
- CSS inline completo
- JavaScript de tracking

---

## 🐳 DOCKER (Opcional)

### `Dockerfile`
**O que faz:** Define imagem Docker da aplicação  
**Como usar:** `docker build -t proposta-web .`

### `docker-compose.yml`
**O que faz:** Orquestra containers  
**Como usar:** `docker-compose up -d`

---

## 🔗 INTEGRAÇÃO

### `n8n_workflow_exemplo.json`
**O que faz:** Workflow completo para importar no N8N  
**Conteúdo:**
- Webhook para receber dados
- Criar proposta
- Enviar WhatsApp
- Verificar visualizações
- Notificações automáticas

**Como usar:**
1. Abrir N8N
2. Workflows > Import from File
3. Selecionar este arquivo
4. Ajustar URLs e credenciais

---

## 🗂️ ESTRUTURA COMPLETA

```
proposta-web/
│
├── 📄 main.py                          # Aplicação principal
├── 📋 requirements.txt                 # Dependências
├── 🔐 .env.example                     # Template config
├── 🚫 .gitignore                       # Arquivos ignorados
│
├── 📚 DOCUMENTAÇÃO
│   ├── README.md                       # Doc completa
│   ├── GUIA_RAPIDO.md                  # Tutorial 5min
│   ├── CHECKLIST_DEPLOY.md             # Deploy checklist
│   ├── TROUBLESHOOTING.md              # Solução problemas
│   └── INDEX.md                        # Este arquivo
│
├── 🗄️ BANCO DE DADOS
│   └── database_schema.sql             # Schema SQL
│
├── 🧪 TESTES
│   ├── test_api.py                     # Testes Python
│   ├── test_curl.sh                    # Testes Bash
│   └── example_request.json            # Dados exemplo
│
├── 🐳 DOCKER
│   ├── Dockerfile                      # Imagem Docker
│   └── docker-compose.yml              # Orquestração
│
├── 🔗 INTEGRAÇÃO
│   └── n8n_workflow_exemplo.json       # Workflow N8N
│
└── 📁 app/                             # Código fonte
    ├── __init__.py
    │
    ├── models/                         # Modelos dados
    │   ├── __init__.py
    │   └── schemas.py                  # Pydantic models
    │
    ├── db/                             # Database
    │   ├── __init__.py
    │   └── database.py                 # Supabase client
    │
    └── web/                            # Interface web
        ├── __init__.py
        ├── html_generator.py           # Gerador HTML
        └── templates/
            └── proposta_template.html  # Template visual
```

---

## 🎯 FLUXO DE TRABALHO TÍPICO

### 1️⃣ Setup Inicial (primeira vez)
```bash
cp .env.example .env          # Copiar config
nano .env                     # Preencher credenciais
pip install -r requirements.txt  # Instalar deps
```

No Supabase: executar `database_schema.sql`

### 2️⃣ Desenvolvimento
```bash
python main.py               # Iniciar servidor
python test_api.py           # Testar localmente
```

### 3️⃣ Deploy
```bash
# Ver CHECKLIST_DEPLOY.md
git push                     # Enviar para GitHub
# Configurar na VPS usando Dockerfile ou PM2
```

### 4️⃣ Integração N8N
- Importar `n8n_workflow_exemplo.json`
- Ajustar URLs
- Testar workflow

### 5️⃣ Monitoramento
```bash
curl http://seu-servidor:8182/health
curl http://seu-servidor:8182/api/proposta/ID/stats
```

---

## 🆘 QUAL ARQUIVO LER PRIMEIRO?

### Se você é:

**👨‍💻 Desenvolvedor novo no projeto:**
1. `README.md` - Entender o projeto
2. `GUIA_RAPIDO.md` - Setup inicial
3. `main.py` - Ver código principal
4. `app/models/schemas.py` - Entender dados

**🚀 Responsável pelo deploy:**
1. `GUIA_RAPIDO.md` - Setup rápido
2. `CHECKLIST_DEPLOY.md` - Todos os passos
3. `database_schema.sql` - Configurar banco
4. `Dockerfile` ou `docker-compose.yml` - Deploy

**🔗 Integrando com N8N:**
1. `README.md` (seção "Integração com N8N")
2. `n8n_workflow_exemplo.json` - Importar
3. `example_request.json` - Ver formato dados

**🐛 Resolvendo problemas:**
1. `TROUBLESHOOTING.md` - Soluções
2. `test_api.py` - Testar componentes
3. Logs da aplicação

---

## 📞 AJUDA

Leu tudo e ainda tem dúvidas?

- 📧 contato@levesol.com.br
- 📞 (14) 99893-7738
- 🌐 www.levesol.com.br

---

**Última atualização:** 21/11/2024  
**Versão:** 1.0.0
