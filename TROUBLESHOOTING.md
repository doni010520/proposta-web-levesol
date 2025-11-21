# 🔧 GUIA DE TROUBLESHOOTING

Soluções para problemas comuns ao rodar o Sistema de Propostas Web.

---

## 🚨 PROBLEMAS DE CONEXÃO

### Erro: "Connection refused" ou "Failed to connect"

**Sintoma:** API não responde

**Causas possíveis:**
1. API não está rodando
2. Porta bloqueada
3. Firewall bloqueando

**Soluções:**

```bash
# Verificar se API está rodando
ps aux | grep main.py

# Se não estiver, iniciar
python main.py

# Verificar se porta está sendo usada
sudo netstat -tulpn | grep 8182

# Se porta está ocupada, matar processo
sudo kill -9 $(sudo lsof -t -i:8182)

# Testar localmente
curl http://localhost:8182/health

# Abrir porta no firewall (Ubuntu/Debian)
sudo ufw allow 8182
sudo ufw reload

# Abrir porta no firewall (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8182/tcp
sudo firewall-cmd --reload
```

---

## 🗄️ PROBLEMAS COM BANCO DE DADOS

### Erro: "SUPABASE_URL not found" ou "SUPABASE_KEY not found"

**Sintoma:** Erro ao iniciar aplicação

**Solução:**

```bash
# Verificar se .env existe
ls -la .env

# Se não existe, criar
cp .env.example .env

# Editar e adicionar credenciais
nano .env

# Verificar se variáveis estão carregando
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('SUPABASE_URL'))"
```

### Erro: "Table 'propostas' does not exist"

**Sintoma:** Erro ao criar proposta

**Solução:**

