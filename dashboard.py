import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import os

# --- 1. CONFIGURAÇÕES E CONEXÃO ---
USUARIO_DB = 'system'
SENHA_DB = '1234'
SERVIDOR_DB = 'xe'
STRING_CONEXAO = f'oracle+oracledb://{USUARIO_DB}:{SENHA_DB}@localhost:1521/{SERVIDOR_DB}'

QUERY_SQL = """
SELECT 
    C.NOME_CLIENTE AS "Cliente",
    E.NOME_EMPRESA AS "Comprou de",
    P.NOME_PRODUTO AS "Produto",
    V.DATA_VENDA AS "Data",
    V.QTD_VENDIDA AS "Qtd",
    V.VALOR_TOTAL_VENDA AS "Valor Gasto pelo Cliente"
FROM VENDAS V
JOIN CLIENTES C ON V.ID_CLIENTE = C.ID_CLIENTE
JOIN EMPRESAS E ON V.ID_EMPRESA = E.ID_EMPRESA
JOIN PRODUTOS P ON V.ID_PRODUTO = P.ID_PRODUTO
"""

def carregar_dados():
    try:
        engine = create_engine(STRING_CONEXAO)
        with engine.connect() as connection:
            df = pd.read_sql(QUERY_SQL, connection)
        df['Data'] = pd.to_datetime(df['Data']) 
        return df
    except Exception as e:
        print(f"Erro: {e}")
        return pd.DataFrame()

df = carregar_dados()

# --- 2. CRIAÇÃO DOS GRÁFICOS ---

# Gráfico 1: Barras (Vendas por Loja)
fig_barras = px.bar(
    df.groupby(["Comprou de"], as_index=False)["Valor Gasto pelo Cliente"].sum().sort_values(by="Valor Gasto pelo Cliente", ascending=False),
    x="Comprou de", y="Valor Gasto pelo Cliente", color="Comprou de",
    template="plotly_dark"
)
fig_barras.update_layout (
    legend=dict(
        font=dict(size=15)
    )
)

# Gráfico 2: Linha (Vendas no Tempo)
fig_linha = px.line(
    df.groupby("Data", as_index=False)["Valor Gasto pelo Cliente"].sum(),
    x="Data", y="Valor Gasto pelo Cliente", markers=True,
    template="plotly_dark"
)

# Gráfico 3: Pizza (Substituindo o Sunburst)
fig_pizza = px.pie(
    df, 
    values='Valor Gasto pelo Cliente', 
    names='Comprou de', 
    title='Distribuição de Vendas por Loja',
    template="plotly_dark"
)
fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
fig_pizza.update_layout(
    legend=dict(
        font=dict(size=15) 
    )
)

# Gráfico 4: Gauge (Velocímetro)
total_vendas = df["Valor Gasto pelo Cliente"].sum() if not df.empty else 0
fig_gauge = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = total_vendas,
    title = {'text': "Faturamento Total"},
    gauge = {'axis': {'range': [None, total_vendas * 1.5]}, 'bar': {'color': "#00CC96"}}
))
fig_gauge.update_layout(template="plotly_dark")

# --- 3. LAYOUT DO DASHBOARD ---

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


# dbc.Container: É a "caixa" principal que segura todo o conteúdo.
# fluid=True: Faz com que o dashboard ocupe toda a largura da tela.
app.layout = dbc.Container([
    
    # --- LINHA DO CABEÇALHO ---
    dbc.Row([
        # width=12: Em Bootstrap, a tela é dividida em 12 colunas. 12 significa largura total.
        # className: Usamos classes CSS. "text-center" centraliza, "mb-4" adiciona margem embaixo.
        dbc.Col(html.H1("Dashboard de Vendas - Oracle Analytics", 
                        className="text-center text-primary mb-4"), width=12)
    ]),

    # --- LINHA 1: INDICADORES PRINCIPAIS ---
    dbc.Row([
        # Coluna da esquerda 
        dbc.Col([
            dbc.Card([ # O Card cria aquela borda/caixa ao redor do gráfico
                dbc.CardHeader("Performance Geral"), # Título da caixa
                dbc.CardBody(dcc.Graph(figure=fig_gauge, style={"height": "470px"})) # Onde o gráfico vive
            ])
        ], width=4),
        
      
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Distribuição de Vendas por Loja"),
                dbc.CardBody(dcc.Graph(figure=fig_pizza, style={"height": "600px"}))
            ])
        ], width=8), 
    ], className="mb-4"), 

    # --- LINHA 3: RANKING E EVOLUÇÃO ---
    dbc.Row([
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Ranking de Lojas"),
                dbc.CardBody(dcc.Graph(figure=fig_barras))
            ])
        ], width=6),
        
        # Lado direito da Evolução 
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Evolução Temporal"),
                dbc.CardBody(dcc.Graph(figure=fig_linha))
            ])
        ], width=6),
    ])

], fluid=True, className="p-4") 

if __name__ == "__main__":
    app.run(debug=True)