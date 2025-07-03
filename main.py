import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from fpdf import FPDF
import google.generativeai as genai
from bcb import sgs
import numpy as np

# Funções de Geração de Gráficos

def plot_revenue_vs_profit(df, timestamp, color_map):
    try:
        sales_summary = df.groupby('Nome_Vendedor').agg(Faturamento=('Valor_Total', 'sum'), Lucro=('Lucro', 'sum')).sort_values(by='Faturamento', ascending=False)
        x = np.arange(len(sales_summary.index))
        width = 0.35
        fig, ax = plt.subplots(figsize=(12, 7))
        rects1 = ax.bar(x - width/2, sales_summary['Faturamento'], width, label='Faturamento', color='cornflowerblue')
        rects2 = ax.bar(x + width/2, sales_summary['Lucro'], width, label='Lucro Líquido', color='mediumseagreen')
        ax.set_ylabel('Valor (R$)')
        ax.set_title('Faturamento vs. Lucro Líquido por Vendedor')
        ax.set_xticks(x)
        ax.set_xticklabels(sales_summary.index, rotation=45, ha="right")
        ax.legend()
        ax.bar_label(rects1, padding=3, fmt='R$ %.0f')
        ax.bar_label(rects2, padding=3, fmt='R$ %.0f')
        fig.tight_layout()
        path = f"temp_graficos/revenue_vs_profit_{timestamp}.png"
        plt.savefig(path)
        plt.close()
        return path
    except Exception: return None

