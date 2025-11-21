from supabase import create_client, Client
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class Database:
    def __init__(self):
        """Inicializa conexão com Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    def salvar_proposta(
        self, 
        numero_proposta: str,
        cliente: Dict[str, str],
        dados_sistema: Dict[str, Any],
        dados_payback: List[Dict[str, Any]]
    ) -> str:
        """
        Salva proposta no banco e retorna o ID
        
        Args:
            numero_proposta: Número da proposta (ex: 211124/2024)
            cliente: Dicionário com dados do cliente
            dados_sistema: Dados extraídos do sistema fotovoltaico
            dados_payback: Lista com dados de payback por ano
            
        Returns:
            str: ID da proposta (UUID)
        """
        try:
            response = self.client.table('propostas').insert({
                "numero_proposta": numero_proposta,
                "cliente_nome": cliente['nome'],
                "cliente_cpf_cnpj": cliente['cpf_cnpj'],
                "cliente_endereco": cliente['endereco'],
                "cliente_cidade": cliente['cidade'],
                "cliente_telefone": cliente['telefone'],
                "dados_sistema": json.dumps(dados_sistema),
                "dados_payback": json.dumps(dados_payback),
                "investimento": float(dados_sistema.get('investimento', 0))
            }).execute()
            
            return response.data[0]['id']
        
        except Exception as e:
            raise Exception(f"Erro ao salvar proposta: {str(e)}")
    
    def buscar_proposta(self, proposta_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca proposta pelo ID
        
        Args:
            proposta_id: UUID da proposta
            
        Returns:
            Dict com dados da proposta ou None se não encontrada
        """
        try:
            response = self.client.table('propostas')\
                .select("*")\
                .eq('id', proposta_id)\
                .execute()
            
            if response.data:
                proposta = response.data[0]
                # Converter JSON strings de volta para dicts
                proposta['dados_sistema'] = json.loads(proposta['dados_sistema'])
                proposta['dados_payback'] = json.loads(proposta['dados_payback'])
                return proposta
            
            return None
        
        except Exception as e:
            raise Exception(f"Erro ao buscar proposta: {str(e)}")
    
    def registrar_visualizacao(
        self, 
        proposta_id: str, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Registra uma visualização da proposta
        
        Args:
            proposta_id: UUID da proposta
            ip_address: IP do visitante
            user_agent: User agent do navegador
        """
        try:
            self.client.table('visualizacoes').insert({
                "proposta_id": proposta_id,
                "ip_address": ip_address,
                "user_agent": user_agent
            }).execute()
        
        except Exception as e:
            # Não falhar se não conseguir registrar visualização
            print(f"Aviso: Não foi possível registrar visualização: {str(e)}")
    
    def listar_visualizacoes(self, proposta_id: str) -> List[Dict[str, Any]]:
        """
        Lista todas as visualizações de uma proposta
        
        Args:
            proposta_id: UUID da proposta
            
        Returns:
            Lista de visualizações ordenadas por data (mais recente primeiro)
        """
        try:
            response = self.client.table('visualizacoes')\
                .select("*")\
                .eq('proposta_id', proposta_id)\
                .order('visualizado_em', desc=True)\
                .execute()
            
            return response.data
        
        except Exception as e:
            raise Exception(f"Erro ao listar visualizações: {str(e)}")
    
    def contar_visualizacoes(self, proposta_id: str) -> int:
        """
        Conta total de visualizações de uma proposta
        
        Args:
            proposta_id: UUID da proposta
            
        Returns:
            int: Total de visualizações
        """
        try:
            response = self.client.table('visualizacoes')\
                .select("id", count="exact")\
                .eq('proposta_id', proposta_id)\
                .execute()
            
            return response.count if response.count else 0
        
        except Exception as e:
            return 0
