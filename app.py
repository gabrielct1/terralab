# importando
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import json
import os

# conectar ao banco e carregar dados
# Usa variável de ambiente ou localhost (para rodar local ou no Docker)
db_host = os.getenv('DB_HOST', 'localhost')
engine = create_engine(f'postgresql://terralab:senha@{db_host}:5432/terralab')
df = pd.read_sql("SELECT * FROM dados_reais_tratados", engine)
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# carregar o geojson
with open('dags/BR_UF_2024.geojson', 'r') as f:
    geojson_states = json.load(f)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# pontos coloridos por geoapi_id
map_points = px.scatter_mapbox(
    df,
    lat='latitude',
    lon='longitude',
    color='geoapi_id',
    hover_data=['state', 'city', 'geoapi_id'],
    center={'lat': -15.7, 'lon': -47.9},
    zoom=3.5,
    mapbox_style='open-street-map',
    title='Mapa de Pontos por API de Geolocalização'
)

# barras - quantidade de dados por mês
df_month = df.groupby(['month', 'year']).size().reset_index(name='count')
bar_chart_month = px.bar(
    df_month,
    x='month',
    y='count',
    color='year',
    title='Quantidade de Registros por Mês',
    labels={'month': 'Mês', 'count': 'Quantidade', 'year': 'Ano'}
)

# barras — top 3 cidades com mais requisições
df_city = df.groupby('city').size().reset_index(name='count').sort_values(by='count', ascending=False).head(3)

bar_chart_city = px.bar(
    df_city,
    x='city',
    y='count',
    title='Top 3 Cidades com Mais Requisições',
    labels={'city': 'Cidade', 'count': 'Quantidade'}
)

# definição do layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='mapa', figure=map_points)
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar_month', figure=bar_chart_month)
        ], width=6),
        dbc.Col([
            dcc.Graph(id='bar_city', figure=bar_chart_city)
        ], width=6)
    ])
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)