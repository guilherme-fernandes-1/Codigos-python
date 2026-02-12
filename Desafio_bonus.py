import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import webbrowser
import os
import plotly.io as pio

pio.renderers.default = 'browser'
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
                        'mes_vencimento': str})

df['mes_aquisicao'] = df['mes_aquisicao'].astype(str).apply(corrigir_datas)
df['mes_vencimento'] = df['mes_vencimento'].astype(str).apply(corrigir_datas)
data_focal = pd.to_datetime('2026-01-31')
df['n_meses'] = (df['mes_aquisicao'].dt.year - data_focal.year) * 12 + (df['mes_aquisicao'].dt.month - data_focal.month)

def calcular_vip(row):
    if row['n_meses'] > 0:
        return row['valor_parcela'] / ((1 + row['taxa_mensal']) ** row['n_meses'])
    else:
        return row['valor_parcela']

df['valor_presente'] = df.apply(calcular_vip, axis=1)

bonus_valor = df.groupby('id_convenio').agg({
    'valor_parcela': 'sum',
    'valor_presente': 'sum'
}).reset_index()

bonus_valor['desagio'] = 1 - (bonus_valor['valor_presente'] / bonus_valor['valor_parcela'])

fig = go.Figure()

fig.add_trace(go.Bar(
    x=bonus_valor['id_convenio'].astype(str), 
    y=bonus_valor['valor_parcela'],           
    name='Valor Nominal (Bruto)',               
    marker_color='#1f77b4',                    
    text=bonus_valor['valor_parcela'],        
    textposition='auto',
    texttemplate='R$ %{y:,.2s}'                 
))

fig.update_layout(
    title='<b>Comparativo: Quanto vale a Carteira Hoje? (Ref: Jan/2026)</b>',
    xaxis_title='ID Convênio',
    yaxis_title='Volume Financeiro (R$)',
    barmode='group', 
    plot_bgcolor='white',
    font=dict(family="Arial", size=12),
    yaxis=dict(
        showgrid=True, 
        gridcolor='lightgray',
        tickprefix="R$ ", 
        tickformat=",.2f"
    ),
    hovermode="x unified",
    legend=dict(
        orientation="h", 
        yanchor="bottom", 
        y=1.02, 
        xanchor="right", 
        x=1
    )
)

fig.show()
fig.write_html("comparativo_carteira.html")
webbrowser.open("file://" + os.path.realpath("comparativo_carteira.html"))

print('\n --- Desafio Bônus ---')
print("-" * 60)
bonus_valor['Deságio (%)'] = bonus_valor['desagio'].map("{:.2%}".format)
bonus_valor['Valor Nominal'] = bonus_valor['valor_parcela'].map("R$ {:,.2f}".format)
bonus_valor['Valor Presente'] = bonus_valor['valor_presente'].map("R$ {:,.2f}".format)

print(bonus_valor[['id_convenio', 'Valor Nominal', 'Valor Presente', 'Deságio (%)']])
