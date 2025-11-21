import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import re

class HTMLGenerator:
    def __init__(self):
        # Define onde estão os templates
        # Ajuste o caminho conforme necessário dependendo de onde roda o main.py
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def _clean_currency(self, value_str):
        """Converte string de moeda (R$ 1.200,00) para float (1200.00)"""
        if not value_str:
            return 0.0
        try:
            # Remove R$ e espaços
            s = str(value_str).replace("R$", "").strip().replace(" ", "")
            # Se tiver vírgula e ponto, assume formato brasileiro (1.000,00)
            if ',' in s and '.' in s:
                s = s.replace('.', '').replace(',', '.')
            elif ',' in s:
                s = s.replace(',', '.')
            return float(s)
        except (ValueError, TypeError):
            return 0.0

    def _extract_data(self, dados_completos):
        """Extrai e limpa os dados do JSON bruto da planilha"""
        dados_sistema = {}
        dados_payback = []

        for item in dados_completos:
            # Extrair dados da Tabela de Payback
            if "Gráfico Payback" in item and item.get("col_2"):
                try:
                    ano = int(item["Gráfico Payback"])
                    saldo = self._clean_currency(item["col_2"])
                    economia = self._clean_currency(item["col_3"])
                    dados_payback.append({
                        "ano": ano,
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
        for key in ['num_modulos', 'investimento', 'conta_antes', 'area_total', 'geracao_mensal', 'consumo_atual']:
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
            if saldo > 0 and i > 0:
                saldo_anterior = dados_payback[i-1]["amortizacao"]
                if saldo_anterior < 0:
                    diferenca_anual = saldo - saldo_anterior
                    if diferenca_anual > 0:
                        fracao_ano = abs(saldo_anterior) / diferenca_anual
                        meses_totais = int(fracao_ano * 12)
                        anos = (i - 1) + (meses_totais // 12)
                        meses = meses_totais % 12
                        return anos, meses
        return 0, 0

    def render_proposal(self, json_entrada):
        """Método principal chamado pela API"""
        
        # 1. Processar dados
        dados_sistema, dados_payback = self._extract_data(json_entrada["dados_completos"])
        anos, meses = self._calcular_payback_tempo(dados_payback)
        
        # Calcular economia total (último ano da tabela)
        economia_total = dados_payback[-1]["amortizacao"] if dados_payback else 0

        # 2. Preparar dados para o Chart.js
        chart_labels = [f"Ano {d['ano']}" for d in dados_payback]
        chart_values = [d['amortizacao'] for d in dados_payback]

        # 3. Limpar telefone para link do WhatsApp (apenas números)
        telefone_raw = json_entrada["cliente"].get("telefone", "")
        telefone_limpo = re.sub(r'\D', '', str(telefone_raw))
        if not telefone_limpo.startswith('55'):
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
