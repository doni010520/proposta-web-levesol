#!/usr/bin/env python3
"""
Script de teste rápido da API
Execute com: python test_api.py
"""

import requests
import json
from datetime import datetime

# Configurações
API_URL = "http://localhost:8182"

def test_health():
    """Testa o endpoint de health"""
    print("\n🔍 Testando health check...")
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        print("✅ API está rodando!")
        print(f"   Resposta: {response.json()}")
    else:
        print(f"❌ Erro: {response.status_code}")

def test_criar_proposta():
    """Testa criação de proposta"""
    print("\n🔍 Testando criação de proposta...")
    
    # Carregar dados de exemplo
    with open('example_request.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    response = requests.post(f"{API_URL}/api/proposta", json=dados)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Proposta criada com sucesso!")
        print(f"   Número: {result['numero_proposta']}")
        print(f"   ID: {result['proposta_id']}")
        print(f"   URL: {result['proposta_url']}")
        return result['proposta_id']
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"   Detalhes: {response.text}")
        return None

def test_estatisticas(proposta_id):
    """Testa endpoint de estatísticas"""
    print(f"\n🔍 Testando estatísticas da proposta {proposta_id}...")
    
    response = requests.get(f"{API_URL}/api/proposta/{proposta_id}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Estatísticas recuperadas!")
        print(f"   Total de visualizações: {stats['total_visualizacoes']}")
        print(f"   Primeira visualização: {stats['primeira_visualizacao']}")
        print(f"   Última visualização: {stats['ultima_visualizacao']}")
    else:
        print(f"❌ Erro: {response.status_code}")

def main():
    print("=" * 60)
    print("🧪 TESTE DA API - Sistema de Propostas Web")
    print("=" * 60)
    
    # Teste 1: Health check
    test_health()
    
    # Teste 2: Criar proposta
    proposta_id = test_criar_proposta()
    
    # Teste 3: Estatísticas
    if proposta_id:
        test_estatisticas(proposta_id)
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        print(f"🌐 Acesse a proposta em: {API_URL}/proposta/{proposta_id}")
        print("=" * 60)
    else:
        print("\n❌ Alguns testes falharam. Verifique se:")
        print("   1. A API está rodando (python main.py)")
        print("   2. O banco de dados está configurado")
        print("   3. O arquivo .env está correto")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API!")
        print(f"   Certifique-se de que a API está rodando em {API_URL}")
        print("   Execute: python main.py")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
