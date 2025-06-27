# Minsmy-AI-Sales

# Geração Automática de Relatórios de Vendas com IA

## 1. Problema

Gerentes de vendas, donos de pequenas empresas e analistas de dados frequentemente gastam horas toda semana ou mês coletando, analisando e transformando dados brutos de vendas em relatórios. O processo é **manual, repetitivo, propenso a erros** e pouco escalável.

### 1.1 Por que é Importante e Quem Afeta

Este problema afeta qualquer profissional que precise tomar decisões baseadas em dados de vendas. A lentidão do processo atrasa decisões críticas, e análises mal feitas podem comprometer o crescimento do negócio. Sem tempo ou ferramentas adequadas, profissionais perdem oportunidades valiosas.

### 1.2 Problemática Exemplificada

> Imagine a **Ana**, gerente de uma rede de lojas em Jaraguá do Sul. Toda primeira segunda-feira do mês, ela passa **o dia inteiro** no Excel. Calcula totais, filiais, produtos parados, melhores vendedores... No final, envia gráficos e números.  
>
> Mas não há tempo para investigar **por que a filial central vendeu 30% a mais do produto X**. Nosso projeto transforma esse trabalho de 8 horas em **5 minutos**, entregando um relatório com **análises e recomendações automáticas**, como se Ana tivesse um **assistente especialista** ao lado dela.

---

## 2. Coleta ou Simulação de Dados

Para fins de prototipagem e privacidade, os dados utilizados são **simulados**.

### 2.1 Simulação e Premissas

Utilizamos as bibliotecas **Python Faker** e **Pandas** para gerar um conjunto de dados fictícios, porém realistas, sobre vendas em múltiplas filiais, com vendedores, categorias e variações mensais.

### 2.2 Estrutura da Planilha

A planilha (`vendas.csv`) contém as seguintes colunas:

| Campo          | Descrição                                      |
|----------------|------------------------------------------------|
| ID_Venda       | Identificador único da venda                   |
| Data_Venda     | Data da transação (últimos 12 meses)           |
| Produto        | Nome do produto                                |
| Categoria      | Categoria do produto (ex: Roupa)               |
| Valor_Unitario | Preço por unidade                              |
| Quantidade     | Quantidade vendida                             |
| Vendedor       | Nome do vendedor                               |
| Filial         | Loja responsável pela venda                    |

---

## 3. Implementação da Solução

A arquitetura da solução segue o seguinte **fluxo**:

**Planilha (CSV)** → [**Fase 1: Python/Pandas**] → [**Fase 2: IA (LLM)**] → [**Fase 3: Relatório PDF**]

### Fase 1: Análise de Dados com Python

- Leitura do arquivo `vendas.csv` com `pandas`
- Cálculo de indicadores principais (KPIs):
  - Receita total
  - Receita por categoria
  - Top 5 produtos (por receita e por volume)
  - Desempenho por vendedor e filial
  - Crescimento mês a mês
- Geração de **gráficos** com `matplotlib` ou `seaborn`:
  - Gráfico de barras por categoria
  - Linha da receita mensal

### Fase 2: Geração de Insights com IA

- Envio dos KPIs e resumos para uma **IA generativa** (ex: [Gemini API](https://ai.google.dev))
- Engenharia de prompt personalizada para criar um **relatório narrativo**
- A resposta inclui análises, destaques, oportunidades e recomendações estratégicas

### Fase 3: Compilação do Relatório (PDF)

- A resposta da IA (em Markdown) é transformada em PDF com a biblioteca `fpdf2`
- O relatório inclui:
  - Título e seções bem formatadas
  - Gráficos gerados na Fase 1
  - Texto com insights e sugestões
- Output final: `Relatorio_Vendas_Junho_2025.pdf`

---

## 4. Conclusão

Este projeto resolve um problema **real, urgente e comum** no mundo dos negócios:

- ✅ **Economia de tempo**: De 8 horas para 5 minutos
- ✅ **Análises consistentes e personalizadas**
- ✅ **Integração moderna** entre Python e IA Generativa
- ✅ **Fácil de adaptar** para marketing, financeiro, RH, etc.

É uma solução **modular e escalável**, ideal tanto para uso interno quanto para evolução em produtos SaaS futuros.

> Feito com ❤️ para tornar a análise de dados mais inteligente e humana.

## Equipe
A equipe envolvida neste projeto é constituída por alunos da 6ª Fase (20251) do curso de Engenharia de Software do Centro Universitário Católica SC de Jaraguá do Sul.

<div align="center">
<table>
  <tr>
    <td align="center"><a href="https://github.com/HigorAz"><img loading="lazy" src="https://avatars.githubusercontent.com/u/141787745?v=4" width="115"><br><sub>Higor Azevedo</sub></a></td>
    <td align="center"><a href="https://github.com/AoiteFoca"><img loading="lazy" src="https://avatars.githubusercontent.com/u/141975272?v=4" width="115"><br><sub>Nathan Cielusinski</sub></a></td>
    <td align="center"><a href="https://github.com/MrNicolass"><img loading="lazy" src="https://avatars.githubusercontent.com/u/80847876?v=4" width="115"><br><sub>Nicolas Gustavo Conte</sub></a></td>
  </tr>
</div>
