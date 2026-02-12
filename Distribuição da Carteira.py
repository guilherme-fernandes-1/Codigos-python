
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. Carregamento e conversão de datas
def corrigir_datas(valor):
    try:
        return pd.to_datetime(valor, dayfirst=True)
    except:
        try:
            
            return datetime(1899, 12, 30) + timedelta(days=int(valor))
        except:
            return pd.NaT # Retorna NaT para valores inválidos

df = pd.read_csv('carteira.csv', sep=';', decimal='.', encoding='utf-8', dtype={'mes_aquisicao': str, 'valor_pago': float, 'id_convenio': str, 'valor_parcela': float, 'valor_aquisicao_parcela': float})
df['mes_aquisicao'] = df['mes_aquisicao'].astype(str).apply(corrigir_datas)

# 2. Agrupamento por Mês de Aquisição e Convênio
distribuicao = df.groupby([df['mes_aquisicao'], 'id_convenio']).agg({
    'valor_parcela': 'sum',
    'valor_aquisicao_parcela': 'sum'
}).reset_index()

distribuicao['valor_aquisicao_parcela'] = pd.to_numeric(distribuicao['valor_aquisicao_parcela'], errors='coerce')

distribuicao['mes_aquisicao'] = distribuicao['mes_aquisicao'].astype(str)
fig = px.bar(distribuicao, 
             x='mes_aquisicao', 
             y='valor_aquisicao_parcela', 
             color='id_convenio', 
             title='<b>Evolução do Volume de Aquisição por Convênio (Safra)</b>', # Negrito no título
             labels={
                 'mes_aquisicao': 'Mês de Aquisição (Safra)', 
                 'valor_aquisicao_parcela': 'Valor de Aquisição', 
                 'id_convenio': 'ID Convênio'
             },
             color_discrete_sequence=px.colors.qualitative.G10 
            )
# 3. Plotagem
fig.update_layout(
    plot_bgcolor='white', 
    font=dict(family="Arial", size=12),
    xaxis=dict(showgrid=False),
    yaxis=dict(
        showgrid=True, 
        gridcolor='lightgray',
        tickprefix="R$ ",  
        tickformat=",.2f"  
    ),
    hovermode="x unified" 
)


fig.update_traces(
    hovertemplate='<b>%{y:,.2f}</b><extra></extra>'
)

fig.show()

print('\n--- RELATÓRIO: VOLUME DE AQUISIÇÃO POR SAFRA E CONVÊNIO ---')
print('-' * 70)

tabela_visual = distribuicao[['mes_aquisicao', 'id_convenio', 'valor_aquisicao_parcela']].copy()

tabela_pivot = tabela_visual.pivot(index='mes_aquisicao', 
                                   columns='id_convenio', 
                                   values='valor_aquisicao_parcela')

def formatar_moeda(valor):
    if pd.isna(valor):
        return '-'
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

tabela_formatada = tabela_pivot.applymap(formatar_moeda)

print(tabela_formatada)
print('-' * 70)
print(f"VALOR TOTAL DA CARTEIRA: {formatar_moeda(distribuicao['valor_aquisicao_parcela'].sum())}")
print('-' * 70)