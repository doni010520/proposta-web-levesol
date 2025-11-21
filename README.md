# 🌞 Sistema de Propostas Web - LEVESOL

Sistema completo para geração e tracking de propostas de energia solar via web, substituindo PDFs por páginas HTML interativas com rastreamento de visualizações.

## 📋 Funcionalidades

- ✅ **Geração de propostas web** - Cria páginas HTML profissionais ao invés de PDFs
- ✅ **Tracking automático** - Registra todas as visualizações (IP, user agent, timestamp)
- ✅ **API REST completa** - Integração fácil com N8N e outros sistemas
- ✅ **Dashboard de estatísticas** - Veja quantas vezes cada proposta foi aberta
- ✅ **Design responsivo** - Funciona perfeitamente em mobile e desktop
- ✅ **Botão de impressão** - Cliente pode imprimir se desejar

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- Conta no Supabase (grátis)
- VPS ou servidor com acesso à internet

### Passo 1: Clone o repositório

```bash
git clone https://github.com/seu-usuario/proposta-web.git
cd proposta-web
```

### Passo 2: Configure o banco de dados

Acesse seu [Supabase](https://supabase.com) e execute o SQL abaixo:

```sql
-- Criar tabela de propostas
CREATE TABLE propostas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_proposta VARCHAR(50) UNIQUE NOT NULL,
    cliente_nome VARCHAR(255) NOT NULL,
    cliente_cpf_cnpj VARCHAR(20),
    cliente_endereco TEXT,
    cliente_cidade VARCHAR(100),
    cliente_telefone VARCHAR(20),
    dados_sistema JSONB NOT NULL,
    dados_payback JSONB NOT NULL,
    investimento DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Criar tabela de visualizações
CREATE TABLE visualizacoes (
    id SERIAL PRIMARY KEY,
    proposta_id UUID REFERENCES propostas(id) ON DELETE CASCADE,
    visualizado_em TIMESTAMP DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Criar índices para performance
CREATE INDEX idx_propostas_numero ON propostas(numero_proposta);
CREATE INDEX idx_visualizacoes_proposta ON visualizacoes(proposta_id);
CREATE INDEX idx_visualizacoes_data ON visualizacoes(visualizado_em DESC);
```

### Passo 3: Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
# Supabase (pegue no painel do Supabase)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_aqui

# Configurações da API
APP_PORT=8182
APP_HOST=0.0.0.0

# URL base (mude para seu domínio)
BASE_URL=https://propostas.levesol.com.br
```

### Passo 4: Instale as dependências

```bash
pip install -r requirements.txt
```

### Passo 5: Execute a aplicação

```bash
python main.py
```

A API estará rodando em `http://localhost:8182`

## 📡 Uso da API

### 1. Criar uma proposta

**Endpoint:** `POST /api/proposta`

**Request:**
```json
{
  "cliente": {
    "nome": "João da Silva",
    "cpf_cnpj": "123.456.789-00",
    "endereco": "Rua Exemplo, 123",
    "cidade": "Bauru - SP",
    "telefone": "(14) 99999-9999"
  },
  "dados_completos": [
    {
      "Gráfico Payback": "1",
      "col_2": "-50000.00",
      "col_3": "800.00"
    },
    {
      "DADOS DA CONTA DE ENERGIA": "Preço do Sistema",
      "col_7": "50000.00"
    }
    // ... mais dados
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "numero_proposta": "211124/2024",
  "proposta_id": "abc-123-def-456",
  "proposta_url": "https://propostas.levesol.com.br/proposta/abc-123-def-456",
  "message": "Proposta criada com sucesso! Envie o link ao cliente."
}
```

### 2. Visualizar proposta

**Endpoint:** `GET /proposta/{proposta_id}`

Abre a página HTML da proposta. **Registra automaticamente a visualização!**

### 3. Ver estatísticas

**Endpoint:** `GET /api/proposta/{proposta_id}/stats`

**Response:**
```json
{
  "proposta_id": "abc-123-def-456",
  "total_visualizacoes": 5,
  "primeira_visualizacao": "2024-11-21T10:30:00Z",
  "ultima_visualizacao": "2024-11-21T15:45:00Z",
  "historico": [
    {
      "id": 1,
      "proposta_id": "abc-123-def-456",
      "visualizado_em": "2024-11-21T15:45:00Z",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

## 🔗 Integração com N8N

### Fluxo sugerido:

1. **Webhook** recebe dados do cliente
2. **HTTP Request** para `POST /api/proposta`
3. **Extrair** `proposta_url` da resposta
4. **Enviar** link via WhatsApp/Email

**Exemplo de nó HTTP Request no N8N:**

```json
{
  "method": "POST",
  "url": "https://seu-servidor.com:8182/api/proposta",
  "body": {
    "cliente": {
      "nome": "{{ $json.nome }}",
      "cpf_cnpj": "{{ $json.cpf }}",
      "endereco": "{{ $json.endereco }}",
      "cidade": "{{ $json.cidade }}",
      "telefone": "{{ $json.telefone }}"
    },
    "dados_completos": "{{ $json.dados_completos }}"
  }
}
```

Depois, use `{{ $json.proposta_url }}` para enviar ao cliente!

## 🐳 Deploy com Docker (Opcional)

Crie um `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Execute:

```bash
docker build -t proposta-web .
docker run -p 8182:8182 --env-file .env proposta-web
```

## 📊 Monitoramento

Acesse os logs para ver as visualizações em tempo real:

```bash
tail -f logs/app.log
```

Ou use o endpoint de health check:

```bash
curl http://localhost:8182/health
```

## 🔒 Segurança

- ✅ Todas as senhas e chaves ficam no `.env` (nunca commite!)
- ✅ CORS configurado para aceitar apenas domínios autorizados
- ✅ Rate limiting pode ser adicionado com `slowapi`
- ✅ Banco de dados com conexão segura (Supabase)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é proprietário da LEVESOL LTDA.

## 🆘 Suporte

- 📧 Email: contato@levesol.com.br
- 📞 Telefone: (14) 99893-7738
- 🌐 Site: www.levesol.com.br

---

**Desenvolvido com ⚡ para transformar propostas de energia solar**
