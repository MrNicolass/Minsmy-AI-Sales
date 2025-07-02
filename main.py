#region #Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os
import sys
import re

#Imports for AI integration
from autogen import AssistantAgent, UserProxyAgent
from groq import Groq
from dotenv import load_dotenv

#Import for real economic data
from bcb import sgs
#endregion

#Loads environment variables (GROQ_API_KEY)
load_dotenv()

#region #AI Configuration
#Configuration of the Groq language model to be used.
llama_config = {
    "config_list": [{"model": "llama3-70b-8192", "api_key": os.environ.get("GROQ_API_KEY"), "api_type": "groq"}],
    "temperature": 0.3,
}
#endregion

#region #Plotting Functions

#Generates a chart with the top 10 customer types by revenue.
def plot_top_customers(df, timestamp):
    try:
        #Validates if the required column exists in the DataFrame.
        if 'Valor_Total' not in df.columns:
            raise KeyError("'Valor_Total' column is missing.")
        
        #Groups data by customer type, calculating the sum and mean of sales.
        customer_sales = df.groupby('Tipo_Cliente')['Valor_Total'].agg(['sum', 'mean']).sort_values(by='sum', ascending=False).head(10)
        customer_sales = customer_sales.rename(columns={'sum': 'Total Comprado', 'mean': 'Média por Compra'})

        #Creates the directory to save the chart, if it doesn't exist.
        os.makedirs("results/customers", exist_ok=True)
        path = f"results/customers/customers_{timestamp}.png"

        #Creates the figure and the bar chart.
        plt.figure(figsize=(12, 7))
        bars = plt.bar(customer_sales.index, customer_sales['Total Comprado'], color='cornflowerblue')
        
        #Adds informative labels about the total and average on each bar.
        labels = [f"Total: R$ {total:,.2f}\nMédia: R$ {mean:,.2f}" for total, mean in zip(customer_sales['Total Comprado'], customer_sales['Média por Compra'])]
        plt.gca().bar_label(bars, labels=labels, padding=5, fontsize=9)

        #Configures the visual details of the chart.
        plt.xlabel('Tipo de Cliente')
        plt.ylabel('Total Comprado (R$)')
        plt.title('Vendas por Tipo de Cliente')
        plt.xticks(rotation=45, ha="right")
        plt.ylim(top=plt.gca().get_ylim()[1] * 1.25)
        plt.tight_layout()
        #Saves the chart to a file and closes the figure to free up memory.
        plt.savefig(path)
        plt.close()
        print(f"Gráfico de clientes salvo em: {path}")
        return path

    except KeyError as e:
        print(f"AVISO: Não foi possível gerar o gráfico de Top Clientes. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Generates a pie chart (donut chart) showing the distribution of payment methods.
def plot_payment_methods(df, timestamp):
    try:
        payment_counts = df['Metodo_Pagamento'].value_counts()
        
        os.makedirs("results/payment_methods", exist_ok=True)
        path = f"results/payment_methods/payment_methods_{timestamp}.png"

        plt.figure(figsize=(10, 8))
        colors = plt.get_cmap('Paired', len(payment_counts))
        plt.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%', startangle=140, pctdistance=0.85, colors=colors.colors)
        
        #Creates the circle in the center for the "donut" effect.
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.title('Distribuição de Métodos de Pagamento')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        print(f"Gráfico de métodos de pagamento salvo em: {path}")
        return path

    except KeyError as e:
        print(f"AVISO: Não foi possível gerar o gráfico de Métodos de Pagamento. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Generates two charts: one for total discounts (R$) and another for average discounts (%) per salesperson.
def plot_discounts_by_salesperson(df, timestamp, color_map):
    try:
        if 'Valor_Desconto_Reais' not in df.columns:
            raise KeyError("'Valor_Desconto_Reais' column is missing.")

        #Calculates discount statistics.
        total_discount_reais = df.groupby('Nome_Vendedor')['Valor_Desconto_Reais'].sum()
        avg_discount_percent = df.groupby('Nome_Vendedor')['Desconto_Aplicado_Percent'].mean()

        os.makedirs("results/discounts", exist_ok=True)
        paths = {}
        
        #Chart 1: Total discounts in R$.
        path_total = f"results/discounts/total_discounts_reais_{timestamp}.png"
        total_sorted = total_discount_reais.sort_values(ascending=False)
        colors_total = [color_map.get(v, 'gray') for v in total_sorted.index]
        plt.figure(figsize=(10, 6))
        plt.bar(total_sorted.index, total_sorted.values, color=colors_total)
        plt.gca().bar_label(plt.gca().containers[0], labels=[f"R$ {v:,.2f}" for v in total_sorted.values], padding=3)
        plt.xlabel('Vendedor')
        plt.ylabel('Total de Descontos Concedidos (R$)')
        plt.title('Total de Descontos Concedidos (R$) por Vendedor')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(path_total)
        plt.close()
        print(f"Gráfico de total de descontos (R$) salvo em: {path_total}")
        paths['total_discounts'] = path_total
        
        #Chart 2: Average discounts in %.
        path_avg = f"results/discounts/average_discounts_percent_{timestamp}.png"
        avg_sorted = avg_discount_percent.sort_values(ascending=False)
        colors_avg = [color_map.get(v, 'gray') for v in avg_sorted.index]
        plt.figure(figsize=(10, 6))
        plt.bar(avg_sorted.index, avg_sorted.values, color=colors_avg)
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        plt.gca().bar_label(plt.gca().containers[0], labels=[f"{v:.1%}" for v in avg_sorted.values], padding=3)
        plt.xlabel('Vendedor')
        plt.ylabel('Média de Desconto Concedido (%)')
        plt.title('Média de Desconto (%) por Vendedor')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(path_avg)
        plt.close()
        print(f"Gráfico de média de descontos (%) salvo em: {path_avg}")
        paths['avg_discounts'] = path_avg
        
        return paths

    except KeyError as e:
        print(f"AVISO: Não foi possível gerar os gráficos de Descontos. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Generates charts for sales channels (Online vs. Physical) and revenue by branch.
def plot_sales_channels(df, timestamp):
    try:
        paths = {}
        channel_counts = df['Canal_Venda'].value_counts()

        os.makedirs("results/sales_channels", exist_ok=True)
        path_channels = f"results/sales_channels/sales_channels_{timestamp}.png"

        plt.figure(figsize=(8, 6))
        plt.pie(channel_counts, labels=channel_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
        plt.title('Vendas Online vs. Vendas Físicas')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(path_channels)
        plt.close()
        print(f"Gráfico de canais de venda salvo em: {path_channels}")
        paths['channels'] = path_channels

        #Generates branch chart only if there are 'Physical' sales.
        physical_sales = df[df['Canal_Venda'] == 'Física']
        if not physical_sales.empty and 'Filial' in physical_sales.columns:
            branch_sales = physical_sales.groupby('Filial')['Valor_Total'].sum().sort_values(ascending=False)
            os.makedirs("results/branch_sales", exist_ok=True)
            path_branches = f"results/branch_sales/branch_sales_{timestamp}.png"
            plt.figure(figsize=(10, 6))
            plt.bar(branch_sales.index, branch_sales.values, color='teal')
            plt.gca().bar_label(plt.gca().containers[0], labels=[f"R$ {v:,.2f}" for v in branch_sales.values], padding=2)
            plt.xlabel('Filial')
            plt.ylabel('Total Vendido (R$)')
            plt.title('Total de Vendas por Filial (Lojas Físicas)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(path_branches)
            plt.close()
            print(f"Gráfico de vendas por filial salvo em: {path_branches}")
            paths['branches'] = path_branches
        
        return paths

    except KeyError as e:
        print(f"AVISO: Não foi possível gerar os gráficos de Canais de Venda. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Generates charts for sales status (Completed vs. Returned) and returns by salesperson.
def plot_sales_status(df, timestamp, color_map):
    try:
        paths = {}
        status_counts = df['Status_Venda'].value_counts()
        os.makedirs("results/sales_status", exist_ok=True)
        path_status = f"results/sales_status/sales_status_{timestamp}.png"
        
        plt.figure(figsize=(8, 6))
        plt.bar(status_counts.index, status_counts.values, color=['lightgreen', 'salmon'])
        plt.gca().bar_label(plt.gca().containers[0], padding=2)
        plt.xlabel('Status da Venda')
        plt.ylabel('Quantidade')
        plt.title('Total de Vendas Concluídas vs. Devolvidas')
        plt.tight_layout()
        plt.savefig(path_status)
        plt.close()
        print(f"Gráfico de status de vendas salvo em: {path_status}")
        paths['status'] = path_status

        #Generates returns chart only if there are returned sales.
        returned_sales = df[df['Status_Venda'] == 'Devolvida']
        if not returned_sales.empty:
            returns_by_salesperson = returned_sales['Nome_Vendedor'].value_counts()
            path_returns = f"results/sales_status/returns_by_salesperson_{timestamp}.png"
            colors_returns = [color_map.get(v, 'gray') for v in returns_by_salesperson.index]
            plt.figure(figsize=(10, 6))
            plt.bar(returns_by_salesperson.index, returns_by_salesperson.values, color=colors_returns)
            plt.gca().bar_label(plt.gca().containers[0], padding=2)
            plt.xlabel('Vendedor')
            plt.ylabel('Número de Devoluções')
            plt.title('Vendedores com Mais Devoluções')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(path_returns)
            plt.close()
            print(f"Gráfico de devoluções por vendedor salvo em: {path_returns}")
            paths['returns'] = path_returns

        return paths
    
    except KeyError as e:
        print(f"AVISO: Não foi possível gerar os gráficos de Status de Venda. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Generates a chart with the total and per-salesperson net profit.
def plot_profit_analysis(df, timestamp, color_map):
    try:
        if 'Lucro' not in df.columns:
            raise KeyError("'Lucro' column is missing.")

        profit_by_salesperson = df.groupby('Nome_Vendedor')['Lucro'].sum().sort_values(ascending=False)
        total_profit = df['Lucro'].sum()
        
        os.makedirs("results/profit", exist_ok=True)
        path = f"results/profit/profit_by_salesperson_{timestamp}.png"

        colors = [color_map.get(v, 'gray') for v in profit_by_salesperson.index]
        plt.figure(figsize=(10, 6))
        plt.bar(profit_by_salesperson.index, profit_by_salesperson.values, color=colors)
        plt.gca().bar_label(plt.gca().containers[0], labels=[f"R$ {v:,.2f}" for v in profit_by_salesperson.values], padding=3)
        
        plt.xlabel('Vendedor')
        plt.ylabel('Lucro Líquido (R$)')
        plt.title(f'Lucro Líquido por Vendedor (Total: R$ {total_profit:,.2f})')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        print(f"Gráfico de lucro por vendedor salvo em: {path}")
        return path

    except KeyError as e:
        print(f"AVISO: Não foi possível gerar o gráfico de Lucro. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Generates product analysis charts: top 10 products and top 10 categories.
def plot_product_analysis(df, timestamp):
    try:
        paths = {}
        os.makedirs("results/products", exist_ok=True)
        
        #Top 10 products chart.
        top_products = df.groupby('Nome_Produto')['Valor_Total'].sum().nlargest(10)
        path_products = f"results/products/top_10_products_{timestamp}.png"
        plt.figure(figsize=(10, 8))
        plt.barh(top_products.index, top_products.values, color='skyblue')
        plt.xlabel('Faturamento Total (R$)')
        plt.ylabel('Produto')
        plt.title('Top 10 Produtos Mais Vendidos (por Faturamento)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(path_products)
        plt.close()
        print(f"Gráfico de top produtos salvo em: {path_products}")
        paths['top_products'] = path_products

        #Top 10 categories chart.
        top_categories = df.groupby('Categoria')['Valor_Total'].sum().nlargest(10)
        path_categories = f"results/products/top_10_categories_{timestamp}.png"
        plt.figure(figsize=(10, 6))
        plt.bar(top_categories.index, top_categories.values, color='mediumseagreen')
        plt.xlabel('Categoria')
        plt.ylabel('Faturamento Total (R$)')
        plt.title('Top 10 Categorias Mais Vendidas (por Faturamento)')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(path_categories)
        plt.close()
        print(f"Gráfico de top categorias salvo em: {path_categories}")
        paths['top_categories'] = path_categories

        return paths

    except KeyError as e:
        print(f"AVISO: Não foi possível gerar os gráficos de Produtos. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Generates a comparative chart of Revenue vs. Profit per salesperson.
def plot_revenue_vs_profit(df, timestamp):
    try:
        if 'Lucro' not in df.columns or 'Valor_Total' not in df.columns:
            raise KeyError("'Lucro' or 'Valor_Total' column is missing.")

        #Groups data by salesperson, summing Revenue and Profit.
        sales_summary = df.groupby('Nome_Vendedor').agg(
            Faturamento=('Valor_Total', 'sum'),
            Lucro=('Lucro', 'sum')
        ).sort_values(by='Faturamento', ascending=False)

        #Setup for the grouped bar chart.
        x = np.arange(len(sales_summary.index))
        width = 0.35

        #Creates the figure and bars.
        fig, ax = plt.subplots(figsize=(12, 7))
        rects1 = ax.bar(x - width/2, sales_summary['Faturamento'], width, label='Faturamento', color='cornflowerblue')
        rects2 = ax.bar(x + width/2, sales_summary['Lucro'], width, label='Lucro Líquido', color='mediumseagreen')

        #Adds labels and titles.
        ax.set_ylabel('Valor (R$)')
        ax.set_title('Faturamento vs. Lucro Líquido por Vendedor')
        ax.set_xticks(x, sales_summary.index, rotation=45, ha="right")
        ax.legend()

        ax.bar_label(rects1, padding=3, fmt='R$ %.0f')
        ax.bar_label(rects2, padding=3, fmt='R$ %.0f')

        fig.tight_layout()

        #Saves the chart.
        os.makedirs("results/profit", exist_ok=True)
        path = f"results/profit/revenue_vs_profit_{timestamp}.png"
        plt.savefig(path)
        plt.close()
        print(f"Gráfico de Faturamento vs. Lucro salvo em: {path}")
        return path

    except KeyError as e:
        print(f"AVISO: Não foi possível gerar o gráfico de Faturamento vs. Lucro. Coluna não encontrada: {e}. Pulando...", file=sys.stderr)
        return None

#Fetches and plots real economic data from the Central Bank of Brazil.
def plot_economic_indicators(timestamp):
    try:
        print("Buscando dados econômicos do Banco Central do Brasil...")
        #Define a 24-month date range for fetching data.
        end_date = date.today()
        start_date = end_date - relativedelta(months=24)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        #Fetch data for IPCA (Inflation) and SELIC (Interest Rate).
        ipca_data = sgs.get({'ipca': 433}, start=start_str, end=end_str)
        selic_data = sgs.get({'selic': 432}, start=start_str, end=end_str)
        
        #Resample daily SELIC data to monthly mean for a cleaner chart.
        if not selic_data.empty:
            selic_data = selic_data.resample('M').mean()

        paths = {}
        os.makedirs("results/economic_context", exist_ok=True)

        #Plot IPCA (Inflation)
        path_ipca = f"results/economic_context/ipca_evolution_{timestamp}.png"
        plt.figure(figsize=(10, 5))
        plt.plot(ipca_data.index, ipca_data['ipca'], marker='o', linestyle='-')
        plt.title('Evolução do IPCA (Inflação) - Últimos 24 Meses')
        plt.ylabel('Variação Mensal (%)')
        plt.xlabel('Data')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(path_ipca)
        plt.close()
        print(f"Gráfico do IPCA salvo em: {path_ipca}")
        paths['ipca_chart'] = path_ipca

        #Plot SELIC (Interest Rate)
        path_selic = f"results/economic_context/selic_evolution_{timestamp}.png"
        plt.figure(figsize=(10, 5))
        plt.plot(selic_data.index, selic_data['selic'], marker='o', linestyle='-', color='red')
        plt.title('Evolução da Taxa SELIC Meta (Média Mensal) - Últimos 24 Meses')
        plt.ylabel('Taxa Anual (%)')
        plt.xlabel('Data')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(path_selic)
        plt.close()
        print(f"Gráfico da SELIC salvo em: {path_selic}")
        paths['selic_chart'] = path_selic

        return paths
        
    except Exception as e:
        print(f"AVISO: Não foi possível buscar ou gerar os gráficos de dados econômicos. Erro: {e}. Pulando...", file=sys.stderr)
        return None
#endregion

#region #Insight Generation Functions

#Compiles a text summary of all analyzed data to send to the AI.
def generate_textual_insights(df):
    insights = ["RESUMO DOS DADOS QUANTITATIVOS PARA ANÁLISE:\n"]
    try:
        #Calculate team averages for comparison
        sales_by_person = df.groupby('Nome_Vendedor')['Valor_Total'].sum()
        profit_by_person = df.groupby('Nome_Vendedor')['Lucro'].sum()
        
        team_avg_revenue = sales_by_person.mean()
        team_avg_profit = profit_by_person.mean()
        team_avg_discount_pct = df['Desconto_Aplicado_Percent'].mean()
        
        insights.append(f"--- Métricas Gerais da Equipe (para comparação) ---")
        insights.append(f"Faturamento médio por vendedor: R$ {team_avg_revenue:,.2f}")
        insights.append(f"Lucro médio por vendedor: R$ {team_avg_profit:,.2f}")
        insights.append(f"Média de desconto geral da equipe: {team_avg_discount_pct:.2%}\n")

        insights.append(f"--- Lucro Total ---\nLucro Líquido Total: R$ {df['Lucro'].sum():,.2f}\n")
        
        insights.append(f"--- Lucro por Vendedor ---\n{profit_by_person.sort_values(ascending=False).to_string(float_format='R$ %.2f')}\n")

        top_customers = df.groupby('Tipo_Cliente')['Valor_Total'].sum().sort_values(ascending=False).head(5)
        insights.append(f"--- Top 5 Tipos de Cliente por Faturamento ---\n{top_customers.to_string(float_format='R$ %.2f')}\n")
        
        top_products = df.groupby('Nome_Produto')['Valor_Total'].sum().nlargest(5)
        insights.append(f"--- Top 5 Produtos por Faturamento ---\n{top_products.to_string(float_format='R$ %.2f')}\n")

        top_categories = df.groupby('Categoria')['Valor_Total'].sum().nlargest(5)
        insights.append(f"--- Top 5 Categorias por Faturamento ---\n{top_categories.to_string(float_format='R$ %.2f')}\n")
        
        idx = df.groupby('Categoria')['Valor_Total'].idxmax()
        top_product_per_category = df.loc[idx, ['Categoria', 'Nome_Produto', 'Valor_Total']].set_index('Categoria')
        insights.append(f"--- Produto Mais Vendido por Categoria ---\n{top_product_per_category.to_string()}\n")

        payment_methods = df['Metodo_Pagamento'].value_counts(normalize=True) * 100
        insights.append(f"--- Distribuição dos Métodos de Pagamento ---\n{payment_methods.to_string(float_format='%.1f%%')}\n")

        total_discounts = df.groupby('Nome_Vendedor')['Valor_Desconto_Reais'].sum().sort_values(ascending=False)
        insights.append(f"--- Vendedores por Total de Desconto (R$) ---\n{total_discounts.to_string(float_format='R$ %.2f')}\n")

        avg_discounts = df.groupby('Nome_Vendedor')['Desconto_Aplicado_Percent'].mean()
        insights.append(f"--- Vendedores por Média de Desconto (%) ---\n{(avg_discounts * 100).to_string(float_format='%.1f%%')}\n")

        returns_by_salesperson = df[df['Status_Venda'] == 'Devolvida']['Nome_Vendedor'].value_counts()
        if not returns_by_salesperson.empty:
            insights.append(f"--- Vendedores com Mais Devoluções ---\n{returns_by_salesperson.to_string()}\n")
        
        total_sales_status = df['Status_Venda'].value_counts()
        insights.append(f"--- Status Geral das Vendas ---\n{total_sales_status.to_string()}\n")

    except KeyError as e:
        return f"Não foi possível gerar o resumo em texto. Coluna não encontrada: {e}"

    return "\n".join(insights)

#Assembles the final Markdown report by injecting graph links into the AI's generated text.
def assemble_final_report(ai_text_response, graph_paths):
    #Correctly calculates the relative path from the .md file to the graph file.
    md_file_dir = os.path.abspath("results/ai_insights")

    #Maps a keyword from the AI's likely response to a graph path key.
    graph_map = {
        r"Contexto Econômico": ['ipca_chart', 'selic_chart'],
        r"Performance Financeira": ['revenue_vs_profit'],
        r"Performance Individual": ['profit_by_salesperson'],
        r"Análise de Produtos e Categorias": ['top_products', 'top_categories'],
    }
    
    #Inject graph links into the AI's response text.
    for title, chart_keys in graph_map.items():
        #Use regex to find the title, ignoring case and allowing for variations.
        pattern = re.compile(f"({title})", re.IGNORECASE)
        match = pattern.search(ai_text_response)
        
        if match:
            insertion_point = match.end(1)
            markdown_links = ""
            for chart_key in chart_keys:
                if chart_key in graph_paths and graph_paths[chart_key]:
                    #Calculate the correct relative path from the markdown file's location.
                    relative_path = os.path.relpath(graph_paths[chart_key], md_file_dir)
                    #Ensure forward slashes for Markdown compatibility.
                    relative_path = relative_path.replace(os.sep, '/')
                    markdown_links += f"\n\n![Gráfico sobre {title}]({relative_path})\n\n"
            
            #Insert the links after the found title.
            ai_text_response = ai_text_response[:insertion_point] + markdown_links + ai_text_response[insertion_point:]

    return ai_text_response
#endregion

#region #Main Execution Block
if __name__ == '__main__':
    #region #Data Loading and Cleaning
    try:
        df = pd.read_csv('sales.csv', index_col=0, na_values=['NA'], delimiter=";", header=0)
    except FileNotFoundError:
        print("ERRO: O arquivo 'sales.csv' não foi encontrado. Verifique se o arquivo está no mesmo diretório que o script.", file=sys.stderr)
        sys.exit(1)

    #Helper function to clean numeric columns that may come as text with commas.
    def clean_numeric_column(series):
        if series.dtype in ('object', 'str', 'string'):
            return series.astype(str).str.replace(',', '.').astype('double')
        return series

    #Checks if all required columns exist in the file.
    required_cols = ['Valor_Unitario', 'Custo_Unitario', 'Desconto_Aplicado_Percent', 'Quantidade', 'Nome_Vendedor', 'Nome_Produto', 'Categoria', 'Tipo_Cliente', 'Metodo_Pagamento', 'Canal_Venda', 'Status_Venda']
    for col in required_cols:
        if col not in df.columns:
            print(f"ERRO: A coluna obrigatória '{col}' não foi encontrada no arquivo 'sales.csv'.", file=sys.stderr)
            sys.exit(1)

    #Applies cleaning and calculates metric columns (Total Value, Total Cost, Profit).
    df['Valor_Unitario'] = clean_numeric_column(df['Valor_Unitario'])
    df['Custo_Unitario'] = clean_numeric_column(df['Custo_Unitario'])
    df['Desconto_Aplicado_Percent'] = clean_numeric_column(df['Desconto_Aplicado_Percent'])
    
    df['Valor_Bruto'] = df['Valor_Unitario'] * df['Quantidade']
    df['Valor_Desconto_Reais'] = df['Valor_Bruto'] * df['Desconto_Aplicado_Percent']
    df['Valor_Total'] = df['Valor_Bruto'] - df['Valor_Desconto_Reais']
    df['Custo_Total'] = df['Custo_Unitario'] * df['Quantidade']
    df['Lucro'] = df['Valor_Total'] - df['Custo_Total']
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("results", exist_ok=True)
    #endregion

    #region #Chart Generation
    #Creates a color map to maintain visual consistency for salespeople across charts.
    vendedores = df['Nome_Vendedor'].unique()
    cmap = plt.get_cmap('tab20', len(vendedores))
    color_map = {vendedor: cmap(i) for i, vendedor in enumerate(vendedores)}

    #Dictionary to store the paths of the generated charts.
    graph_paths = {}

    #Generates the main revenue by salesperson chart.
    salesman_totals = df.groupby('Nome_Vendedor')['Valor_Total'].sum().sort_values(ascending=False)
    os.makedirs("results/total_amount_of_sales", exist_ok=True)
    total_amount_of_sales_path = f"results/total_amount_of_sales/sales_per_salesperson_{timestamp}.png"
    
    colors_original = [color_map.get(v, 'gray') for v in salesman_totals.index]
    plt.figure(figsize=(10, 6))
    plt.bar(salesman_totals.index, salesman_totals.values, color=colors_original)
    plt.gca().bar_label(plt.gca().containers[0], labels=[f"R$ {v:,.2f}" for v in salesman_totals.values], padding=2)
    plt.xlabel('Vendedor')
    plt.ylabel('Total Vendido (R$)')
    plt.title('Total de Vendas por Vendedor')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(total_amount_of_sales_path)
    plt.close()
    print(f"Gráfico de vendas por vendedor salvo em: {total_amount_of_sales_path}")

    #Calls all plotting functions and stores their paths.
    print("\nGerando gráficos adicionais...")
    graph_paths['top_customers'] = plot_top_customers(df, timestamp)
    graph_paths['payment_methods'] = plot_payment_methods(df, timestamp)
    
    discounts_paths = plot_discounts_by_salesperson(df, timestamp, color_map)
    if discounts_paths: graph_paths.update(discounts_paths)

    channels_paths = plot_sales_channels(df, timestamp)
    if channels_paths: graph_paths.update(channels_paths)

    status_paths = plot_sales_status(df, timestamp, color_map)
    if status_paths: graph_paths.update(status_paths)
    
    graph_paths['profit_by_salesperson'] = plot_profit_analysis(df, timestamp, color_map)
    
    product_paths = plot_product_analysis(df, timestamp)
    if product_paths: graph_paths.update(product_paths)

    graph_paths['revenue_vs_profit'] = plot_revenue_vs_profit(df, timestamp)

    economic_paths = plot_economic_indicators(timestamp)
    if economic_paths: graph_paths.update(economic_paths)

    print("\nProcesso de geração de gráficos concluído.")
    #endregion

    #region #AI Insight Generation
    print("\n--- Gerando Insights com o Especialista Focado ---")
    
    #Generates the text summary with data for the AI.
    textual_summary_for_ai = generate_textual_insights(df)
    if "Não foi possível" in textual_summary_for_ai:
        print(textual_summary_for_ai)
        sys.exit(1)
    
    #Creates the single, highly-instructed specialist agent.
    analyst_agent = AssistantAgent(
        name="Analista_Especialista_Senior",
        system_message="""Você é um analista de negócios e estrategista de BI sênior de elite. Sua tarefa é criar o relatório MAIS COMPLETO E DETALHADO POSSÍVEL a partir dos dados fornecidos. A superficialidade não é aceitável. Siga RIGOOROSAMENTE esta estrutura em formato Markdown.

        **ESTRUTURA OBRIGATÓRIA DO RELATÓRIO:**

        1.  **SUMÁRIO EXECUTIVO:** Um parágrafo conciso resumindo as descobertas mais críticas e a principal recomendação.

        2.  **CONTEXTO ECONÔMICO (ANÁLISE EXTERNA):**
            - **2.1. Cenário Macroeconômico (Brasil):** Com base nos dados sobre IPCA (inflação) e SELIC (juros), comente sobre como as tendências impactam o poder de compra e o custo do crédito.
            - **2.2. Cenário Microeconômico (Local):** Analise a economia específica da cidade/região fornecida.

        3.  **DIAGNÓSTICO DO NEGÓCIO (ANÁLISE INTERNA):**
            * **3.1. Performance Financeira:** Avalie a saúde financeira usando o lucro total e a relação faturamento vs. lucro. SEJA QUANTITATIVO: calcule e comente a margem de lucro média da empresa (Lucro Total / Faturamento Total).
            * **3.2. Análise de Produtos e Categorias:** Identifique produtos "campeões" (maior faturamento) e produtos "de alta margem" (maior lucratividade). Existe algum campeão que tem baixa margem?
            * **3.3. Eficiência Operacional e Riscos:** Analise os canais de venda, devoluções (calcule a taxa de devolução em %) e a política de descontos.

        4.  **ANÁLISE DE PERFORMANCE INDIVIDUAL (VENDEDORES):**
            * **Para CADA vendedor**, crie uma subseção individual e detalhada. **NÃO AGRUPE VENDEDORES.**
            * Para cada um, faça uma análise **QUANTITATIVA E COMPARATIVA**:
                - **Faturamento e Lucratividade:** Compare o faturamento e o lucro do vendedor com a MÉDIA DA EQUIPE (fornecida no resumo). Ex: "O faturamento de Carlos (R$ 2.973) ficou 15% abaixo da média da equipe (R$ 3.500)".
                - **Política de Descontos:** Compare a média de desconto do vendedor com a MÉDIA DA EQUIPE. Ex: "Sua média de desconto (2.7%) é quase o dobro da média da equipe (1.5%), o que explica sua baixa margem de lucro."
                - **Taxa de Devoluções:** Compare o número de devoluções com os outros vendedores.
                - **Diagnóstico e Recomendações:** Dê um diagnóstico claro (ex: "Vendedor de Alto Volume, Baixa Margem") e 1-2 sugestões PRÁTICAS e PERSONALIZADAS para ele.

        5.  **PLANO DE AÇÃO ESTRATÉGICO:**
            * Liste de 3 a 5 recomendações estratégicas CLARAS e ACIONÁVEIS.
            * Para cada recomendação, detalhe o "Porquê" (com base nos dados), o "Como" (passos para implementar) e o "KPI para Medir o Sucesso".

        6.  **LEITURAS RECOMENDADAS E FONTES:**
            * Forneça de 2 a 3 links **FUNCIONAIS, REAIS e de alta qualidade** para artigos ou relatórios que suportem sua análise. **NÃO invente links.**
        """,
        llm_config=llama_config,
    )

    #Creates the user proxy agent that will initiate the chat.
    user_proxy = UserProxyAgent(
        name="Admin",
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    #Defines the task prompt, including date and location.
    today = date.today().strftime("%d de %B de %Y")
    location = "Jaraguá do Sul, SC, Brasil"
    task_prompt = f"""
    Por favor, gere um relatório de análise de negócios completo e profundo, seguindo rigorosamente a estrutura e o nível de detalhe quantitativo definidos em seu perfil. Em sua análise, você receberá um resumo de dados que já contém os dados econômicos. Refira-se a eles conceitualmente (ex: 'como visto na tendência da SELIC...'), e o script se encarregará de inserir as imagens corretas.

    **Contexto para a Análise:**
    - **Data:** {today}
    - **Localização:** {location}

    **Resumo de Dados e Médias da Equipe para Análise:**
    {textual_summary_for_ai}
    """

    #Initiates the chat and captures the result.
    chat_result = user_proxy.initiate_chat(
        recipient=analyst_agent,
        message=task_prompt,
        max_turns=1,
        silent=True
    )

    #Saves the AI's response to a .md file and displays it in the console.
    if chat_result and chat_result.summary:
        ai_response_text = chat_result.summary
        
        #Assemble the final report by injecting graph links into the AI's text response.
        final_report_md = assemble_final_report(ai_response_text, graph_paths)

        os.makedirs("results/ai_insights", exist_ok=True)
        ai_insights_path = f"results/ai_insights/insights_{timestamp}.md"
        
        try:
            with open(ai_insights_path, 'w', encoding='utf-8') as f:
                f.write(final_report_md)
            print(f"\nInsights da IA salvos com sucesso em: {ai_insights_path}")
        except IOError as e:
            print(f"\nERRO: Não foi possível salvar o arquivo de insights da IA. Erro: {e}", file=sys.stderr)

        print("\n--- RELATÓRIO DO ESPECIALISTA SÊNIOR DE IA ---")
        print(final_report_md)
    else:
        print("\nNão foi possível obter uma resposta da IA. Verifique as configurações, a chave da API e o prompt do sistema.")
    #endregion
#endregion