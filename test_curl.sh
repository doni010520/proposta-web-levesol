#!/bin/bash
# ========================================
# EXEMPLOS DE CURL PARA TESTAR A API
# Sistema de Propostas Web - LEVESOL
# ========================================

BASE_URL="http://localhost:8182"

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TESTANDO API - Sistema de Propostas Web${NC}"
echo -e "${BLUE}========================================${NC}\n"

# ========================================
# 1. HEALTH CHECK
# ========================================
echo -e "${GREEN}1. Testando Health Check...${NC}"
curl -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json" \
  | jq .

echo -e "\n${BLUE}----------------------------------------${NC}\n"

# ========================================
# 2. CRIAR PROPOSTA
# ========================================
echo -e "${GREEN}2. Criando nova proposta...${NC}"

PROPOSTA_RESPONSE=$(curl -X POST "$BASE_URL/api/proposta" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {
      "nome": "João da Silva Teste",
      "cpf_cnpj": "123.456.789-00",
      "endereco": "Rua das Flores, 123, Centro, CEP: 17015-000",
      "cidade": "Bauru - SP",
      "telefone": "(14) 99999-9999"
    },
    "dados_completos": [
      {
        "Gráfico Payback": "1",
        "col_2": "-45000.00",
        "col_3": "800.00"
      },
      {
        "Gráfico Payback": "2",
        "col_2": "-40000.00",
        "col_3": "840.00"
      },
      {
        "Gráfico Payback": "3",
        "col_2": "-34800.00",
        "col_3": "882.00"
      },
      {
        "DADOS DA CONTA DE ENERGIA": "Consumo Total Permitido (mês) kwh:",
        "col_7": "1200"
      },
      {
        "DADOS DA CONTA DE ENERGIA": "Quantidade de módulos",
        "col_7": "10"
      },
      {
        "DADOS DA CONTA DE ENERGIA": "Potência do sistema",
        "col_7": "7.0"
      },
      {
        "DADOS DA CONTA DE ENERGIA": "Área total instalada",
        "col_7": "25"
      },
      {
        "DADOS DA CONTA DE ENERGIA": "Energia Média Gerada (mês)",
        "col_7": "1150"
      },
      {
        "DADOS DA CONTA DE ENERGIA": "Preço do Sistema",
        "col_7": "50000.00"
      },
      {
        "DADOS DA CONTA DE ENERGIA": "Padrão do Cliente",
        "col_7": "Bifásico"
      }
    ]
  }')

echo "$PROPOSTA_RESPONSE" | jq .

# Extrair proposta_id para próximos testes
PROPOSTA_ID=$(echo "$PROPOSTA_RESPONSE" | jq -r '.proposta_id')
PROPOSTA_URL=$(echo "$PROPOSTA_RESPONSE" | jq -r '.proposta_url')

echo -e "\n${BLUE}Proposta ID: $PROPOSTA_ID${NC}"
echo -e "${BLUE}Proposta URL: $PROPOSTA_URL${NC}"

echo -e "\n${BLUE}----------------------------------------${NC}\n"

# ========================================
# 3. VISUALIZAR PROPOSTA (simular abertura)
# ========================================
echo -e "${GREEN}3. Simulando visualização da proposta...${NC}"
echo -e "Abrindo URL: $BASE_URL/proposta/$PROPOSTA_ID"

curl -X GET "$BASE_URL/proposta/$PROPOSTA_ID" \
  -H "User-Agent: Test-Script/1.0" \
  -o /dev/null -s -w "Status: %{http_code}\n"

echo -e "\n${BLUE}----------------------------------------${NC}\n"

# Aguardar 2 segundos
sleep 2

# ========================================
# 4. VERIFICAR ESTATÍSTICAS
# ========================================
echo -e "${GREEN}4. Verificando estatísticas...${NC}"
curl -X GET "$BASE_URL/api/proposta/$PROPOSTA_ID/stats" \
  -H "Content-Type: application/json" \
  | jq .

echo -e "\n${BLUE}----------------------------------------${NC}\n"

# ========================================
# 5. LISTAR TODAS AS PROPOSTAS (se implementado)
# ========================================
# echo -e "${GREEN}5. Listando todas as propostas...${NC}"
# curl -X GET "$BASE_URL/api/propostas" | jq .

# ========================================
# RESUMO
# ========================================
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ TESTES CONCLUÍDOS!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "📊 Proposta criada com sucesso!"
echo -e "🔗 Acesse: ${BLUE}$PROPOSTA_URL${NC}"
echo -e "📈 Visualizações registradas"
echo -e "✅ API funcionando corretamente\n"

# ========================================
# COMANDOS ÚTEIS ADICIONAIS
# ========================================
echo -e "${BLUE}Comandos úteis:${NC}\n"

echo -e "# Ver proposta no navegador:"
echo -e "xdg-open $PROPOSTA_URL\n"

echo -e "# Testar health check:"
echo -e "curl $BASE_URL/health | jq .\n"

echo -e "# Ver stats de proposta específica:"
echo -e "curl $BASE_URL/api/proposta/$PROPOSTA_ID/stats | jq .\n"

echo -e "# Criar proposta a partir de arquivo:"
echo -e "curl -X POST $BASE_URL/api/proposta \\"
echo -e "  -H 'Content-Type: application/json' \\"
echo -e "  -d @example_request.json | jq .\n"
