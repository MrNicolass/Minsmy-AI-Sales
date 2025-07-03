import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import main

# Configuração da Página e Carregamento da API Key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(layout="wide")
st.title("📈 Analisador Estratégico de Vendas com IA")
st.markdown("Faça o upload da sua planilha de vendas (`.csv` com separador `;`) para receber um relatório completo com análises, gráficos e plano de ação.")

# Interface Gráfica
with st.expander("Clique aqui para ver o formato esperado da planilha"):
    st.markdown("""
    Sua planilha deve conter as colunas: `ID_Venda`, `Data_Hora_Venda`, `SKU`, `Nome_Produto`, `Categoria`, `Valor_Unitario`, `Custo_Unitario`, `Quantidade`, `Desconto_Aplicado_Percent`, `ID_Cliente`, `Tipo_Cliente`, `ID_Vendedor`, `Nome_Vendedor`, `Filial`, `Canal_Venda`, `Metodo_Pagamento`, `Status_Venda`.
    **Observação:** O separador de colunas deve ser o **ponto e vírgula (;)**.
    """)

uploaded_file = st.file_uploader("Carregue sua planilha de vendas (.csv)", type="csv")

if uploaded_file is not None:
    if not API_KEY or API_KEY == "SUA_CHAVE_API_AQUI":
        st.error("Chave da API não encontrada. Por favor, configure seu arquivo .env com a chave correta.")
    else:
        try:
            df = pd.read_csv(uploaded_file, sep=';')
            st.success("Planilha carregada com sucesso! Iniciando análise completa...")

            # Bloco único para processamento com spinner
            with st.spinner('Analisando dados e gerando relatório completo... Por favor, aguarde.'):
                # Chamada única para a função principal que faz todo o trabalho
                analise_ia, pdf_bytes = main.gerar_relatorio_completo(df.copy(), API_KEY)

            st.success("Relatório Estratégico gerado com sucesso!")
            
            st.download_button(
                label="📥 Baixar Relatório Completo em PDF",
                data=pdf_bytes,
                file_name=f"relatorio_estrategico_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            
            st.markdown("---")
            st.subheader("📄 Prévia da Análise Gerada pela IA:")
            st.markdown(analise_ia)

        except Exception as e:
            st.error(f"Ocorreu um erro crítico durante o processamento: {e}")
            st.error("Por favor, verifique se a planilha segue o formato especificado e tente novamente.")