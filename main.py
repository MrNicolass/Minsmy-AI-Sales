import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from fpdf import FPDF
import google.generativeai as genai
import io

# --- Funções de Lógica de Negócio (O "Motor" da Aplicação) ---

def processar_dados_vendas(df):
    """
    Processa o DataFrame de vendas para calcular KPIs e gerar gráficos.
    Esta função é o núcleo da análise de dados.
    Retorna um dicionário com os KPIs e um dicionário com os caminhos dos gráficos salvos.
    """
    # 1. Limpeza e Preparação dos Dados
    for col in ['Valor_Unitario', 'Custo_Unitario', 'Desconto_Aplicado_Percent']:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
    
    df['Quantidade'] = df['Quantidade'].astype(int)
    df_valido = df[df['Status_Venda'] == 'Concluída'].copy()

    # 2. Cálculos de KPIs
    df_valido['Receita_Bruta'] = df_valido['Valor_Unitario'] * df_valido['Quantidade']
    df_valido['Valor_Desconto'] = df_valido['Receita_Bruta'] * df_valido['Desconto_Aplicado_Percent']
    df_valido['Receita_Liquida'] = df_valido['Receita_Bruta'] - df_valido['Valor_Desconto']
    df_valido['Lucro'] = df_valido['Receita_Liquida'] - (df_valido['Custo_Unitario'] * df_valido['Quantidade'])
    
    kpis = {
        "receita_total": df_valido['Receita_Liquida'].sum(),
        "lucro_total": df_valido['Lucro'].sum(),
        "ticket_medio": df_valido['Receita_Liquida'].mean(),
        "total_vendas": len(df_valido),
        "vendas_por_vendedor": df_valido.groupby('Nome_Vendedor')['Receita_Liquida'].sum().sort_values(ascending=False),
        "lucro_por_categoria": df_valido.groupby('Categoria')['Lucro'].sum().sort_values(ascending=False),
        "top_5_produtos_receita": df_valido.groupby('Nome_Produto')['Receita_Liquida'].sum().nlargest(5),
        "vendas_por_canal": df_valido.groupby('Canal_Venda')['Receita_Liquida'].sum()
    }

    # 3. Geração de Gráficos
    os.makedirs("temp_graficos", exist_ok=True)
    caminhos_graficos = {}

    plt.figure(figsize=(10, 6))
    kpis['vendas_por_vendedor'].plot(kind='bar', color='skyblue')
    plt.title('Receita Total por Vendedor')
    plt.ylabel('Receita (R$)')
    plt.xlabel('Vendedor')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    caminho_grafico1 = "temp_graficos/vendas_vendedor.png"
    plt.savefig(caminho_grafico1)
    plt.close()
    caminhos_graficos['vendas_vendedor'] = caminho_grafico1

    plt.figure(figsize=(10, 6))
    kpis['lucro_por_categoria'].plot(kind='pie', autopct='%1.1f%%', startangle=90, colormap='viridis')
    plt.title('Distribuição de Lucro por Categoria')
    plt.ylabel('')
    plt.tight_layout()
    caminho_grafico2 = "temp_graficos/lucro_categoria.png"
    plt.savefig(caminho_grafico2)
    plt.close()
    caminhos_graficos['lucro_categoria'] = caminho_grafico2
    
    return kpis, caminhos_graficos

def gerar_analise_ia(kpis, api_key):
    """
    Usa a API do Gemini para gerar uma análise textual baseada nos KPIs.
    """
    if not api_key or api_key == "SUA_CHAVE_API_AQUI":
        return "Análise por IA desativada. Configure a chave da API no arquivo .env."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return f"Erro ao configurar a API do Google: {e}"
    
    prompt_kpis = f"""
    - Receita Total: R$ {kpis['receita_total']:.2f}
    - Lucro Total: R$ {kpis['lucro_total']:.2f}
    - Ticket Médio por Venda: R$ {kpis['ticket_medio']:.2f}
    - Ranking de Vendedores (por receita):\n{kpis['vendas_por_vendedor'].to_string()}
    - Lucro por Categoria:\n{kpis['lucro_por_categoria'].to_string()}
    - Top 5 Produtos (por receita):\n{kpis['top_5_produtos_receita'].to_string()}
    """

    prompt_final = f"""
    **Função:** Você é um Diretor Comercial e especialista em análise de vendas com 20 anos de experiência. Sua análise é afiada, direta e focada em ações práticas.
    **Contexto:** Você está analisando os dados de vendas do último mês de uma rede de lojas de vestuário. Abaixo estão os principais indicadores de desempenho (KPIs) calculados.
    **KPIs do Mês:**\n{prompt_kpis}
    **Tarefa:** Com base nos KPIs fornecidos, escreva um relatório executivo em português. O relatório deve ter um tom profissional e estratégico. Divida o relatório nas seguintes seções, usando exatamente estes títulos em negrito:
    **1. Resumo Executivo:**
    Um parágrafo conciso com os principais destaques.
    **2. Análise de Desempenho e Diagnóstico:**
    Analise os resultados em detalhes. Identifique pontos fortes e fracos.
    **3. Recomendações Estratégicas (Plano de Ação):**
    Forneça de 3 a 4 recomendações claras e acionáveis em uma lista numerada para resolver problemas ou potencializar pontos fortes.
    """
    
    try:
        response = model.generate_content(prompt_final)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao contatar a IA: {e}"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatório de Análise de Vendas', 0, 1, 'C')
        self.set_font('Arial', '', 8)
        self.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, text.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()

    def add_image_section(self, title, image_path):
        self.add_page()
        self.chapter_title(title)
        self.image(image_path, x=10, w=190)

def criar_pdf(analise_ia, caminhos_graficos):
    """
    Cria um arquivo PDF com a análise e os gráficos.
    Retorna o PDF como um objeto de bytes.
    """
    pdf = PDF()
    pdf.add_page()
    
    partes = analise_ia.split('**')
    for parte in partes:
        if parte.strip():
            if any(titulo in parte for titulo in ["1. Resumo Executivo", "2. Análise de Desempenho e Diagnóstico", "3. Recomendações Estratégicas"]):
                pdf.chapter_title(parte.replace(":", "").strip())
            else:
                pdf.chapter_body(parte.strip())

    pdf.add_image_section("Gráfico: Receita por Vendedor", caminhos_graficos['vendas_vendedor'])
    pdf.add_image_section("Gráfico: Lucro por Categoria", caminhos_graficos['lucro_categoria'])
    
    return bytes(pdf.output(dest='S'))