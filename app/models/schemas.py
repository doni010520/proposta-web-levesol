from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ClienteInput(BaseModel):
    """Dados do cliente"""
    nome: str = Field(..., description="Nome completo do cliente")
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ")
    endereco: str = Field(..., description="Endereço completo")
    cidade: str = Field(..., description="Cidade e estado")
    telefone: str = Field(..., description="Telefone de contato")

class DadosCompletoItem(BaseModel):
    """Item individual dos dados completos da planilha"""
    row_number: Optional[str] = None
    
    # Dados do gráfico de payback
    Gráfico_Payback: Optional[str] = Field(None, alias="Gráfico Payback")
    col_2: Optional[str] = None
    col_3: Optional[str] = None
    col_4: Optional[str] = None
    col_5: Optional[str] = None
    col_6: Optional[str] = None
    col_7: Optional[str] = None
    
    # Dados da conta de energia
    DADOS_DA_CONTA_DE_ENERGIA: Optional[str] = Field(None, alias="DADOS DA CONTA DE ENERGIA")
    
    class Config:
        populate_by_name = True

class PropostaInput(BaseModel):
    """Entrada completa para criação de proposta"""
    cliente: ClienteInput
    dados_completos: List[Dict[str, Any]] = Field(..., description="Array com todos os dados da planilha")

class PropostaResponse(BaseModel):
    """Resposta após criar proposta"""
    status: str
    numero_proposta: str
    proposta_id: str
    proposta_url: str
    message: str

class VisualizacaoResponse(BaseModel):
    """Dados de uma visualização"""
    id: int
    proposta_id: str
    visualizado_em: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

class EstatisticasResponse(BaseModel):
    """Estatísticas de visualizações de uma proposta"""
    proposta_id: str
    total_visualizacoes: int
    primeira_visualizacao: Optional[datetime]
    ultima_visualizacao: Optional[datetime]
    historico: List[VisualizacaoResponse]
