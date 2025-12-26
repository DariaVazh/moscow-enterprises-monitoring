import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, State, callback
import SQLLL

import sqlite3
conn = sqlite3.connect('organizations.db')

# df_map = pd.DataFrame({
#     "ISO": ["DEU", "CHN", "IND", "KAZ", "USA", "DEU", "CHN"],
#     "Страна": ["Германия", "Китай", "Индия", "Казахстан", "США", "Германия", "Китай"],
#     "Отрасль": ["Пищевая", "Пищевая", "Пищевая", "Машиностроение", "Машиностроение", "Химическая", "Химическая"]
# # })

df_map = SQLLL.get_export_countries_set(conn)
moscow_lat, moscow_lon = 55.7558, 37.6173

layout = html.Div([
    html.H2("Страны, куда экспортируют товары из Москвы", style={'textAlign': 'center'}),

    html.Label("Выберите отрасль:"),
    dcc.Dropdown(
        id='industry-selector-map',
        options=[{"label": ind, "value": ind} for ind in df_map['Отрасль'].unique()],
        value=df_map['Отрасль'].unique()[0],
        clearable=False
    ),

    html.Button("Показать страны", id='show-btn-map', n_clicks=0, style={'marginTop': '10px'}),
    dcc.Graph(id='map-graph'),

    html.Hr(style={'margin': '40px 0'}),


])

@callback(
    Output('map-graph', 'figure'),
    Input('show-btn-map', 'n_clicks'),
    State('industry-selector-map', 'value')
)
def update_map(n_clicks, selected_industry):
    df_filtered = df_map[df_map['Отрасль'] == selected_industry]

    fig = px.scatter_geo(
        df_filtered,
        locations="ISO",
        hover_name="Страна",
        projection="natural earth",
        title=f"Страны, куда экспортирует {selected_industry} промышленность из Москвы"
    )

    fig.add_trace(go.Scattergeo(
        lat=[moscow_lat],
        lon=[moscow_lon],
        text=["Москва"],
        hoverinfo="text",
        mode="markers",
        marker=dict(size=12, color="blue"),
        name="Москва"
    ))

    fig.update_traces(marker=dict(size=12, color="red"))
    return fig
