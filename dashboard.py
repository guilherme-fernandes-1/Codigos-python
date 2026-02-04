import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import os
import json
from urllib.request import urlopen
import ssl
import oracledb

IP_DESTINO = '192.168.100.61'
USUARIO_DB = 'system'
SENHA_DB = '1234'
SERVIDOR_DB = 'xe'
STRING_CONEXAO = (
    "oracle+oracledb://system:1234@localhost:1521/?service_name=xe"
)
DNS = f"{USUARIO_DB}:{SENHA_DB}@{IP_DESTINO}:1521/?service_name={SERVIDOR_DB}"

try:
    conn = oracledb.connect(DNS)
    print("Conexão bem-sucedida ao banco de dados Oracle.")
    query = "SELECT * FROM fPreco" 
    df = pd.read_sql(query, conn)

    print(df.head()) 
    
except Exception as e:
    print(f"Erro ao conectar: {e}")

QUERY_SQL = """
SELECT 
lc.NOME AS CLIENTE,
lp.NOME AS PRODUTO,
lf.NOME AS FORNECEDOR,
lm.NOME AS MARCA,
la.NOME AS CATEGORIA,
lc.CIDADE AS CIDADE,
lv.VALOR_TOTAL AS FATURAMENTO,
TO_CHAR(lv.DATA_VENDA, 'YYYY') AS ANO
FROM LOJA_CLIENTES lc
JOIN LOJA_VENDAS lv ON lc.ID = lv.ID_CLIENTE      
JOIN LOJA_ITENS li  ON lv.ID = li.ID_VENDA        
JOIN LOJA_PRODUTOS lp  ON li.ID_PRODUTO = lp.ID      
JOIN LOJA_FORNECEDORES lf ON lp.ID_FORN = lf.ID         
JOIN LOJA_MARCAS lm  ON lp.ID_MARCA = lm.ID        
JOIN LOJA_CATEGORIAS la ON lp.ID_CAT = la.ID  
"""

def carregar_dados():
    try:
        engine = create_engine(STRING_CONEXAO)
        with engine.connect() as connection:
            df = pd.read_sql(QUERY_SQL, connection)
        
        if df.empty:
            print("AVISO: A consulta retornou 0 registros.")
            return df

        df.columns = [c.upper() for c in df.columns]

        if 'ANO' in df.columns:
            df['ANO'] = pd.to_datetime(df['ANO'], format='%Y')
        else:
            print(f"ERRO: Coluna 'ANO' não encontrada. Colunas disponíveis: {df.columns.tolist()}")
            
        return df
    except Exception as e:
        print(f"ERRO AO CONECTAR OU EXECUTAR SQL: {e}")
        return pd.DataFrame()



df = carregar_dados()
if not df.empty:
    total_vendas = df.shape[0] 
    total_faturamento = df['FATURAMENTO'].sum()
    ticket_medio = total_faturamento / total_vendas
else:
    total_vendas = 0
    total_faturamento = 0
    ticket_medio = 0


def formatar_valor(valor):
    if valor >= 1000000:
        return f"R$ {valor/1000000:,.2f}M"
    elif valor >= 1000:
        return f"R$ {valor/1000:,.1f}k"
    else:
        return f"R$ {valor:,.2f}"
print(df.head())
print(df.columns)
df['UF'] = df['CIDADE'].str[-2:]

url_geojson = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
try:
    contexto_ssl = ssl._create_unverified_context()
    with urlopen(url_geojson, context=contexto_ssl) as response:
        brazil_states = json.load(response)
except Exception as e:
    print(f"Erro ao baixar mapa: {e}")
    brazil_states = None


fig_barras = px.bar(
    df.groupby('FORNECEDOR')['FATURAMENTO'].sum().reset_index(),
    x='FORNECEDOR', y='FATURAMENTO',
    title= None,
    template='plotly_dark',
    color='FORNECEDOR',
    text_auto='.2s',
    category_orders={'FORNECEDOR': df.groupby('FORNECEDOR')['FATURAMENTO'].sum().sort_values(ascending=False).index.tolist()}
)
fig_barras.update_traces(
    texttemplate='<b>%{y:.2s}</b>',
    textposition='outside'
)

