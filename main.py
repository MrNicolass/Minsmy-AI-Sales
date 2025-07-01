import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

df = pd.read_csv('sales.csv', index_col=0, na_values=['NA'], delimiter=";", header=0)
filtered = pd.DataFrame([])
unique_indices = []

for i in df['Nome_Vendedor'].values:
    if i not in unique_indices:
        unique_indices.append(i)

filtered['Salesperson'] = unique_indices

#Check if the column is a string, then, converts to float
if df['Valor_Unitario'].dtype in ('object', 'str', 'string'):
    df['Valor_Unitario'] = df['Valor_Unitario'].astype(str).str.replace(',', '.').astype('double')
    
sales_orders = df[['Nome_Vendedor', 'Valor_Unitario', 'Quantidade']].astype({'Nome_Vendedor': str, 'Valor_Unitario': 'double', 'Quantidade': int}).values

def salesAmoutPerSalesMan(sales_orders):
    """
    Calculates the total sales amount and quantity sold per salesperson from a list of sales orders.
    Args:
        sales_orders (list): A list of lists, where each inner list contains the following elements in order:
            - salesman_name (str): The name of the salesperson.
            - product_value (float or int): The value of the product sold.
            - quantity_saled (int): The quantity of the product sold.
    Returns:
        dict: A dictionary mapping each salesperson's name (str) to a tuple: (total_sales_amount (float or int), total_quantity_sold (int)).
    Example:
        sales_orders = [
            ["Alice", 10.0, 2],
            ["Bob", 15.0, 1],
            ["Alice", 5.0, 3]
        ]
        results in {'Alice': (35.0, 5), 'Bob': (15.0, 1)}
    """
    unique_sale = {}

    for sales in sales_orders:
        for idx, sale in enumerate(sales):
            if type(sale) == str:
                if sale not in unique_sale:
                    unique_sale[sale] = (0,0)
            elif sales[idx-1] in unique_sale:
                actual_value, actual_quantity = unique_sale[sales[idx-1]]
                unique_sale[sales[idx-1]] = (actual_value + (sales[idx] * sales[idx+1]), actual_quantity + sales[idx+1])
    
    return unique_sale

#Adds the 'Sold' column to the 'filtered' DataFrame using the values from the unique_sale dict
salesman_totals = salesAmoutPerSalesMan(sales_orders)
filtered['Sold'] = filtered['Salesperson'].map(lambda x: salesman_totals.get(x, (0, 0))[0])
filtered['Quantity'] = filtered['Salesperson'].map(lambda x: salesman_totals.get(x, (0, 0))[1])

#Create folders to save graphs
os.makedirs("results", exist_ok=True)
os.makedirs("results/total_amount_of_sales", exist_ok=True)

#Define timestamp and graph location
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
total_amount_of_sales = f"results/total_amount_of_sales/sales_per_salesperson{timestamp}.png"

plt.figure(figsize=(10, 6))
plt.bar(filtered['Salesperson'], filtered['Sold'])
plt.gca().bar_label(plt.gca().containers[0], labels=[f"R$ {v:,.2f}" for v in filtered['Sold']], padding=2)
plt.xlabel('Salesperson')
plt.ylabel('Total Sold (R$)')
plt.title('Total amount of sales per salesperson')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(total_amount_of_sales)
plt.close()