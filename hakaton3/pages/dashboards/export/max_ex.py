import pandas as pd
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import SQLLL
import sqlite3
conn = sqlite3.connect('organizations.db')



df_pie = SQLLL.get_top5_export_countries_count(conn)

layout = html.Div([
    html.H2("Топ компаний по отрасли и году", style={'textAlign': 'center'}),

    html.Label("Выберите год:"),
    dcc.Dropdown(
        id='year-selector-pie',
        options=[{'label': y, 'value': y} for y in sorted(df_pie['Год'].unique())],
        value=df_pie['Год'].min(),
        clearable=False
    ),

    html.Label("Выберите отрасль:"),
    dcc.Dropdown(
        id='industry-selector-pie',
        options=[{'label': i, 'value': i} for i in df_pie['Отрасль'].unique()],
        value=df_pie['Отрасль'].unique()[0],
        clearable=False
    ),

    html.Button("Показать топ компаний", id='show-btn-pie', n_clicks=0, style={'marginTop': '10px'}),
    dcc.Graph(id='pie-chart')  # Этот ID должен совпадать с Output
])

@callback(
    Output('pie-chart', 'figure'),  # Изменил на 'pie-chart' чтобы совпадало с layout
    Input('show-btn-pie', 'n_clicks'),
    State('year-selector-pie', 'value'),
    State('industry-selector-pie', 'value')
)
def update_pie(n_clicks, selected_year, selected_industry):
    df_filtered = df_pie[(df_pie['Год'] == selected_year) & (df_pie['Отрасль'] == selected_industry)]
    df_top = df_filtered.sort_values('Объем', ascending=False).head(5)
    if df_top.empty:
        return go.Figure().update_layout(title="Нет данных для выбранного года и отрасли")
    fig = go.Figure(go.Pie(
        labels=df_top['Компания'],
        values=df_top['Объем'],
        hole=0.4,
        marker=dict(line=dict(color='white', width=2))
    ))
    fig.update_layout(title=f"Топ компаний по объему экспорта ({selected_industry}, {selected_year})")
    return fig