fig_barras.update_layout(
    xaxis_title='FORNECEDOR',
    template='plotly_dark',
    xaxis_tickangle=-45,
    yaxis_title='FATURAMENTO',
    legend_title='NOME_FORNECEDOR',
    title_x=0.5,
    yaxis=dict(
        showgrid=True,
        griddash='dash',
        gridcolor='rgba(255, 255, 255, 0.2)',
        gridwidth=1
        
    ),
    
    font=dict(
        family="Arial, sans-serif",
        size=15,
        color="white"
       
    )
)

fig_linhas = px.line(
    df.groupby(['ANO', 'CATEGORIA'])['FATURAMENTO'].sum().reset_index(),
    x='ANO', y='FATURAMENTO', color='CATEGORIA', 
    title=None,
    template='plotly_dark',
    markers=True
)
fig_linhas.update_layout(
    xaxis_title='ANO',
    yaxis_title='FATURAMENTO',
    legend_title='CATEGORIA',
    title_x=0.5,
    font=dict(
        family="Arial, sans-serif",
        size=15,
        color="white"
    )
)

fig_sunburst = px.sunburst(
    df,
    path=['CATEGORIA', 'PRODUTO'],
    values='FATURAMENTO',
    color='FATURAMENTO',
    color_continuous_scale='RdBu',
    title= None,
    template='plotly_dark'
)
fig_sunburst.update_layout(
    legend_title='CATEGORIA',
    uniformtext=dict(minsize=10, mode='hide'),
    title_x=0.5,
    font=dict(
        family="Arial, sans-serif",
        size=15,
        color="white",

    ),
    coloraxis_colorbar=dict(
        title="FATURAMENTO",
        tickformat=".2s",
        title_side="top",
        tickprefix="<b>",
        ticksuffix="</b>",
        x=1,
        xanchor="right",
        xpad=0,
        thickness=20,
        len=0.8,
        yanchor="middle",
        y=0.5            
    )
)
fig_sunburst.update_traces(
    textinfo='label',
    texttemplate='<b>%{label}</b>'
)


fig_mapa = px.choropleth(
    df.groupby('UF')['FATURAMENTO'].sum().reset_index(),
    geojson=brazil_states,
    locations='UF',
    featureidkey='properties.sigla',
    color='FATURAMENTO',
    color_continuous_scale="Reds",
    template="plotly_dark",
    title= None
)
fig_mapa.update_traces(marker_line_width=0.5, marker_line_color='black')
fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_layout(
    title_x=0.5,
    font=dict(
        size=15, 
        color="white", 
        family="Arial, sans-serif"
        ),
    coloraxis_colorbar=dict(
        title="FATURAMENTO",
        tickformat=".2s",
        title_side="top",
        tickprefix="<b>",
        ticksuffix="</b>",
        x=1,
        xanchor="right",
        xpad=0,
        thickness=20,
        len=0.8,
        yanchor="middle",
        y=0.5            
    ))


app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col(html.H1("Análise de Vendas", className="text-center", style={'color': 'white'}), width=14)
    ]),

    
    dbc.Row([
        
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Faturamento Total", className="text-center"),
                dbc.CardBody(
                    html.H3(formatar_valor(total_faturamento), className="text-center text-success")
                )
            ], color="dark", outline=True), 
            width=4 
        ),

      
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Total de Vendas", className="text-center"),
                dbc.CardBody(
                    html.H3(f"{total_vendas}", className="text-center text-info")
                )
            ], color="dark", outline=True),
            width=4
        ),

      
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Ticket Médio", className="text-center"),
                dbc.CardBody(
                    html.H3(formatar_valor(ticket_medio), className="text-center text-warning")
                )
            ], color="dark", outline=True),
            width=4
        )
    ], className="mb-4"),


    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Faturamento por Fornecedor'), class_name='text-white m-0'),
                dbc.CardBody(dcc.Graph(figure=fig_barras, style={'height': '550px'}))
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Evolução do Faturamento ao Longo dos Anos'), class_name='text-white m-0'),
                dbc.CardBody(dcc.Graph(figure=fig_linhas, style={'height': '550px'}))
            ])
        ], width=6, className="mb-4")
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Faturamento por Categoria'), class_name='text-white m-0'),
                dbc.CardBody(dcc.Graph(figure=fig_sunburst, style={'height': '780px'}))
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4('Vendas por Estado'), class_name='text-white m-0'),
                dbc.CardBody(dcc.Graph(figure=fig_mapa, style={'height': '780px'}))
            ])
        ], width=6)
    ])
], fluid=True, className="p-4")

if __name__ == "__main__":
    app.run(debug=True)
