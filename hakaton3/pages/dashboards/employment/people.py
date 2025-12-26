import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output
import sqlite3

import SQLLL

conn = sqlite3.connect('organizations.db')

# data_num_people = {
#     "Год": [2017] * 5 + [2018] * 5 + [2019] * 5 + [2020] * 5 + [2021] * 5 + [2022] * 5,
#     "Компания": ["ЦАО", "САО", "СВАО", "ЮАО", "ЗАО"] * 6,
#     "Кол-во сотрудников": [10000, 20000, 50000, 3000, 4000,
#                            1200, 1080, 7000, 3200, 4100,
#                            10030, 21000, 9000, 3300, 42000,
#                            1000, 2000, 5000, 3000, 30000,
#                            1520, 1805, 7005, 30250, 4150,
#                            1630, 2106, 9600, 3630, 4260],
#     "Отрасль": ["Промышленность", "Торговля", "IT", "Промышленность", "Транспорт"] * 6,
#     "Средняя_зарплата": [50000, 70000, 65000, 40000, 80000] * 6
# }
# df = pd.DataFrame(data_num_people)

df = SQLLL.number_of_staff6(conn)

layout = html.Div([
    html.H1("Динамика занятости по отраслям", className="mb-4"),

    html.Div([
        html.Label("Выберите отрасль:"),
        dcc.Dropdown(
            id='industry-dropdown',
            options=[{'label': i, 'value': i} for i in df['Отрасль'].unique()],
            value=df['Отрасль'].unique()[0],
            clearable=False
        ),
    ], style={'width': '40%', 'margin-bottom': '20px'}),

    dcc.Graph(id='employment-graph'),

    html.Div(id='top-companies-text', style={'margin-top': '20px', 'font-size': '16px'})
])
@callback(
    Output('employment-graph', 'figure'),
    # Output('top-companies-text', 'children'),
    Input('industry-dropdown', 'value')
)
def update_graph(selected_industry):
    filtered_df = df[df['Отрасль'] == selected_industry]
    grouped = filtered_df.groupby('Год', as_index=False)['Кол-во сотрудников'].sum()
    fig = px.bar(
        grouped,
        x='Год',
        y='Кол-во сотрудников',
        text='Кол-во сотрудников',
        title=f"Суммарное количество сотрудников по годам ({selected_industry})",
        color_discrete_sequence=['#2E86AB']
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        xaxis_title="Год",
        yaxis_title="Суммарное количество сотрудников",
        xaxis_tickangle=-45
    )
    # last_year = filtered_df['Год'].max()
    # last_year_df = filtered_df[filtered_df['Год'] == last_year]
    # top3 = last_year_df.sort_values(by='Средняя_зарплата', ascending=False).head(3)
    #
    # top_text = [html.P(f"{row['Компания']} — средняя зарплата {row['Средняя_зарплата']} ₽")
    #             for _, row in top3.iterrows()]
    #
    # header = html.H2(f"Топ-3 компаний с наибольшей средней зарплатой в отрасли {selected_industry} за {last_year}",
    #                  style={'margin-top': '30px'})

    return fig