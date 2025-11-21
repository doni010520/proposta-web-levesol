from jinja2 import Environment, FileSystemLoader
import os
from typing import Dict, List, Any, Tuple

class HTMLGenerator:
    def __init__(self):
        """Inicializa o gerador de HTML com templates Jinja2"""
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template('proposta_template.html')
    
    def _clean_currency(self, value_str) -> float:
        """
        Converte uma string de moeda para float de forma segura.
        Mesma lógica do gerador de PDF original.
        """
        if value_str is None:
            return 0.0
        try:
            s = str(value_str).replace("R$", "").strip()
            s = s.replace(" ", "")
            
            if ',' in s and '.' in s:
                pos_virgula = s.rfind(',')
                pos_ponto = s.rfind('.')
                
                if pos_ponto > pos_virgula:
                    s = s.replace(',', '')
                else:
                    s = s.replace('.', '').replace(',', '.')
            elif ',' in s:
                partes = s.split(',')
                if len(partes[-1]) == 2:
                    s = s.replace(',', '.')
                else:
                    s = s.replace(',', '')
            
            return float(s)
        except (ValueError, TypeError) as e:
            print(f"Erro ao converter '{value_str}': {e}")
            return 0.0
    
    def extrair_dados(self, dados_completos: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extrai dados do sistema e payback do JSON unificado.
        Mesma lógica do gerador de PDF original.
        """
        dados_sistema = {}
        dados_payback = []
        
        for item in dados_completos:
            # Extrair dados do gráfico de payback
            if "Gráfico Payback" in item and item.get("col_2"):
                try:
                    valor = self._clean_currency(item["col_2"])
                    economia = self._clean_currency(item["col_3"])
                    ano = int(item["Gráfico Payback"])
                    dados_payback.append({
                        "ano": ano, 
                        "amortizacao": valor, 
                        "economia_mensal": economia
                    })
                except (ValueError, TypeError):
                    continue
            
            # Extrair dados da conta de energia
            if "DADOS DA CONTA DE ENERGIA" in item:
                campo = item["DADOS DA CONTA DE ENERGIA"]
                valor = item.get("col_7")
                
                key_map = {
                    "Consumo Total Permitido (mês) kwh:": "consumo_atual",
                    "Quantidade de módulos": "num_modulos",
                    "Potência do sistema": "potencia_kwp",
                    "Potência do inversor": "potencia_inversor",
                    "Área total instalada": "area_total",
                    "Energia Média Gerada (mês)": "geracao_mensal",
                    "Energia Média Gerada (ano)": "geracao_anual",
                    "Valor da conta antes": "conta_antes",
                    "Valor da conta depois": "conta_depois",
                    "Preço do Sistema": "investimento",
                    "Padrão do Cliente": "tipo_fornecimento"
                }
                
                for key, mapped_key in key_map.items():
                    if key in campo:
                        dados_sistema[mapped_key] = valor
                        break
        
        # Converter valores numéricos
        for key in ['num_modulos', 'investimento', 'conta_antes', 'area_total', 'geracao_mensal', 'consumo_atual']:
            if key in dados_sistema and dados_sistema[key] is not None:
                try:
                    dados_sistema[key] = self._clean_currency(dados_sistema[key])
                except (ValueError, TypeError):
                    dados_sistema[key] = 0
            else:
                dados_sistema[key] = 0
        
        return dados_sistema, dados_payback
    
    def calcular_payback(self, dados_payback: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Calcula o período de payback em anos e meses.
        Mesma lógica do gerador de PDF original.
        """
        for i, item in enumerate(dados_payback):
            if item["amortizacao"] > 0 and i > 0:
                valor_anterior = dados_payback[i-1]["amortizacao"]
                if valor_anterior < 0:
                    diferenca_anual = item["amortizacao"] - valor_anterior
                    if diferenca_anual > 0:
                        meses_para_zerar = (abs(valor_anterior) / (diferenca_anual / 12))
                        anos = i - 1
                        meses = int(meses_para_zerar)
                        if meses >= 12:
                            anos += meses // 12
                            meses %= 12
                        return anos, meses
        return 0, 0
    
    def gerar_proposta_html(
        self, 
        proposta_id: str,
        numero_proposta: str,
        cliente: Dict[str, str],
        dados_completos: List[Dict[str, Any]]
    ) -> str:
        """
        Gera HTML completo da proposta
        
        Args:
            proposta_id: UUID da proposta
            numero_proposta: Número formatado da proposta
            cliente: Dados do cliente
            dados_completos: Array com todos os dados da planilha
            
        Returns:
            str: HTML renderizado
        """
        # Extrair dados do sistema e payback
        dados_sistema, dados_payback = self.extrair_dados(dados_completos)
        
        # Calcular payback
        payback_anos, payback_meses = self.calcular_payback(dados_payback)
        
        # Economia total (último valor do payback)
        economia_total = dados_payback[-1]["amortizacao"] if dados_payback else 0
        
        # Renderizar template
        html_content = self.template.render(
            proposta_id=proposta_id,
            numero_proposta=numero_proposta,
            cliente=cliente,
            dados_sistema=dados_sistema,
            dados_payback=dados_payback,
            payback_anos=payback_anos,
            payback_meses=payback_meses,
            economia_total=economia_total
        )
        
        return html_content
