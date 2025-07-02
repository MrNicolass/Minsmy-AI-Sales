import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# Importa as funções do nosso arquivo de lógica principal
import main

# --- Configuração da Página e Carregamento da API Key ---

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(layout="wide")
st.title("🤖 Analisador de Vendas com IA")
st.markdown("Faça o upload da sua planilha de vendas em formato `.csv` para receber uma análise completa e recomendações estratégicas geradas por IA.")

# --- Interface Gráfica (Streamlit) ---

# Instruções para o usuário
with st.expander("Clique aqui para ver o formato esperado da planilha"):
    st.markdown("""
    Sua planilha deve conter, no mínimo, as seguintes colunas:
    - `ID_Venda`, `Data_Hora_Venda`, `SKU`, `Nome_Produto`, `Categoria`
    - `Valor_Unitario`, `Custo_Unitario`, `Quantidade`, `Desconto_Aplicado_Percent`
    - `ID_Cliente`, `Tipo_Cliente`, `ID_Vendedor`, `Nome_Vendedor`
    - `Filial`, `Canal_Venda`, `Metodo_Pagamento`, `Status_Venda`
    
    **Observação:** O separador de colunas deve ser o ponto e vírgula (`;`).
    """)

uploaded_file = st.file_uploader("Carregue sua planilha de vendas (.csv)", type="csv")

if uploaded_file is not None:
    # Verifica se a chave da API foi carregada
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "SUA_CHAVE_API_AQUI":
        st.error("Chave da API do Google não encontrada. Por favor, configure seu arquivo .env.")
    else:
        try:
            # Lê o arquivo CSV enviado pelo usuário, especificando o separador
            df = pd.read_csv(uploaded_file, sep=';')
            
            st.success("Planilha carregada com sucesso! Processando...")

            # Orquestra a execução das funções do main.py
            with st.spinner('1/3 - Calculando indicadores e gerando gráficos...'):
                kpis, caminhos_graficos = main.processar_dados_vendas(df.copy())
            
            with st.spinner('2/3 - A IA está analisando os dados e preparando as recomendações...'):
                analise_ia = main.gerar_analise_ia(kpis, GOOGLE_API_KEY)

            with st.spinner('3/3 - Montando o relatório em PDF...'):
                pdf_bytes = main.criar_pdf(analise_ia, caminhos_graficos)

            st.success("Relatório gerado com sucesso!")
            
            # Exibe o botão de download para o usuário
            st.download_button(
                label="Baixar Relatório em PDF",
                data=pdf_bytes,
                file_name=f"relatorio_vendas_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            
            st.markdown("---")
            st.subheader("Análise Gerada pela IA:")
            st.markdown(analise_ia)

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
            st.error("Por favor, verifique se o arquivo está no formato correto e tente novamente.")