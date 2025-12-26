import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output, State
import SQLLL
import sqlite3

conn = sqlite3.connect('organizations.db')
# data = {
#     "Год": [2017] * 5 + [2018] * 5 + [2019] * 5 + [2020] * 5 + [2021] * 5 + [2022] * 5,
#     "Компания": ["ЦАО", "САО", "СВАО", "ЮАО", "ЗАО"] * 6,
#     "Инвестиции_тыс_руб": [
#         500000, 300000, 200000, 400000, 600000,
#         550000, 320000, 220000, 450000, 650000,
#         600000, 350000, 250000, 500000, 700000,
#         650000, 380000, 280000, 550000, 750000,
#         700000, 400000, 300000, 600000, 800000,
#         750000, 420000, 320000, 650000, 850000
#     ]
# }
# df = pd.DataFrame(data)
df = SQLLL.get_top5_investors_moscow(conn)
data_1 = {
    "Год": [2017] * 6 + [2018] * 6 + [2019] * 6 + [2020] * 6 + [2021] * 6 + [2022] * 6,
    "Компания": ["ЦАО", "САО", "СВАО", "ЮАО", "ЗАО", "ВАО"] * 6,
    "Отрасль": ["Пищевая", "Машиностроение", "Химическая", "Пищевая", "Машиностроение", "Химическая"] * 6,
    "Инвестиции_тыс_руб": [
        # 2017
        500000, 300000, 200000, 400000, 600000, 350000,
        # 2018
        550000, 320000, 220000, 450000, 650000, 380000,
        # 2019
        600000, 350000, 250000, 500000, 700000, 400000,
        # 2020
        650000, 380000, 280000, 550000, 750000, 420000,
        # 2021
        700000, 400000, 300000, 600000, 800000, 450000,
        # 2022
        750000, 420000, 320000, 650000, 850000, 480000
    ]
}
df_1 = pd.DataFrame(data_1)

# Создаем layout
layout = html.Div([
    html.H1("Инвестиции в промышленность Москвы", style={'textAlign': 'center'}),

    # Первая диаграмма - по компаниям
    html.H2("Инвестиции по компаниям", style={'textAlign': 'center', 'marginTop': '40px'}),
    html.Div([
        html.Label("Выберите год:"),
        dcc.Dropdown(
            id='investments-year-selector',
            options=[{'label': str(year), 'value': year} for year in sorted(df['Год'].unique())],
            value=df['Год'].max(),
            clearable=False
        ),
    ], style={'marginBottom': '20px'}),
    dcc.Graph(id='investments-company-chart'),

    html.Hr(style={'margin': '40px 0'}),

    # Вторая диаграмма - по отраслям
    html.H2("Инвестиции по отраслям", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Выберите год:"),
        dcc.Dropdown(
            id='investments-year-dropdown',
            options=[{'label': str(year), 'value': year} for year in sorted(df_1['Год'].unique())],
            value=df_1['Год'].max(),
            clearable=False
        ),
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Label("Выберите отрасль:"),
        dcc.Dropdown(
            id='investments-sector-dropdown',
            options=[{'label': industry, 'value': industry} for industry in df_1['Отрасль'].unique()],
            value=df_1['Отрасль'].unique()[0],
            clearable=False
        ),
    ], style={'marginBottom': '20px'}),

    html.Button("Показать график", id='investments-display-btn', n_clicks=0,
                style={'marginBottom': '20px'}),

    dcc.Graph(id='investments-industry-chart')
])


# Callback для первой диаграммы (по компаниям)
@callback(
    Output('investments-company-chart', 'figure'),
    Input('investments-year-selector', 'value')
)
def update_investments_by_company(selected_year):
    df_filtered = df[df['Год'] == selected_year]

    if df_filtered.empty:
        return go.Figure().update_layout(
            title="Нет данных для выбранного года",
            annotations=[dict(text="Нет данных", x=0.5, y=0.5, showarrow=False)]
        )

    fig = px.bar(
        df_filtered,
        x='Компания',
        y='Инвестиции_тыс_руб',
        title=f"Инвестиции по компаниям в {selected_year} году",
        labels={'Инвестиции_тыс_руб': 'Инвестиции (тыс. руб)', 'Компания': 'Компания'},
        color='Компания'
    )

    fig.update_layout(
        xaxis_title="Компания",
        yaxis_title="Инвестиции (тыс. руб)",
        showlegend=False
    )

    return fig


# Callback для второй диаграммы (по отраслям)
@callback(
    Output('investments-industry-chart', 'figure'),
    Input('investments-display-btn', 'n_clicks'),
    State('investments-year-dropdown', 'value'),
    State('investments-sector-dropdown', 'value')
)
def update_investments_by_industry(n_clicks, selected_year, selected_industry):
    # Фильтруем данные по году и отрасли
    df_filtered = df_1[(df_1['Год'] == selected_year) & (df_1['Отрасль'] == selected_industry)]

    if df_filtered.empty:
        return go.Figure().update_layout(
            title="Нет данных для выбранных параметров",
            annotations=[dict(text="Нет данных", x=0.5, y=0.5, showarrow=False)]
        )

    # Создаем столбчатую диаграмму
    fig = px.bar(
        df_filtered,
        x='Компания',
        y='Инвестиции_тыс_руб',
        title=f"Инвестиции в {selected_industry} отрасль в {selected_year} году",
        labels={'Инвестиции_тыс_руб': 'Инвестиции (тыс. руб)', 'Компания': 'Компания'},
        color='Компания'
    )

    fig.update_layout(
        xaxis_title="Компания",
        yaxis_title="Инвестиции (тыс. руб)",
        showlegend=True
    )

    return fig