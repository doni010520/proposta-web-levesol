from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
from dotenv import load_dotenv
import os
import traceback

# Carregar variáveis de ambiente
load_dotenv()

# Imports locais
from app.models.schemas import (
    PropostaInput, 
    PropostaResponse, 
    EstatisticasResponse,
    VisualizacaoResponse
)
from app.db.database import Database
from app.web.html_generator import HTMLGenerator

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Propostas Web - LEVESOL",
    description="API para geração e tracking de propostas de energia solar",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
db = Database()
html_generator = HTMLGenerator()

# Configurações
BASE_URL = os.getenv("BASE_URL", "http://localhost:8182")


@app.get("/")
def read_root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Sistema de Propostas Web - LEVESOL",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "criar_proposta": "POST /api/proposta",
            "visualizar_proposta": "GET /proposta/{proposta_id}",
            "estatisticas": "GET /api/proposta/{proposta_id}/stats",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check para monitoramento"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "proposta-web-api"
    }


@app.post("/api/proposta", response_model=PropostaResponse)
async def criar_proposta(dados: PropostaInput):
    """
    Cria uma nova proposta e retorna o link para visualização
    
    - **cliente**: Dados do cliente (nome, CPF/CNPJ, endereço, etc)
    - **dados_completos**: Array com todos os dados da planilha
    
    Retorna:
    - **proposta_id**: UUID da proposta
    - **proposta_url**: Link para visualização (enviar ao cliente)
    - **numero_proposta**: Número formatado da proposta
    """
    try:
        # Gerar número da proposta
        numero_proposta = f"{datetime.now().strftime('%d%m%y')}/{datetime.now().year}"
        
        # Preparar dados do cliente
        cliente_dict = {
            "nome": dados.cliente.nome,
            "cpf_cnpj": dados.cliente.cpf_cnpj,
            "endereco": dados.cliente.endereco,
            "cidade": dados.cliente.cidade,
            "telefone": dados.cliente.telefone
        }
        
        # Extrair dados do sistema e payback
        dados_sistema, dados_payback = html_generator.extrair_dados(dados.dados_completos)
        
        # Salvar no banco de dados
        proposta_id = db.salvar_proposta(
            numero_proposta=numero_proposta,
            cliente=cliente_dict,
            dados_sistema=dados_sistema,
            dados_payback=dados_payback
        )
        
        # Gerar URL da proposta
        proposta_url = f"{BASE_URL}/proposta/{proposta_id}"
        
        return PropostaResponse(
            status="success",
            numero_proposta=numero_proposta,
            proposta_id=proposta_id,
            proposta_url=proposta_url,
            message="Proposta criada com sucesso! Envie o link ao cliente."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
    except Exception as e:
        print(f"Erro ao criar proposta: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar proposta: {str(e)}"
        )


@app.get("/proposta/{proposta_id}", response_class=HTMLResponse)
async def visualizar_proposta(proposta_id: str, request: Request):
    """
    Renderiza a proposta como página HTML
    
    IMPORTANTE: Este endpoint também registra automaticamente cada visualização
    para tracking (IP, user agent, timestamp)
    """
    try:
        # Buscar proposta no banco
        proposta = db.buscar_proposta(proposta_id)
        
        if not proposta:
            raise HTTPException(
                status_code=404,
                detail="Proposta não encontrada. Verifique se o ID está correto."
            )
        
        # REGISTRAR VISUALIZAÇÃO (tracking automático)
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        try:
            db.registrar_visualizacao(
                proposta_id=proposta_id,
                ip_address=client_ip,
                user_agent=user_agent
            )
        except Exception as e:
            # Não falhar se o tracking der erro
            print(f"Aviso: Falha ao registrar visualização: {str(e)}")
        
        # Preparar dados do cliente
        cliente_dict = {
            "nome": proposta["cliente_nome"],
            "cpf_cnpj": proposta["cliente_cpf_cnpj"],
            "endereco": proposta["cliente_endereco"],
            "cidade": proposta["cliente_cidade"],
            "telefone": proposta["cliente_telefone"]
        }
        
        # Reconstruir dados_completos a partir dos dados salvos
        # (necessário para o html_generator)
        dados_completos = []
        
        # Adicionar dados de payback
        for item in proposta["dados_payback"]:
            dados_completos.append({
                "Gráfico Payback": str(item["ano"]),
                "col_2": str(item["amortizacao"]),
                "col_3": str(item["economia_mensal"])
            })
        
        # Adicionar dados do sistema
        dados_sistema = proposta["dados_sistema"]
        mapeamento_inverso = {
            "consumo_atual": "Consumo Total Permitido (mês) kwh:",
            "num_modulos": "Quantidade de módulos",
            "potencia_kwp": "Potência do sistema",
            "potencia_inversor": "Potência do inversor",
            "area_total": "Área total instalada",
            "geracao_mensal": "Energia Média Gerada (mês)",
            "geracao_anual": "Energia Média Gerada (ano)",
            "conta_antes": "Valor da conta antes",
            "conta_depois": "Valor da conta depois",
            "investimento": "Preço do Sistema",
            "tipo_fornecimento": "Padrão do Cliente"
        }
        
        for key, label in mapeamento_inverso.items():
            if key in dados_sistema:
                dados_completos.append({
                    "DADOS DA CONTA DE ENERGIA": label,
                    "col_7": str(dados_sistema[key])
                })
        
        # Gerar HTML
        html_content = html_generator.gerar_proposta_html(
            proposta_id=proposta_id,
            numero_proposta=proposta["numero_proposta"],
            cliente=cliente_dict,
            dados_completos=dados_completos
        )
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao visualizar proposta: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar proposta: {str(e)}"
        )


