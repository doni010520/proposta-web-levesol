# ✅ CHECKLIST DE DEPLOY - PRODUÇÃO

Use este checklist antes de colocar em produção na VPS.

## 🔒 SEGURANÇA

- [ ] Arquivo `.env` está fora do repositório Git (no .gitignore)
- [ ] Variável `BASE_URL` aponta para domínio real (não localhost)
- [ ] Credenciais do Supabase estão corretas
- [ ] CORS está configurado corretamente (permitir apenas domínios necessários)
- [ ] Banco de dados tem backup configurado
- [ ] RLS (Row Level Security) está ativo no Supabase

## 🗄️ BANCO DE DADOS

- [ ] SQL do `database_schema.sql` foi executado no Supabase
- [ ] Tabelas `propostas` e `visualizacoes` existem
- [ ] Índices foram criados
- [ ] View `vw_propostas_stats` está funcionando
- [ ] Testei INSERT e SELECT nas tabelas
- [ ] Políticas de segurança estão ativas

## 🖥️ SERVIDOR (VPS)

- [ ] Python 3.8+ instalado
- [ ] pip está atualizado (`pip install --upgrade pip`)
- [ ] Todas as dependências instaladas (`pip install -r requirements.txt`)
- [ ] Porta 8182 está aberta no firewall
- [ ] Domínio/subdomínio aponta para VPS
- [ ] Certificado SSL configurado (HTTPS)

## 📁 ARQUIVOS

- [ ] Todos os arquivos foram copiados para VPS
- [ ] Permissões corretas (`chmod 644` arquivos, `chmod 755` diretórios)
- [ ] Arquivo `.env` existe e está preenchido
- [ ] Pasta `app/web/templates/` existe com o HTML

## 🚀 DEPLOY

### Opção 1: Systemd (Recomendado)

Criar arquivo `/etc/systemd/system/proposta-web.service`:

```ini
[Unit]
Description=Sistema de Propostas Web - LEVESOL
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/caminho/para/proposta-web
Environment="PATH=/caminho/para/venv/bin"
ExecStart=/caminho/para/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Comandos:
```bash
sudo systemctl daemon-reload
sudo systemctl enable proposta-web
sudo systemctl start proposta-web
sudo systemctl status proposta-web
```

- [ ] Service criado
- [ ] Service habilitado no boot
- [ ] Service rodando sem erros

### Opção 2: PM2

```bash
npm install -g pm2
pm2 start main.py --name proposta-web --interpreter python3
pm2 save
pm2 startup
```

- [ ] PM2 instalado
- [ ] Aplicação rodando no PM2
- [ ] PM2 configurado para iniciar no boot

### Opção 3: Screen (Temporário)

```bash
screen -S proposta-web
python main.py
# Ctrl+A+D para desatachar
```

## 🔍 TESTES PÓS-DEPLOY

- [ ] Endpoint `/health` responde 200 OK
- [ ] Criar proposta via API funciona
- [ ] Página HTML da proposta abre
- [ ] Tracking de visualização funciona
- [ ] Endpoint `/stats` retorna dados corretos
- [ ] Teste com `curl` ou Postman passou

```bash
# Teste rápido
curl https://seu-dominio.com:8182/health
```

## 📊 MONITORAMENTO

- [ ] Logs estão sendo salvos
- [ ] Configurar alertas de erro (opcional)
- [ ] Configurar backup automático do banco
- [ ] Documentar credenciais em local seguro

## 🔄 INTEGRAÇÃO N8N

- [ ] N8N consegue acessar a API
- [ ] Workflow de teste funcionou
- [ ] Links gerados são acessíveis
- [ ] WhatsApp envia mensagens com links
- [ ] Tracking funciona quando cliente abre

## 🌐 NGINX (Se usar)

Configuração em `/etc/nginx/sites-available/proposta-web`:

```nginx
server {
    listen 80;
    server_name propostas.levesol.com.br;
    
    location / {
        proxy_pass http://localhost:8182;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
```

- [ ] NGINX instalado
- [ ] Configuração criada
- [ ] Certificado SSL instalado (Certbot)
- [ ] NGINX reiniciado

```bash
sudo ln -s /etc/nginx/sites-available/proposta-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📝 DOCUMENTAÇÃO

- [ ] README atualizado com URLs reais
- [ ] Credenciais documentadas em local seguro
- [ ] Equipe sabe como reiniciar se necessário
- [ ] Procedimento de backup documentado

## ⚠️ COMANDOS ÚTEIS

```bash
# Ver logs
journalctl -u proposta-web -f

# Reiniciar service
sudo systemctl restart proposta-web

# Ver status
sudo systemctl status proposta-web

# Parar service
sudo systemctl stop proposta-web

# Ver uso de porta
sudo netstat -tulpn | grep 8182

# Testar endpoint
curl -X POST https://seu-dominio.com/api/proposta \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

## 🎉 FINAL

Se todos os checkboxes acima estão marcados:

**✅ SISTEMA PRONTO PARA PRODUÇÃO!**

Próximos passos:
1. Monitorar logs por 24h
2. Testar com cliente real
3. Configurar backup automático
4. Criar alertas de erro

---

**Data do deploy:** _________________

**Responsável:** _________________

**Domínio:** _________________

**Observações:**
_________________________________________________
_________________________________________________
_________________________________________________
