import pandas as pd          
import plotly.express as px    
from sqlalchemy import create_engine 
import json                     
from urllib.request import urlopen   
import ssl                     

# --- 1. CONFIGURAÇÕES DE BANCO DE DADOS ---
USUARIO_DB = 'system'
SENHA_DB = '1234' 
SERVIDOR_DB = 'xe'
STRING_CONEXAO = f'oracle+oracledb://{USUARIO_DB}:{SENHA_DB}@localhost:1521/{SERVIDOR_DB}'

QUERY_SQL = """
    SELECT 
        p.nome_produto AS "Produto",
        p.preco AS "Preço Unitário",
        NVL(r.qtd_vendida, 0) AS "Quantidade",
        NVL(r.nome_regiao, 'Sem Venda') AS "Região",
        (p.preco * NVL(r.qtd_vendida, 0)) AS "Total Vendas"
    FROM tb_produtos p
    INNER JOIN regiao r ON p.id_produto = r.id_produto
"""

# --- 3. FUNÇÃO DE EXTRAÇÃO (ETL) ---
def carregar_dados():
    """Conecta ao banco e retorna um DataFrame com os dados."""
    print("⏳ Carregando dados do Oracle...")
    try:
        engine = create_engine(STRING_CONEXAO)
        with engine.connect() as connection:
            df = pd.read_sql(QUERY_SQL, connection)
        print(" Dados carregados com sucesso!")
        return df
    except Exception as e:
        print(f" Erro de conexão: {e}")
        return pd.DataFrame()

# --- 4. GRÁFICO 1: BARRAS (RANKING DE VENDAS) ---
def criar_grafico_barras(df):
    if df.empty:
        return

    print(" Gerando Gráfico de Barras...")

    # Ranking correto por produto
    ranking = (
        df.groupby("Produto", as_index=False)["Total Vendas"]
          .sum()
          .sort_values(by="Total Vendas", ascending=False)
    )

    ordem_produtos = ranking["Produto"].tolist()
    total = ranking["Total Vendas"].sum()

    fig = px.bar(
        df,
        x="Produto",
        y="Total Vendas",
        color="Região",
        category_orders={"Produto": ordem_produtos},
        color_discrete_sequence=px.colors.qualitative.G10,
        title=(
            "<b>Vendas por Produto</b><br>"
            f"<span style='font-size:14px;color:green'>"
            f"Total Geral: R$ {total:,.2f}</span>"
        ),
        text_auto='.2s'
    )

    fig.update_layout(
        template='plotly_white',
        xaxis_tickangle=-45,
        hovermode="x unified",
        bargap=0.1,
        legend=dict(
            title="Localização",
            orientation="v",
            y=1, x=1.02
        )
    )

    fig.update_yaxes(tickprefix='R$ ')
    fig.show()


# --- 5. GRÁFICO 2: PIZZA (DISTRIBUIÇÃO) ---
def criar_grafico_pizza(df):
    print(" Gerando Gráfico de Pizza...")
    
    fig_pie = px.pie(
        df,
        values='Total Vendas',
        names='Região',
        title='<b>Distribuição de Vendas por Região</b>',
        color_discrete_sequence=px.colors.qualitative.G10
    )
    
    # Coloca a porcentagem e o nome dentro da fatia
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(template='plotly_white')
    
    fig_pie.show()

# --- 6. GRÁFICO 3: MAPA (GEOLOCALIZAÇÃO) ---
def gerar_mapageografico(df):
    print(" Gerando Mapa Geográfico...")
    
    # Cria uma cópia para não alterar os dados originais
    df = df.copy() 
    
    # Lógica para extrair a UF: Pega as 2 últimas letras de "São Paulo - SP" -> "SP"
    df['UF'] = df['Região'].apply(lambda x: x[-2:] if isinstance(x, str) and '-' in x else 'NA')
    
    # Agrupa os dados somando por Estado
    df_mapa = df.groupby('UF')[['Total Vendas']].sum().reset_index()

    # Link oficial com o desenho dos estados brasileiros
    url_geojson = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
    
    try:
        # Hack para evitar erro de certificado SSL ao baixar o mapa
        contexto_ssl = ssl._create_unverified_context()
        
        with urlopen(url_geojson, context=contexto_ssl) as response:
            brazil_states = json.load(response)
            
    except Exception as e:
        print(f"Erro ao baixar mapa: {e}")
        return

    if df_mapa.empty:
        print("Sem dados válidos de UF.")
        return

    # Criação do Mapa de Calor (Choropleth)
    fig = px.choropleth(
        df_mapa,
        geojson=brazil_states,
        locations='UF',
        featureidkey='properties.sigla', # Chave que liga o Excel ao GeoJSON
        color='Total Vendas',
        color_continuous_scale="Reds",   # Escala de cor (Vermelhos)
        title='<b>Vendas por Estado (Mapa de Calor)</b>'
    )

    # Foca o mapa apenas onde tem dados (Brasil) e esconde o resto do mundo
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title_x=0.5, margin={"r":0,"t":30,"l":0,"b":0})
    fig.show()

if __name__ == "__main__":  
    df_produtos = carregar_dados()

    if not df_produtos.empty:
        criar_grafico_barras(df_produtos)
        criar_grafico_pizza(df_produtos)
        gerar_mapageografico(df_produtos)