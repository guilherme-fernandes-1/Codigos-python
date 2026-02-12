import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import plotly.io as pio

pio.renderers.default = 'browser'

def corrigir_datas(valor):
    if pd.isna(valor) or valor == '':
        return pd.NaT
    try:
        return pd.to_datetime(valor, dayfirst=True)
    except:
        try:
            return datetime(1899, 12, 30) + timedelta(days=int(valor))
        except:
            return pd.NaT

df = pd.read_csv('carteira.csv', sep=';', encoding='utf-8', 
                 dtype={'mes_vencimento': str, 'id_convenio': str, 'mes_aquisicao': str, 
                        'valor_parcela': str, 'valor_pago': str})

cols_financeiras = ['valor_parcela', 'valor_pago']

for col in cols_financeiras:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['mes_vencimento'] = df['mes_vencimento'].apply(corrigir_datas)
df['mes_aquisicao'] = df['mes_aquisicao'].apply(corrigir_datas)

data_focal = pd.to_datetime('2026-01-31')
df_vencido = df[df['mes_vencimento'] < data_focal].copy()

analise_inad = df_vencido.groupby(['id_convenio']).agg({
    'valor_parcela': 'sum', 
    'valor_pago': 'sum'
}).reset_index()

analise_inad['taxa_inadimplencia'] = 1 - (analise_inad['valor_pago'] / analise_inad['valor_parcela'])
analise_inad = analise_inad.sort_values('taxa_inadimplencia', ascending=False)

fig = px.bar(analise_inad, 
             x='id_convenio', 
             y='taxa_inadimplencia', 
             title='Taxa de Inadimplência Cash por Convênio',
             labels={'taxa_inadimplencia': 'Inadimplência (%)', 'id_convenio': 'Convênio'},
             color='taxa_inadimplencia',
             color_continuous_scale='Reds')

fig.update_layout(
    yaxis=dict(tickformat='.2%', title='Inadimplência (%)'),
    plot_bgcolor='white',
    coloraxis_showscale=False
)

fig.update_traces(hovertemplate='Convênio: %{x}<br>Inadimplência: <b>%{y:.2%}</b>')

fig.show()

print("\n--- Inadimplência Cash por Convênio ---")
analise_inad['Inad (%)'] = analise_inad['taxa_inadimplencia'].map("{:.2%}".format)
print(analise_inad[['id_convenio', 'Inad (%)']])