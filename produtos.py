import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import matplotlib.ticker as mtick

# --- 2. CONFIGURAÇÕES ---
USUARIO_DB = 'system'
SENHA_DB = '1234' 
SERVIDOR_DB = 'xe'
STRING_CONEXAO = f'oracle+oracledb://{USUARIO_DB}:{SENHA_DB}@localhost:1521/{SERVIDOR_DB}'

# Query SQL para obter os dados dos alunos
query_sql = """
    SELECT
    nome_produto as "Produto",
    preco as "Preço",
    quantidade as "Quantidade",
    (preco * quantidade) as "Total Vendas"  
    FROM produtos
"""

# --- 3. FUNÇÕES DE LÓGICA ---
def carregar_dados_do_banco(engine, query):
    """Conecta ao banco, executa a query e retorna um DataFrame."""
    print("Conectando ao banco...")
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        print("Conectado! Dados carregados.")
        return df
    except Exception as e:
        print(f"\nERRO AO CONECTAR: {e}\nPor favor, verifique sua senha e a query.")
        return pd.DataFrame()



    
def gerar_relatorio_grafico(df):
    """Gera um gráfico de barras com os dados fornecidos."""
    
    if df.empty:
        print("O DataFrame está vazio. Nenhum gráfico para gerar.")
        print("Verifique se seu script SQL (no SQL Developer) rodou com sucesso.")
        return

    print("Gerando gráfico...")
    plt.figure(figsize=(10, 6))
    df_sorted = df.sort_values('Total Vendas', ascending=False)

    barplot = sns.barplot(
        data =df_sorted,
        x="Produto",
        y="Total Vendas",
        color = "#3498db"  
        )
    # Adicionar rótulos de dados formatados como R$
    for p in barplot.patches:
        valor = p.get_height()
        barplot.annotate(
            f'R$ {valor:,.2f}',  
            (p.get_x() + p.get_width() / 2., valor),
            ha='center', va='center',
            xytext=(0, 9),
            textcoords='offset points'
        ) 
    sns.despine(left=True , top =True, right =True)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
 
    plt.xlabel("Produtos", fontsize=12)
    plt.ylabel("Valor Total em Estoque (R$)", fontsize=12)
    plt.title("Relatório de Valor Total (R$) em Estoque", fontsize=16, fontweight='bold', pad=20)


    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R$ {x:,.0f}'))

    
    plt.tight_layout() 
    
  
    plt.show()


if __name__ == "__main__":
    
    engine = create_engine(STRING_CONEXAO)
    
    df_produtos = carregar_dados_do_banco(engine, query_sql)
    
    
    gerar_relatorio_grafico(df_produtos)