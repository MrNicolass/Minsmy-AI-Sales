# Minsmy-AI-Sales: Automated Sales Reporting with AI

## 1. Problem Statement

Sales managers, small business owners, and data analysts often spend hours every week or month collecting, analyzing, and transforming raw sales data into reports. The process is **manual, repetitive, prone to errors**, and does not scale effectively.

### 1.1 Why It Matters & Who It Affects

This problem affects any professional who needs to make data-driven sales decisions. The slow pace of manual reporting delays critical choices, and flawed analyses can compromise business growth. Without adequate time or tools, professionals miss out on valuable opportunities.

### 1.2 The Problem in Action

> Imagine **Ana**, the manager of a retail chain in Jaraguá do Sul, Brazil. On the first Monday of every month, she spends her **entire day** in Excel. She calculates totals, branch performance, stagnant products, top salespeople... At the end of the day, she sends out some charts and numbers.
>
> But there's no time to investigate **why the central branch sold 30% more of product X**. Our project transforms this 8-hour ordeal into a **5-minute process**, delivering a report with **automated analysis and recommendations**, as if Ana had an **expert assistant** by her side.

---

## 2. Data Source

For prototyping and privacy purposes, the data used in this project is **simulated**.

### 2.1 Simulation and Assumptions

We use the **Python Faker** and **Pandas** libraries to generate a fictional yet realistic dataset covering sales across multiple branches, with different salespeople, categories, and monthly variations.

### 2.2 Data Schema

The `sales.csv` spreadsheet must contain the following columns. The script is designed to handle this specific structure.

| Field | Description | Example |
| :--- | :--- | :--- |
| `ID_Venda` | Unique sale identifier | `1` |
| `Data_Venda` | Transaction date (format: YYYY-MM-DD) | `2025-06-23` |
| `Nome_Produto` | Name of the product sold | `Camisa Polo Branca M` |
| `Categoria` | Product category | `Vestuário Masculino`|
| `Tipo_Cliente` | Type of customer | `Novo Cliente` |
| `Valor_Unitario`| Price per unit (use comma for decimals)| `120,50` |
| `Custo_Unitario`| Production cost per unit (use comma) | `45,20` |
| `Quantidade` | Quantity of units sold | `2` |
| `Desconto_Aplicado_Percent`| Discount percentage (0.1 = 10%)| `0.1` |
| `Nome_Vendedor` | Name of the salesperson | `Beatriz Costa` |
| `Filial` | Store/branch responsible for the sale| `Filial Centro` |
| `Metodo_Pagamento`| Payment method used | `Cartão de Crédito` |
| `Canal_Venda` | Sales channel | `Física` or `Online` |
| `Status_Venda` | Sale status | `Concluída` or `Devolvida`|

---

## 3. Setup and Execution

Follow these steps to set up and run the project on your local machine.

### Step 1: Prerequisites
- Ensure you have Python 3.8 or newer installed.

### Step 2: Clone the Repository
```bash
git clone [https://github.com/MrNicolass/Minsmy-AI-Sales.git](https://github.com/MrNicolass/Minsmy-AI-Sales.git)
cd Minsmy-AI-Sales
```

### Step 3: Set Up the Python Environment
It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

Now, install all the necessary libraries with a single command:
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a file named `.env` in the root directory of the project. This file will securely store your API key.

**`.env`**
```
GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"
```
Replace `YOUR_GROQ_API_KEY_HERE` with your actual API key from the [Groq Console](https://console.groq.com/keys).

### Step 5: Prepare the Data File (`sales.csv`)
You must create a file named `sales.csv` in the project's root directory, as the script will read data from it.

- The file **must** use a semicolon (`;`) as the delimiter.
- The file **must** contain all the columns listed in the [Data Schema](#22-data-schema) section.

Here is an example of two rows to guide you:
```csv
ID_Venda;Data_Venda;Nome_Produto;Categoria;Tipo_Cliente;Valor_Unitario;Custo_Unitario;Quantidade;Desconto_Aplicado_Percent;Nome_Vendedor;Filial;Metodo_Pagamento;Canal_Venda;Status_Venda
1;2025-06-15;Bolsa de Couro Preta;Acessórios;Cliente Frequente;350,00;120,00;1;0.05;Beatriz Costa;Filial Centro;Cartão de Crédito;Física;Concluída
2;2025-06-15;Tênis Casual Preto 41;Calçados;Novo Cliente;289,90;95,50;1;0.0;Ana Pereira;Filial Norte;PIX;Online;Concluída
```

### Step 6: Run the Script
With the environment activated and the `.env` and `sales.csv` files in place, simply run the main script from your terminal:

```bash
python main.py
```
The script will execute, generate all the charts and the final AI-powered report, and save them inside the `results/` directory.

---

## 4. Solution Implementation

The solution's architecture follows this flow:

**Spreadsheet (CSV)** → [**Phase 1: Python/Pandas**] → [**Phase 2: AI (LLM)**] → [**Phase 3: Markdown Report**]

### Phase 1: Data Analysis with Python

- Reads the `sales.csv` file using `pandas`.
- Calculates key performance indicators (KPIs): total revenue, net profit, revenue by category, top products, and performance by salesperson.
- Fetches real economic data (inflation and interest rates) from the **Central Bank of Brazil's API** using the `python-bcb` library.
- Generates multiple charts with `matplotlib` to visualize all findings.

### Phase 2: Insight Generation with AI

- Sends the calculated KPIs and data summaries to a **Generative AI** (Llama 3 via Groq API).
- Uses a highly detailed and structured prompt to instruct the AI to generate a **narrative report**.
- The AI's response includes in-depth analysis, business diagnostics, individual salesperson feedback, and strategic recommendations.

### Phase 3: Report Compilation

- The AI's text-based response is received by the script.
- A Python function assembles the final report by **programmatically injecting the generated charts** into the AI's narrative.
- The final output is a **Markdown (`.md`) file**, which provides rich formatting and embeds the local images for a complete, visual, and portable report.

---

## 5. Conclusion

This project solves a **real, urgent, and common** problem in the business world:

-   **Time Savings**: Reduces an 8-hour task to under 5 minutes.
-   **In-depth Analysis**: Provides consistent, personalized, and expert-level insights.
-   **Modern Integration**: Seamlessly combines Python data analysis with Generative AI.
-   **Adaptable**: Easy to adapt for other business areas like marketing, finance, or HR.

It is a **modular and scalable** solution, ideal for both internal use and as a foundation for future SaaS products.

> Made with ❤️ to make data analysis smarter and more human.

## Team

The team involved in this project consists of students from the 6th semester (2025/1) of the Software Engineering program at Centro Universitário Católica SC in Jaraguá do Sul.

<div align="center">
<table>
  <tr>
    <td align="center"><a href="https://github.com/HigorAz"><img loading="lazy" src="https://avatars.githubusercontent.com/u/141787745?v=4" width="115"><br><sub>Higor Azevedo</sub></a></td>
    <td align="center"><a href="https://github.com/AoiteFoca"><img loading="lazy" src="https://avatars.githubusercontent.com/u/141975272?v=4" width="115"><br><sub>Nathan Cielusinski</sub></a></td>
    <td align="center"><a href="https://github.com/MrNicolass"><img loading="lazy" src="https://avatars.githubusercontent.com/u/80847876?v=4" width="115"><br><sub>Nicolas Gustavo Conte</sub></a></td>
  </tr>
</div>