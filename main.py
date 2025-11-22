from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORREÇÃO: Servir arquivos estáticos (logo)
app.mount("/static", StaticFiles(directory="app/assets"), name="static")

# Inicializar componentes
try:
    db = Database()
except:
    print("Aviso: Banco de dados não inicializado (Database class not found)")
    db = None

html_generator = HTMLGenerator()

# Configurações
BASE_URL = os.getenv("BASE_URL", "http://localhost:8182")


@app.get("/")
def read_root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Sistema de Propostas Web - LEVESOL",
        "version": "2.0.0",
        "endpoints": {
            "health": "GET /health",
            "criar_proposta": "POST /api/proposta",
            "preview_proposta": "POST /api/proposta/web (Teste sem salvar)",
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


@app.post("/api/proposta/web", response_class=HTMLResponse)
async def ver_proposta_web(dados: PropostaInput):
    """
    Gera a versão WEB interativa da proposta DIRETAMENTE (Sem salvar no banco).
    Útil para testes rápidos.
    """
    try:
        # Converte o modelo Pydantic para dict
        dados_dict = {
            "cliente": {
                "nome": dados.cliente.nome,
                "cpf_cnpj": dados.cliente.cpf_cnpj,
                "endereco": dados.cliente.endereco,
                "cidade": dados.cliente.cidade,
                "telefone": dados.cliente.telefone
            },
            "dados_completos": dados.dados_completos
        }
        
        # Gera o HTML usando o gerador
        html_content = html_generator.render_proposal(dados_dict)
        return html_content
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar página web: {str(e)}")


@app.post("/api/proposta", response_model=PropostaResponse)
async def criar_proposta(dados: PropostaInput):
    """
    Cria uma nova proposta, salva no banco e retorna o link para visualização.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Banco de dados não disponível")

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
        
        # Extrair dados limpos para salvar no banco
        dados_sistema, dados_payback = html_generator._extract_data(dados.dados_completos)
        
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
    Busca a proposta no banco e renderiza o HTML via Template.
    Registra visualização automaticamente.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Banco de dados não disponível")

    try:
        # Buscar proposta no banco
        proposta = db.buscar_proposta(proposta_id)
        
        if not proposta:
            raise HTTPException(
                status_code=404,
                detail="Proposta não encontrada. Verifique se o ID está correto."
            )
        
        # REGISTRAR VISUALIZAÇÃO (Tracking)
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        try:
            db.registrar_visualizacao(
                proposta_id=proposta_id,
                ip_address=client_ip,
                user_agent=user_agent
            )
        except Exception as e:
            print(f"Aviso: Falha ao registrar visualização: {str(e)}")
        
        # RECONSTRUÇÃO DOS DADOS
        cliente_dict = {
            "nome": proposta["cliente_nome"],
            "cpf_cnpj": proposta["cliente_cpf_cnpj"],
            "endereco": proposta["cliente_endereco"],
            "cidade": proposta["cliente_cidade"],
            "telefone": proposta["cliente_telefone"]
        }
        
        # Reconstruir 'dados_completos' baseados no que foi salvo no banco
        dados_completos_reconstruidos = []
        
        # 1. Adicionar dados de payback simulando linhas da planilha
        for item in proposta["dados_payback"]:
            dados_completos_reconstruidos.append({
                "Gráfico Payback": str(item["ano"]),
                "col_2": str(item["amortizacao"]),
                "col_3": str(item["economia_mensal"])
            })
        
        # 2. Adicionar dados do sistema simulando linhas da planilha
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
                dados_completos_reconstruidos.append({
                    "DADOS DA CONTA DE ENERGIA": label,
                    "col_7": str(dados_sistema[key])
                })
        
        # Montar payload final
        payload = {
            "cliente": cliente_dict,
            "dados_completos": dados_completos_reconstruidos
        }
        
        # Gerar HTML
        html_content = html_generator.render_proposal(payload)
        
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
    """Retorna estatísticas de visualizações da proposta"""
    if not db:
        raise HTTPException(status_code=503, detail="Banco de dados não disponível")
        
    try:
        proposta = db.buscar_proposta(proposta_id)
        if not proposta:
            raise HTTPException(status_code=404, detail="Proposta não encontrada")
        
        visualizacoes = db.listar_visualizacoes(proposta_id)
        
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
    """Tracking adicional de engajamento (ex: tempo na página)"""
    return {"status": "tracked"}


@app.post("/api/proposta/{proposta_id}/track-exit")
async def track_exit(proposta_id: str, request: Request):
    """Tracking de saída"""
    return {"status": "tracked"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("APP_PORT", 8182))
    host = os.getenv("APP_HOST", "0.0.0.0")
    
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║  Sistema de Propostas Web - LEVESOL                  ║
    ║  Rodando em: http://{host}:{port}                      ║
    ║  Documentação: http://{host}:{port}/docs               ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host=host, port=port, log_level="info")