1. Acesse Supabase (https://supabase.com)
2. Vá em SQL Editor
3. Cole e execute o conteúdo de `database_schema.sql`
4. Verifique se tabelas foram criadas:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('propostas', 'visualizacoes');
```

### Erro: "Invalid API key" ou "Unauthorized"

**Sintoma:** Erro 401 ao acessar banco

**Solução:**

1. No Supabase, vá em Settings > API
2. Copie a chave **anon/public**
3. Cole no arquivo `.env` na variável `SUPABASE_KEY`
4. Reinicie a aplicação

---

## 📦 PROBLEMAS COM DEPENDÊNCIAS

### Erro: "No module named 'fastapi'" ou similar

**Sintoma:** Import errors ao rodar

**Solução:**

```bash
# Reinstalar todas as dependências
pip install -r requirements.txt --force-reinstall

# Se ainda não funcionar, usar venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Erro: "ModuleNotFoundError: No module named 'app'"

**Sintoma:** Erro ao importar módulos locais

**Solução:**

```bash
# Verificar estrutura de pastas
ls -R

# Garantir que todos __init__.py existem
find . -name "__init__.py"

# Se faltarem, criar
touch app/__init__.py
touch app/models/__init__.py
touch app/web/__init__.py
touch app/db/__init__.py

# Rodar do diretório raiz do projeto
cd /caminho/para/proposta-web
python main.py
```

---

## 🌐 PROBLEMAS COM HTML/TEMPLATES

### Erro: "Template not found: proposta_template.html"

**Sintoma:** Erro 500 ao visualizar proposta

**Solução:**

```bash
# Verificar se template existe
ls -la app/web/templates/proposta_template.html

# Se não existe, criar o arquivo
# (copie do repositório ou dos arquivos fornecidos)

# Verificar permissões
chmod 644 app/web/templates/proposta_template.html
```

### Proposta HTML aparece sem estilo

**Sintoma:** Página carrega mas sem formatação

**Causas:**
- CSS inline quebrado no template
- Erro no HTML

**Solução:**

1. Verificar console do navegador (F12) por erros
2. Revalidar arquivo HTML
3. Se necessário, baixar template novamente

---

## 🔐 PROBLEMAS COM CORS

### Erro: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Sintoma:** N8N ou frontend não consegue acessar API

**Solução:**

Editar `main.py` e adicionar domínios permitidos:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-n8n.com",
        "https://seu-dominio.com",
        "*"  # Apenas para desenvolvimento!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 PROBLEMAS COM TRACKING

### Visualizações não estão sendo registradas

**Sintoma:** Stats sempre mostra 0 visualizações

**Debug:**

```bash
# Verificar logs da aplicação
tail -f logs/app.log

# Testar endpoint de visualização manualmente
curl -H "User-Agent: Test" http://localhost:8182/proposta/SEU-ID-AQUI

# Verificar no Supabase se há registros
# Table Editor > visualizacoes
```

**Soluções:**

1. Verificar se RLS (Row Level Security) está permitindo inserts:

```sql
-- No Supabase SQL Editor
ALTER TABLE visualizacoes DISABLE ROW LEVEL SECURITY;
-- OU configurar política adequada
```

2. Verificar permissões da service key

---

## 🐳 PROBLEMAS COM DOCKER

### Erro: "docker: command not found"

**Solução:**

```bash
# Instalar Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Logout e login novamente
```

### Container não inicia

**Debug:**

```bash
# Ver logs do container
docker logs proposta-web-api

# Ver status
docker ps -a

# Remover e recriar
docker-compose down
docker-compose up --build
```

---

## 🔄 PROBLEMAS NO N8N

### N8N não consegue acessar a API

**Verificar:**

1. API está acessível externamente?
```bash
curl http://SEU-IP:8182/health
```

2. Firewall permite conexões externas na porta 8182?

3. N8N tem permissão para fazer requests HTTP externos?

4. URL no N8N está correta? (http:// ou https://)

### Proposta cria mas link não funciona

**Problema:** BASE_URL incorreta

**Solução:**

Editar `.env`:
```env
BASE_URL=https://seu-dominio-real.com
```

Reiniciar aplicação.

---

## 📝 LOGS E DEBUG

### Como ver logs detalhados

```bash
# Logs do systemd (se usar service)
journalctl -u proposta-web -f

# Logs do PM2 (se usar PM2)
pm2 logs proposta-web

# Logs do Docker
docker logs -f proposta-web-api

# Logs manuais (se criar arquivo de log)
tail -f logs/app.log
```

### Modo debug

Editar `main.py` e mudar:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        log_level="debug",  # Adicionar esta linha
        reload=True  # Auto-reload em desenvolvimento
    )
```

---

## 🆘 AINDA COM PROBLEMAS?

### Checklist final:

- [ ] Python 3.8+ instalado? `python --version`
- [ ] Todas dependências instaladas? `pip list`
- [ ] Arquivo .env existe e está preenchido? `cat .env`
- [ ] Banco de dados configurado? (verificar no Supabase)
- [ ] Porta 8182 acessível? `curl localhost:8182/health`
- [ ] Firewall permite conexões? `sudo ufw status`

### Comandos de diagnóstico completo:

```bash
# 1. Verificar Python
python --version

# 2. Verificar pip
pip --version

# 3. Verificar dependências
pip list | grep -E "fastapi|supabase|jinja2|uvicorn"

# 4. Verificar estrutura de arquivos
ls -R | grep -E ".py|.html|.env"

# 5. Testar conexão Supabase
python -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print('Conexão OK!')"

# 6. Testar porta
sudo netstat -tulpn | grep 8182

# 7. Testar API
curl -v http://localhost:8182/health
```

### Coletar informações para suporte:

```bash
# Criar arquivo de diagnóstico
cat > diagnostico.txt << EOF
Python: $(python --version)
Pip: $(pip --version)
Sistema: $(uname -a)
API rodando: $(ps aux | grep main.py)
Porta 8182: $(sudo netstat -tulpn | grep 8182)
EOF

cat diagnostico.txt
```

---

## 📞 SUPORTE

Se nenhuma solução funcionou:

1. 📧 Email: contato@levesol.com.br
2. 📞 Telefone: (14) 99893-7738
3. Enviar arquivo `diagnostico.txt` criado acima

**Informações úteis para incluir:**
- Sistema operacional
- Versão do Python
- Mensagem de erro completa
- Logs da aplicação
- Arquivo .env (SEM as credenciais!)
