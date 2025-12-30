import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import matplotlib.ticker as mtick

# --- 1. CONFIGURAÇÕES ---
USUARIO_DB = 'system'
SENHA_DB = '1234' 
SERVIDOR_DB = 'xe' 
STRING_CONEXAO = f'oracle+oracledb://{USUARIO_DB}:{SENHA_DB}@localhost:1521/{SERVIDOR_DB}'

query_sql = """
    SELECT 
    nome_produto as "Produto", 
    preco as "Preço", 
    quantidade as "Quantidade", 
    (preco * quantidade) as "Total Vendas"  
    FROM produtos
"""

# --- 2. FUNÇÕES DE LÓGICA ---
def carregar_dados_do_banco(engine, query):
    print("Conectando ao banco...")
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        print("Conectado! Dados carregados.")
        return df
    except Exception as e:
        print(f"\nERRO AO CONECTAR: {e}\nPor favor, verifique sua senha e a query.")
        return pd.DataFrame()

    
def gerar_dashboard_grafico(df):
    
    if df.empty:
        print("O DataFrame está vazio.")
        return

    print("Gerando dashboard...")
    
    # 1. CÁLCULO DE MÉTRICAS (KPIs)
    df_sorted = df.sort_values('Total Vendas', ascending=False)
    
    total_geral = df_sorted['Total Vendas'].sum()
    media_vendas = df_sorted['Total Vendas'].mean()
    
    # Pega o produto que mais vendeu (primeira linha após ordenar)
    produto_campeao = df_sorted.iloc[0]['Produto']
    valor_maximo = df_sorted.iloc[0]['Total Vendas']

    # --- INÍCIO DA PLOTAGEM ---
    # Aumentamos a altura da figura para caber o cabeçalho
    plt.figure(figsize=(13, 8)) 

    # 2. CRIAÇÃO DO GRÁFICO DE BARRAS
    barplot = sns.barplot(
        data=df_sorted,
        x="Produto",
        y="Total Vendas",
        color="#e6841e" 
    )

    # 3. ANOTAÇÕES NAS BARRAS
    for p in barplot.patches:
        valor = p.get_height()
        if valor > 0:
            barplot.annotate(
                f'R$ {valor:,.2f}',  
                (p.get_x() + p.get_width() / 2., valor),
                ha='center', va='center',
                xytext=(0, 9),
                textcoords='offset points',
                fontsize=9,
                fontweight='bold',
                color='#333333'
            ) 

    # 4. DESIGN DO "DASHBOARD" (CABEÇALHO)
    # Vamos escrever as métricas no topo do gráfico usando coordenadas relativas
    # y=1.02 significa "um pouco acima do topo do gráfico"
    
    # KPI 1: Faturamento Total
    plt.text(0, 1.12, "Faturamento Total", transform=plt.gca().transAxes, fontsize=10, color='gray')
    plt.text(0, 1.07, f"R$ {total_geral:,.2f}", transform=plt.gca().transAxes, fontsize=16, fontweight='bold', color='#2E8B57') # Verde

    # KPI 2: Produto Campeão (O que você pediu)
    plt.text(0.35, 1.12, "Produto Mais Vendido (Máx)", transform=plt.gca().transAxes, fontsize=10, color='gray')
    plt.text(0.35, 1.07, f"{produto_campeao}", transform=plt.gca().transAxes, fontsize=16, fontweight='bold', color='#e6841e') # Laranja
    plt.text(0.35, 1.03, f"(R$ {valor_maximo:,.2f})", transform=plt.gca().transAxes, fontsize=10, color='#e6841e')

    # KPI 3: Média de Vendas
    plt.text(0.75, 1.12, "Média por Produto", transform=plt.gca().transAxes, fontsize=10, color='gray')
    plt.text(0.75, 1.07, f"R$ {media_vendas:,.2f}", transform=plt.gca().transAxes, fontsize=16, fontweight='bold', color='#4682B4') # Azul

    # Linha divisória estética entre o Dashboard e o Gráfico
    plt.axhline(y=valor_maximo * 1.15, color='gray', linewidth=1, alpha=0.3, clip_on=False)

    # 5. ESTILIZAÇÃO GERAL
    sns.despine(left=True, top=True, right=True)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.xlabel("Produtos", fontsize=11, fontweight='bold', labelpad=15)
    plt.ylabel("Receita (R$)", fontsize=11, fontweight='bold')
    
    # Título Principal (movido para cima para não bater nos KPIs)
    plt.title("Relatório Analítico de Vendas", fontsize=20, fontweight='bold', y=1.25, color='#333333')
    
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R$ {x:,.0f}'))
    
    plt.xticks(rotation=45, ha='right')

    # Ajuste de margens para que o cabeçalho não seja cortado
    plt.subplots_adjust(top=0.80, bottom=0.20) 

    plt.show()

# --- 3. EXECUÇÃO ---
if __name__ == "__main__":
    engine = create_engine(STRING_CONEXAO)
    df_produtos = carregar_dados_do_banco(engine, query_sql)
    gerar_dashboard_grafico(df_produtos)