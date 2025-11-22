import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import re
import locale

# Tenta definir o locale para PT-BR para formatação de moeda
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass # fallback para o padrão se não conseguir

class HTMLGenerator:
    def __init__(self):
        # Define onde estão os templates
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Adiciona o filtro personalizado de moeda ao ambiente Jinja2
        self.env.filters['format_currency'] = self._format_currency_filter

    def _clean_currency(self, value_str):
        """
        Converte string de moeda (R$ 1.200,00) para float (1200.00)
        CORREÇÃO: Detecta se já é número e retorna direto
        """
        if not value_str:
            return 0.0
        
        # SE JÁ FOR NÚMERO (int ou float), RETORNA DIRETO
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        try:
            # Remove R$ e espaços
            s = str(value_str).replace("R$", "").replace(" ", "").strip()
            
            # Se NÃO tem vírgula, já é formato americano (ex: 1234.56 ou 3.5)
            if "," not in s:
                return float(s)
            
            # Se TEM vírgula, é formato BR (ex: 1.234,56)
            # Remove pontos de milhar e troca vírgula decimal por ponto
            s = s.replace(".", "").replace(",", ".")
            return float(s)
        except (ValueError, TypeError):
            return 0.0
            
    def _format_currency_filter(self, value):
        """Filtro Jinja2 para formatar moeda no padrão BRL (R$ 1.234,56)"""
        try:
            val_float = float(value)
            # Tenta usar o locale do sistema
            try:
                return locale.currency(val_float, grouping=True, symbol="R$ ")
            except:
                # Fallback manual se o locale falhar
                formatted = "{:,.2f}".format(val_float)
                formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
                return f"R$ {formatted}"
        except (ValueError, TypeError):
             return value # Retorna o valor original se não for número

    def _extract_data(self, dados_completos):
        """Extrai e limpa os dados do JSON bruto da planilha"""
        dados_sistema = {}
        dados_payback = []

        ano_atual = datetime.now().year

        for item in dados_completos:
            # Extrair dados da Tabela de Payback
            if "Gráfico Payback" in item and item.get("col_2"):
                try:
                    valor_ano = int(item["Gráfico Payback"])
                    saldo = self._clean_currency(item["col_2"])
                    economia = self._clean_currency(item["col_3"])
                    
                    # Detecta se é ano real (>= 2000) ou ano relativo (1, 2, 3...)
                    if valor_ano >= 2000:
                        ano_real = valor_ano
                        ano_relativo = valor_ano - ano_atual + 1
                    else:
                        ano_relativo = valor_ano
                        ano_real = ano_atual + ano_relativo - 1
                    
                    dados_payback.append({
                        "ano": ano_relativo,
                        "ano_real": ano_real,
                        "amortizacao": saldo,
                        "economia_mensal": economia
                    })
                except:
                    continue

            # Extrair dados gerais do Sistema e Conta
            if "DADOS DA CONTA DE ENERGIA" in item:
                campo = item["DADOS DA CONTA DE ENERGIA"]
                valor = item.get("col_7")
                
                # Mapeamento dos campos da planilha para nossas variáveis
                mapa = {
                    "Consumo Total Permitido (mês) kwh:": "consumo_atual",
                    "Quantidade de módulos": "num_modulos",
                    "Potência do sistema": "potencia_kwp",
                    "Potência do inversor": "potencia_inversor",
                    "Área total instalada": "area_total",
                    "Energia Média Gerada (mês)": "geracao_mensal",
                    "Valor da conta antes": "conta_antes",
                    "Preço do Sistema": "investimento",
                    "Padrão do Cliente": "tipo_fornecimento"
                }
                
                for chave_planilha, chave_sistema in mapa.items():
                    if chave_planilha in campo:
                        dados_sistema[chave_sistema] = valor

        # Limpar números do sistema (converter para float/int)
        for key in ['num_modulos', 'investimento', 'conta_antes', 'area_total', 'geracao_mensal', 'consumo_atual', 'potencia_kwp']:
            if key in dados_sistema:
                dados_sistema[key] = self._clean_currency(dados_sistema[key])
        
        # Tratamento especial para inteiros
        if 'num_modulos' in dados_sistema:
            dados_sistema['num_modulos'] = int(dados_sistema['num_modulos'])

        return dados_sistema, dados_payback

    def _calcular_payback_tempo(self, dados_payback):
        """Calcula anos e meses para o retorno do investimento"""
        for i, item in enumerate(dados_payback):
            saldo = item["amortizacao"]
            # Se o saldo ficou positivo neste ano
            if saldo > 0:
                # Se for o primeiro ano, o payback é em meses
                if i == 0:
                    # Estimativa simples: investimento / economia mensal média do ano
                    investimento_inicial = abs(dados_payback[0]["amortizacao"] - dados_payback[0]["economia_mensal"] * 12)
                    if dados_payback[0]["economia_mensal"] > 0:
                         meses_totais = int(investimento_inicial / dados_payback[0]["economia_mensal"])
                         return 0, meses_totais
                    return 0, 0

                # Se não for o primeiro ano, calcula a fração do ano
                saldo_anterior = dados_payback[i-1]["amortizacao"]
                if saldo_anterior < 0:
                    diferenca_anual = saldo - saldo_anterior
                    if diferenca_anual > 0:
                        fracao_ano = abs(saldo_anterior) / diferenca_anual
                        meses_extra = int(fracao_ano * 12)
                        # CORREÇÃO: Retorna o índice (número de anos desde o início)
                        anos = i
                        return anos, meses_extra
        
        # Se nunca ficar positivo na série fornecida
        return len(dados_payback), 0

    def render_proposal(self, json_entrada):
        """Método principal chamado pela API"""
        
        # 1. Processar dados
        dados_sistema, dados_payback = self._extract_data(json_entrada["dados_completos"])
        anos, meses = self._calcular_payback_tempo(dados_payback)
        
        # Calcular economia total (último ano da tabela)
        economia_total = dados_payback[-1]["amortizacao"] if dados_payback else 0

        # 2. Preparar dados para o Chart.js
        # Usar o ano real (str) para os labels do eixo X
        chart_labels = [str(d['ano_real']) for d in dados_payback]
        chart_values = [d['amortizacao'] for d in dados_payback]

        # 3. Limpar telefone para link do WhatsApp (apenas números)
        telefone_raw = json_entrada["cliente"].get("telefone", "")
        telefone_limpo = re.sub(r'\D', '', str(telefone_raw))
        if not telefone_limpo.startswith('55') and telefone_limpo:
            telefone_limpo = '55' + telefone_limpo

        # 4. Criar contexto para o Template
        contexto = {
            "numero_proposta": f"{datetime.now().strftime('%d%m%y')}/{datetime.now().year}",
            "cliente": {
                **json_entrada["cliente"],
                "telefone_limpo": telefone_limpo
            },
            "dados_sistema": dados_sistema,
            "dados_payback": dados_payback,
            "payback_anos": anos,
            "payback_meses": meses,
            "economia_total": economia_total,
            "chart_labels": chart_labels,
            "chart_values": chart_values
        }

        # 5. Renderizar HTML
        template = self.env.get_template('proposta_template.html')
        return template.render(contexto)