def plot_product_analysis(df, timestamp):
    try:
        paths = {}
        top_products = df.groupby('Nome_Produto')['Valor_Total'].sum().nlargest(10)
        path_products = f"temp_graficos/top_10_products_{timestamp}.png"
        plt.figure(figsize=(10, 8))
        plt.barh(top_products.index, top_products.values, color='skyblue')
        plt.xlabel('Faturamento Total (R$)')
        plt.ylabel('Produto')
        plt.title('Top 10 Produtos Mais Vendidos (por Faturamento)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(path_products)
        plt.close()
        paths['top_products'] = path_products

        top_categories = df.groupby('Categoria')['Valor_Total'].sum().nlargest(10)
        path_categories = f"temp_graficos/top_10_categories_{timestamp}.png"
        plt.figure(figsize=(10, 6))
        plt.bar(top_categories.index, top_categories.values, color='mediumseagreen')
        plt.xlabel('Categoria')
        plt.ylabel('Faturamento Total (R$)')
        plt.title('Top 10 Categorias Mais Vendidas (por Faturamento)')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(path_categories)
        plt.close()
        paths['top_categories'] = path_categories
        return paths
    except Exception: return None

def plot_economic_indicators(timestamp):
    try:
        end_date = date.today()
        start_date = end_date - relativedelta(months=24)
        start_str, end_str = start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        
        ipca_data = sgs.get({'ipca': 433}, start=start_str, end=end_str)
        selic_data = sgs.get({'selic': 432}, start=start_str, end=end_str)
        
        paths = {}
        
        path_ipca = f"temp_graficos/ipca_evolution_{timestamp}.png"
        plt.figure(figsize=(10, 5))
        plt.plot(ipca_data.index, ipca_data['ipca'], marker='o', linestyle='-')
        plt.title('Evolução do IPCA (Inflação) - Últimos 24 Meses')
        plt.ylabel('Variação Mensal (%)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(path_ipca)
        plt.close()
        paths['ipca_chart'] = path_ipca

        path_selic = f"temp_graficos/selic_evolution_{timestamp}.png"
        plt.figure(figsize=(10, 5))
        plt.plot(selic_data.index, selic_data['selic'], marker='o', linestyle='-', color='red')
        plt.title('Evolução da Taxa SELIC Meta (Média Mensal) - Últimos 24 Meses')
        plt.ylabel('Taxa Anual (%)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(path_selic)
        plt.close()
        paths['selic_chart'] = path_selic
        return paths
    except Exception: return None


# Funções de Geração de Conteúdo

def generate_textual_insights(df):
    """Compila um resumo em texto de todos os dados analisados para enviar à IA."""
    insights = ["RESUMO DOS DADOS QUANTITATIVOS PARA ANÁLISE:\n"]
    try:
        sales_by_person = df.groupby('Nome_Vendedor')['Valor_Total'].sum()
        profit_by_person = df.groupby('Nome_Vendedor')['Lucro'].sum()
        
        insights.append(f"--- Métricas Gerais da Equipe (para comparação) ---")
        insights.append(f"Faturamento médio por vendedor: R$ {sales_by_person.mean():,.2f}")
        insights.append(f"Lucro médio por vendedor: R$ {profit_by_person.mean():,.2f}")
        insights.append(f"Média de desconto geral da equipe: {df['Desconto_Aplicado_Percent'].mean():.2%}\n")
        
        insights.append(f"--- Lucro Total ---\nLucro Líquido Total: R$ {df['Lucro'].sum():,.2f}\n")
        insights.append(f"--- Faturamento Total ---\nFaturamento Total: R$ {df['Valor_Total'].sum():,.2f}\n")
        insights.append(f"--- Lucro por Vendedor ---\n{profit_by_person.sort_values(ascending=False).to_string(float_format='R$ %.2f')}\n")
        top_products = df.groupby('Nome_Produto')['Valor_Total'].sum().nlargest(5)
        insights.append(f"--- Top 5 Produtos por Faturamento ---\n{top_products.to_string(float_format='R$ %.2f')}\n")
        top_categories = df.groupby('Categoria')['Valor_Total'].sum().nlargest(5)
        insights.append(f"--- Top 5 Categorias por Faturamento ---\n{top_categories.to_string(float_format='R$ %.2f')}\n")
    except KeyError as e:
        return f"Não foi possível gerar o resumo em texto. Coluna não encontrada: {e}"
    return "\n".join(insights)

def gerar_analise_ia(textual_summary, api_key):
    """Usa a API do Gemini para gerar uma análise textual, usando o prompt detalhado."""
    if not api_key or api_key == "SUA_CHAVE_API_AQUI":
        return "Análise por IA desativada. Configure a chave da API no arquivo .env."
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    today = date.today().strftime("%d de %B de %Y")
    location = "Jaraguá do Sul, SC, Brasil"

    prompt_final = f"""
    **Função:** Você é um analista de negócios e estrategista de BI sênior de elite. Sua tarefa é criar o relatório MAIS COMPLETO E DETALHADO POSSÍVEL a partir dos dados fornecidos. Siga RIGOOROSAMENTE esta estrutura em formato Markdown. NÃO invente dados ou explique a ausência de dados. Apenas analise os números que foram fornecidos no resumo.

    **ESTRUTURA OBRIGATÓRIA DO RELATÓRIO:**
    1.  **SUMÁRIO EXECUTIVO:** Um parágrafo conciso resumindo as descobertas mais críticas.
    2.  **CONTEXTO ECONÔMICO (ANÁLISE EXTERNA):** Comente o impacto das tendências de IPCA e SELIC no poder de compra e crédito.
    3.  **DIAGNÓSTICO DO NEGÓCIO (ANÁLISE INTERNA):**
        * **3.1. Performance Financeira:** Avalie a saúde financeira (lucro, faturamento). Calcule e comente a margem de lucro média da empresa (Lucro Total / Faturamento Total).
        * **3.2. Análise de Produtos e Categorias:** Identifique produtos "campeões" (faturamento) e "de alta margem" (lucratividade).
    4.  **ANÁLISE DE PERFORMANCE INDIVIDUAL (VENDEDORES):**
        * Para CADA vendedor, crie uma subseção.
        * Compare o faturamento, lucro e descontos de cada um com a MÉDIA DA EQUIPE.
        * Dê um diagnóstico claro (ex: "Alto Volume, Baixa Margem") e 1-2 sugestões PRÁTICAS.
    5.  **PLANO DE AÇÃO ESTRATÉGICO:** Liste 3-5 recomendações ACIONÁVEIS (Porquê, Como, KPI para medir).

    **Contexto para a Análise:**
    - **Data:** {today}
    - **Localização:** {location}

    **Resumo de Dados para Análise:**
    {textual_summary}
    """
    try:
        response = model.generate_content(prompt_final)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao contatar a IA: {e}"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Relatório Estratégico de Vendas', 0, 1, 'C')
        self.set_font('Arial', '', 8)
        self.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 6, title, 0, 1, 'L')
        self.ln(4)
    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, text.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()
    def add_image(self, image_path):
        if image_path and os.path.exists(image_path):
            self.image(image_path, w=190)
            self.ln(5)

def criar_pdf_corrigido(analise_ia, caminhos_graficos):
    pdf = PDF()
    pdf.add_page()
    
    mapa_titulos_graficos = {
        "CONTEXTO ECONÔMICO": ['ipca_chart', 'selic_chart'],
        "Performance Financeira": ['revenue_vs_profit'],
        "Análise de Produtos e Categorias": ['top_products', 'top_categories'],
    }
    
    secoes = analise_ia.split('**')
    
    for i in range(1, len(secoes), 2):
        titulo = secoes[i].strip()
        corpo = secoes[i+1].strip() if (i+1) < len(secoes) else ""

        pdf.chapter_title(titulo)
        pdf.chapter_body(corpo)
        
        for titulo_mapa, chaves_graficos in mapa_titulos_graficos.items():
            if titulo_mapa in titulo:
                for chave in chaves_graficos:
                    if chave in caminhos_graficos and caminhos_graficos[chave]:
                        pdf.add_image(caminhos_graficos[chave])
    
    return bytes(pdf.output(dest='S'))

# Função Orquestradora Principal

def gerar_relatorio_completo(df, api_key):
    """
    Função principal que orquestra todo o processo de análise.
    Recebe o DataFrame e a chave da API, e retorna o texto da IA e os bytes do PDF.
    """
    # 1. Preparação e Limpeza de Dados
    for col in ['Valor_Unitario', 'Custo_Unitario', 'Desconto_Aplicado_Percent']:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
    df['Quantidade'] = df['Quantidade'].astype(int)
    
    df_concluido = df[df['Status_Venda'] == 'Concluída'].copy()
    df_concluido['Valor_Bruto'] = df_concluido['Valor_Unitario'] * df_concluido['Quantidade']
    df_concluido['Valor_Desconto_Reais'] = df_concluido['Valor_Bruto'] * df_concluido['Desconto_Aplicado_Percent']
    df_concluido['Valor_Total'] = df_concluido['Valor_Bruto'] - df_concluido['Valor_Desconto_Reais']
    df_concluido['Custo_Total'] = df_concluido['Custo_Unitario'] * df_concluido['Quantidade']
    df_concluido['Lucro'] = df_concluido['Valor_Total'] - df_concluido['Custo_Total']
    
    # 2. Geração de todos os gráficos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("temp_graficos", exist_ok=True)
    
    vendedores = df_concluido['Nome_Vendedor'].unique()
    cmap = plt.get_cmap('tab20', len(vendedores))
    color_map = {vendedor: cmap(i) for i, vendedor in enumerate(vendedores)}
    
    caminhos_graficos = {}
    caminhos_graficos.update(plot_product_analysis(df_concluido, timestamp) or {})
    caminhos_graficos['revenue_vs_profit'] = plot_revenue_vs_profit(df_concluido, timestamp, color_map)
    caminhos_graficos.update(plot_economic_indicators(timestamp) or {})

    # 3. Geração do Resumo em Texto para a IA
    textual_summary_for_ai = generate_textual_insights(df_concluido)
    
    # 4. Geração da Análise pela IA
    analise_ia = gerar_analise_ia(textual_summary_for_ai, api_key)
    
    # 5. Criação do PDF
    pdf_bytes = criar_pdf_corrigido(analise_ia, caminhos_graficos)
    
    return analise_ia, pdf_bytes