from dash import html, callback, Output, Input, dcc
import pandas as pd
import plotly.express as px
import numpy as np
import SQLLL
import sqlite3
conn = sqlite3.connect('organizations.db')

# df_eco = pd.DataFrame({
#     "Компания": ["ЦАО", "САО", "СВАО", "ЮАО", "ЗАО", "ВАО"] * 6,
#     "Год": [2017] * 6 + [2018] * 6 + [2019] * 6 + [2020] * 6 + [2021] * 6 + [2022] * 6,
#     "Эко_оборудование": [
#         0, 0, 1, 0, 0, 0,
#         1, 0, 1, 0, 1, 0,
#         1, 1, 1, 0, 1, 1,
#         1, 1, 1, 1, 1, 1,
#         1, 1, 1, 1, 1, 1,
#         1, 1, 1, 1, 1, 1
#     ]
# })

df_eco = SQLLL.ecology(conn)

np.random.seed(42)
companies = [f"Компания_{i}" for i in range(1, 26)]
lats = 55.70 + np.random.rand(25) * 0.1
lons = 37.60 + np.random.rand(25) * 0.1
pollution_level = np.random.randint(1, 6, size=25)
df_pollution = pd.DataFrame({
    "Компания": companies,
    "lat": lats,
    "lon": lons,
    "Уровень_загрязнения": pollution_level
})

layout = html.Div([
    html.H1("Экологическая ситуация в Москве",
            style={'textAlign': 'center', 'color': '#2E86AB', 'fontFamily': 'Arial', 'marginBottom': '40px'}),
    html.Div([
        html.H2("Уровень промышленных выбросов в Москве",
                style={'textAlign': 'center', 'color': '#E74C3C', 'fontFamily': 'Arial', 'marginBottom': '20px'}),
        dcc.Graph(id='pollution-map')
    ], style={'marginBottom': '50px', 'padding': '20px', 'backgroundColor': '#F7FBFC', 'borderRadius': '10px'}),
    html.Div([
        html.H2("Количество компаний с экологическим оборудованием (2017-2022)",
                style={'textAlign': 'center', 'color': '#27AE60', 'fontFamily': 'Arial', 'marginBottom': '20px'}),
        dcc.Graph(id='eco-equipment-graph')
    ], style={'padding': '20px', 'backgroundColor': '#F7FBFC', 'borderRadius': '10px'})
])

@callback(
    Output('pollution-map', 'figure'),
    Input('pollution-map', 'id')
)
def update_map(_):
    fig = px.scatter_map(
        df_pollution,
        lat="lat",
        lon="lon",
        size="Уровень_загрязнения",
        color="Уровень_загрязнения",
        hover_name="Компания",
        hover_data={"lat": False, "lon": False, "Уровень_загрязнения": True},
        color_continuous_scale=px.colors.sequential.OrRd,
        size_max=25,
        zoom=10,
        height=500,
        title="Уровень промышленных выбросов в атмосферу и водоемы",
        opacity=0.8
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title=dict(x=0.5, font=dict(size=16))
    )

    return fig
@callback(
    Output('eco-equipment-graph', 'figure'),
    Input('eco-equipment-graph', 'id')
)
def update_eco_graph(_):
    # grouped = df_eco.groupby('Год', as_index=False)['Эко_оборудование'].sum()

    fig = px.bar(
        df_eco,
        x='Год',
        y="Количество организаций",
        text="Количество организаций",
        labels={'Эко_оборудование': "Количество организаций"},
        title="Рост количества компаний с экологическим оборудованием (2017-2022)",
        color="Количество организаций",
        color_continuous_scale=px.colors.sequential.Tealgrn
    )

    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        marker_line_color='darkgreen',
        marker_line_width=1
    )

    fig.update_layout(
        plot_bgcolor='#FFFFFF',paper_bgcolor='#F7FBFC',
        font=dict(family="Arial", size=14, color="#34495E"),
        title=dict(x=0.5, font=dict(size=18)),
        xaxis=dict(title="Год", tickmode='linear'), yaxis=dict(title="Количество компаний", range=[0, df_eco["Количество организаций"].max() + 1]))

    return fig
