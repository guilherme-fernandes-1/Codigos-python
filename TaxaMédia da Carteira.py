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
            return pd.NaT

df = pd.read_csv('carteira.csv', sep=';', decimal='.', encoding='utf-8', 
                 dtype={'mes_aquisicao': str, 'valor_pago': float, 'id_convenio': str, 
                        'valor_parcela': float, 'valor_aquisicao_parcela': float, 'taxa_mensal': float})

df['mes_aquisicao'] = df['mes_aquisicao'].astype(str).apply(corrigir_datas)

# 2. Agrupamento e Cálculo (MANTIDO IGUAL - MATEMÁTICA CORRETA)
df['peso_taxa'] = df['taxa_mensal'] * df['valor_aquisicao_parcela']
etapa_2 = df.groupby([df['mes_aquisicao'], 'id_convenio']).agg({
    'valor_aquisicao_parcela': 'sum',
    'peso_taxa': 'sum'
}).reset_index()

etapa_2['taxa_ponderada'] = etapa_2['peso_taxa'] / etapa_2['valor_aquisicao_parcela']

etapa_2 = etapa_2.sort_values('mes_aquisicao')
etapa_2['mes_aquisicao'] = etapa_2['mes_aquisicao'].astype(str)

# --- 3. Plotagem ---

fig = px.line(etapa_2, 
             x='mes_aquisicao', 
             y='taxa_ponderada', 
             color='id_convenio',
             markers=True, 
             title='<b>Evolução da Taxa Média Ponderada (Safra)</b>', 
             labels={
                 'mes_aquisicao': 'Mês de Aquisição', 
                 'taxa_ponderada': 'Taxa Mensal', 
                 'id_convenio': 'Convênio'
             }, 
             color_discrete_sequence=px.colors.qualitative.G10 
            )

fig.update_layout(
    plot_bgcolor='white', 
    font=dict(family="Arial", size=12),
    xaxis=dict(showgrid=False),
    yaxis=dict(
        showgrid=True, 
        gridcolor='lightgray',
        tickformat=".2%"  
        
    ),
    hovermode="x unified" 
)

fig.update_traces(
    hovertemplate='<b>%{y:.4%}</b><extra></extra>'
)

fig.show()
print('--- Taxa Média Ponderada ---')
tabela_visual = etapa_2[['mes_aquisicao', 'id_convenio', 'taxa_ponderada']].copy()
tabela_visual.columns = ['Mês (Safra)', 'Convênio', 'Taxa Média']
tabela_visual['Taxa Média'] = tabela_visual['Taxa Média'].map("{:.4%}".format)
tabela_pivot = tabela_visual.pivot(index='Mês (Safra)', columns='Convênio', values='Taxa Média')

print(tabela_pivot.fillna('-')) 
print('-' * 60)
