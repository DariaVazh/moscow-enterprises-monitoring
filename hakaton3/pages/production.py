import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import SQLLL
import sqlite3
conn = sqlite3.connect('organizations.db')


# # Тестовые данные
# def generate_production_data():
#     dates = pd.date_range('2024-01-01', '2024-10-01', freq='M')
#     industries = ['Машиностроение', 'Химическая', 'Пищевая', 'Электроника']
#     districts = ['ЦАО', 'ЮАО', 'ЗАО', 'СВАО', 'ЗелАО']
#
#     data = []
#     for date in dates:
#         for industry in industries:
#             for district in districts:
#                 data.append({
#                     'date': date,
#                     'industry': industry,
#                     'district': district,
#                     'production': np.random.randint(1000000, 5000000),
#                     'growth': np.random.uniform(-5, 15)
#                 })
#
#     return pd.DataFrame(data)


df = SQLLL.get_top5_companies_metrics(conn)

layout = html.Div([
    html.H1("🏭 Производство"),

    # Фильтры
    dbc.Row([
        dbc.Col([
            html.Label("Динамика по:"),
            dcc.Dropdown(
                id='production-view-type',
                options=[
                    {'label': 'По отраслям', 'value': 'industry'},
                    {'label': 'По округам', 'value': 'district'},
                    {'label': 'По времени', 'value': 'time'}
                ],
                value='industry'
            )
        ], width=4),
    ], className="mb-4"),

    # Графики
    dbc.Row([
        dbc.Col(dcc.Graph(id='production-main-chart'), width=8),
        dbc.Col([
            dcc.Graph(id='production-pie-chart'),
            html.Div(id='production-stats', className="mt-3")
        ], width=4),
    ]),
])


@callback(
    [Output('production-main-chart', 'figure'),
     Output('production-pie-chart', 'figure'),
     Output('production-stats', 'children')],
    [Input('production-view-type', 'value')]
)
def update_production_charts(view_type):
    if view_type == 'industry':
        # Группируем по отраслям
        industry_data = df.groupby('industry')['production'].sum().reset_index()

        main_fig = px.bar(industry_data, x='industry', y='production',
                          title="Производство по отраслям")

        pie_fig = px.pie(industry_data, values='production', names='industry',
                         title="Доля отраслей")

    elif view_type == 'district':
        # Группируем по округам
        district_data = df.groupby('district')['production'].sum().reset_index()

        main_fig = px.bar(district_data, x='district', y='production',
                          title="Производство по округам")

        pie_fig = px.pie(district_data, values='production', names='district',
                         title="Доля округов")

    else:  # time
        # Группируем по времени
        time_data = df.groupby('date')['production'].sum().reset_index()

        main_fig = px.line(time_data, x='date', y='production',
                           title="Динамика производства")

        pie_fig = px.pie(df.groupby('industry')['production'].sum().reset_index(),
                         values='production', names='industry',
                         title="Доля отраслей")

    # Статистика
    total_production = df['production'].sum()
    avg_growth = df['growth'].mean()

    stats = dbc.Card([
        dbc.CardBody([
            html.H4(f"{total_production:,.0f} ₽", className="text-primary"),
            html.P("Общий объем производства"),
            html.Hr(),
            html.H5(f"{avg_growth:+.1f}%", className="text-success"),
            html.P("Средний рост")
        ])
    ])

    return main_fig, pie_fig, stats