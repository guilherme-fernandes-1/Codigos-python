import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

# --- 2. CONFIGURAÇÃO GLOBAL ---
# Todas as nossas "variáveis" e constantes ficam aqui em cima.

# Configurações do Gráfico e Regras
NOTA_DE_CORTE = 6.0
PALETA_CORES = {'Aprovado': '#2ecc71', 'Reprovado': '#e74c3c'}

# Configurações do Banco de Dados
USUARIO_DB = 'system'
SENHA_DB = '1234'
SERVIDOR_DB = 'xe'
STRING_CONEXAO = f'oracle+oracledb://{USUARIO_DB}:{SENHA_DB}@localhost:1521/{SERVIDOR_DB}'

# Query SQL para obter os dados dos alunos
QUERY_DADOS_ALUNOS = f"""
    SELECT 
        nome_aluno AS "Estudante",
        ROUND((nota_p1 + nota_p2) / 2, 2) AS "Media Final",
        CASE 
            WHEN (nota_p1 + nota_p2) / 2 >= {NOTA_DE_CORTE} THEN 'Aprovado'
            ELSE 'Reprovado'
        END AS "Status"
    FROM 
        tabela_alunos
"""

# --- 3. FUNÇÕES DE LÓGICA ---

def carregar_dados_do_banco(engine, query):
    """Conecta ao banco, executa a query e retorna um DataFrame."""
    print("Conectando ao banco de dados...")
    try:
        df = pd.read_sql(query, engine)
        print("Dados carregados com sucesso do Oracle!")
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"ERRO AO CARREGAR DADOS DO BANCO: {e}")
        print("Verifique string de conexão, query SQL e se a tabela 'tabela_alunos' existe.")
        return None  # Retorna None em caso de falha

def analisar_dados(df):
    """Calcula e imprime as estatísticas descritivas da turma."""
    if df is None or df.empty:
        print("Nenhum dado para analisar.")
        return

    print("\n--- Estatísticas da Turma ---")
    media_geral = df['Media Final'].mean()
    taxa_aprov = df['Status'].value_counts(normalize=True).get('Aprovado', 0) * 100
    melhor_aluno = df.loc[df['Media Final'].idxmax()]

    print(f"Média geral da turma: {media_geral:.2f}")
    print(f"Taxa de aprovação: {taxa_aprov:.1f}%")
    print(f"Melhor desempenho: {melhor_aluno['Estudante']} (Média: {melhor_aluno['Media Final']})")

def criar_visualizacao(df, nota_corte):
    """Gera e exibe o gráfico de barras com os resultados."""
    if df is None or df.empty:
        print("Nenhum dado para visualizar.")
        return

    print("Gerando gráfico...")
    plt.figure(figsize=(10, 6))  # Define um tamanho melhor para o gráfico

    # Gráfico de barras
    barplot = sns.barplot(
        data=df.sort_values('Media Final', ascending=False),
        x='Estudante',
        y='Media Final',
        hue='Status',
        palette=PALETA_CORES
    )

    # Linha de corte
    plt.axhline(y=nota_corte, color='red', linestyle='--', label=f'Nota de Corte ({nota_corte})')

    # Rótulos de dados (os valores em cima das barras)
    for p in barplot.patches:
        barplot.annotate(
            f'{p.get_height():.2f}',
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center',
            xytext=(0, 9),
            textcoords='offset points'
        )

  
    plt.xlabel("Estudantes")
    plt.ylabel("Médias Finais")
    plt.title("Relatório de Médias dos Estudantes")
    plt.ylim(0, 10.5)
    plt.legend(title="Status")
    plt.tight_layout() 
    
    
    plt.show()

# --- 4. EXECUÇÃO PRINCIPAL ---
# O padrão "if __name__ == '__main__':" é a forma correta de
# organizar um script Python para que ele seja executável.

def main():
    """Função principal que orquestra o pipeline."""
    # 1. Cria a "ponte" de conexão
    engine = create_engine(STRING_CONEXAO)
    
    # 2. Carrega os dados
    df_turma = carregar_dados_do_banco(engine, QUERY_DADOS_ALUNOS)
    
    # 3. Continua só se os dados foram carregados com sucesso
    if df_turma is not None:
        # 4. Analisa os dados (imprime estatísticas)
        analisar_dados(df_turma)
        
        # 5. Cria a visualização
        criar_visualizacao(df_turma, NOTA_DE_CORTE)

if __name__ == "__main__":
    main()