@app.get("/api/proposta/{proposta_id}/stats", response_model=EstatisticasResponse)
async def estatisticas_proposta(proposta_id: str):
    """
    Retorna estatísticas de visualizações da proposta
    
    - **total_visualizacoes**: Número total de vezes que foi aberta
    - **primeira_visualizacao**: Data/hora da primeira abertura
    - **ultima_visualizacao**: Data/hora da última abertura
    - **historico**: Lista completa de todas as visualizações
    """
    try:
        # Verificar se proposta existe
        proposta = db.buscar_proposta(proposta_id)
        if not proposta:
            raise HTTPException(status_code=404, detail="Proposta não encontrada")
        
        # Buscar visualizações
        visualizacoes = db.listar_visualizacoes(proposta_id)
        
        # Preparar resposta
        visualizacoes_response = [
            VisualizacaoResponse(
                id=v["id"],
                proposta_id=v["proposta_id"],
                visualizado_em=v["visualizado_em"],
                ip_address=v.get("ip_address"),
                user_agent=v.get("user_agent")
            )
            for v in visualizacoes
        ]
        
        return EstatisticasResponse(
            proposta_id=proposta_id,
            total_visualizacoes=len(visualizacoes),
            primeira_visualizacao=visualizacoes[-1]["visualizado_em"] if visualizacoes else None,
            ultima_visualizacao=visualizacoes[0]["visualizado_em"] if visualizacoes else None,
            historico=visualizacoes_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )


@app.post("/api/proposta/{proposta_id}/track-engagement")
async def track_engagement(proposta_id: str, request: Request):
    """
    Endpoint para tracking adicional de engajamento
    (chamado via JavaScript após 5 segundos na página)
    """
    try:
        # Pode adicionar lógica adicional aqui se necessário
        return {"status": "tracked"}
    except:
        return {"status": "ignored"}


@app.post("/api/proposta/{proposta_id}/track-exit")
async def track_exit(proposta_id: str, request: Request):
    """
    Endpoint para tracking de saída da página
    (chamado via JavaScript quando usuário sai)
    """
    try:
        # Pode adicionar lógica adicional aqui se necessário
        return {"status": "tracked"}
    except:
        return {"status": "ignored"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("APP_PORT", 8182))
    host = os.getenv("APP_HOST", "0.0.0.0")
    
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║  Sistema de Propostas Web - LEVESOL                 ║
    ║  Rodando em: http://{host}:{port}              ║
    ║  Documentação: http://{host}:{port}/docs       ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host=host, port=port, log_level="info")
