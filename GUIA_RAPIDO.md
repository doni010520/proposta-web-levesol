# 🚀 GUIA RÁPIDO DE INÍCIO

## ⚡ Começando em 5 minutos

### 1️⃣ Configure o Supabase (2 min)

1. Acesse https://supabase.com e crie uma conta gratuita
2. Crie um novo projeto
3. Vá em SQL Editor
4. Cole e execute o conteúdo de `database_schema.sql`
5. Copie sua URL e Key do painel "Settings > API"

### 2️⃣ Configure o projeto (1 min)

```bash
# Copie o template de ambiente
cp .env.example .env

# Edite o .env e coloque suas credenciais do Supabase
nano .env
```

### 3️⃣ Instale e rode (2 min)

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute a API
python main.py
```

Pronto! API rodando em http://localhost:8182

### 4️⃣ Teste (30 segundos)

```bash
# Execute o script de teste
python test_api.py
```

---

## 📡 Como usar no N8N

### Criar proposta:

**Node: HTTP Request**
- Method: POST
- URL: `http://seu-servidor:8182/api/proposta`
- Body: JSON com dados do cliente + dados_completos

### Enviar link ao cliente:

Use a variável `{{ $json.proposta_url }}` para enviar o link via WhatsApp/Email.

### Verificar visualizações:

**Node: HTTP Request**
- Method: GET
- URL: `http://seu-servidor:8182/api/proposta/{{ $json.proposta_id }}/stats`

---

## 🎯 Exemplo de fluxo completo no N8N

```
[Webhook] 
    ↓ (dados do cliente)
[HTTP Request - Criar Proposta]
    ↓ (proposta_url)
[WhatsApp - Enviar Link]
    ↓
[Aguardar 1 hora]
    ↓
[HTTP Request - Verificar Stats]
    ↓
[IF - Visualizou?]
    ├─ SIM → [Email: "Cliente visualizou!"]
    └─ NÃO → [WhatsApp: "Lembrete"]
```

---

## 🔧 Comandos úteis

```bash
# Ver logs em tempo real
tail -f logs/app.log

# Reiniciar aplicação
pkill -f main.py && python main.py

# Testar endpoint específico
curl http://localhost:8182/health

# Ver propostas no banco (Supabase)
# Vá em Table Editor > propostas
```

---

## 🆘 Resolução de problemas

### Erro: "Connection refused"
- A API não está rodando
- Execute: `python main.py`

### Erro: "SUPABASE_URL not found"
- O arquivo .env não está configurado
- Copie .env.example para .env e preencha

### Erro: "Table propostas does not exist"
- Execute o SQL do database_schema.sql no Supabase

### Erro: "Port 8182 already in use"
- Mude a porta no .env: `APP_PORT=8183`

---

## 📞 Precisa de ajuda?

- 📧 contato@levesol.com.br
- 📞 (14) 99893-7738

**Boa sorte! ⚡**
