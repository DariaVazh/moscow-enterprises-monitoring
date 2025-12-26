from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import SQLLL
import sqlite3
conn = sqlite3.connect('organizations.db')

# data = {
#     "Компания": ["ЦАО", "САО", "СВАО", "ЮАО", "ЗАО", "ВАО"] * 3,
#     "Отрасль": ["Промышленность", "Промышленность", "IT", "IT", "Транспорт", "Транспорт"] * 3,
#     "Год": [2020] * 6 + [2021] * 6 + [2022] * 6,
#     "Выручка": [1000, 1500, 2000, 1800, 1200, 1600, 1100, 1550, 2100, 1900, 1300, 1650, 1150, 1600, 2200, 2000, 1400,
#                 1700],
#     "Прибыль": [200, 300, 500, 450, 250, 350, 220, 310, 520, 480, 270, 360, 230, 320, 540, 500, 290, 380],
#     "Объем_реализации": [500, 700, 1000, 900, 600, 800, 520, 710, 1050, 950, 630, 820, 540, 720, 1100, 980, 650, 850]
# }
#
# df = pd.DataFrame(data)

df = SQLLL.get_top5_companies_metrics(conn)
layout = html.Div([
    html.H1("Финансово-экономические показатели компаний", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Выберите отрасль:"),
        dcc.Dropdown(
            id='industry-dropdown',
            options=[{'label': i, 'value': i} for i in df['Отрасль'].unique()],
            value=df['Отрасль'].unique()[0],
            clearable=False
        ),
    ], style={'width': '40%', 'marginBottom': '20px'}),

    html.Div([
        html.Label("Выберите год:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': y, 'value': y} for y in df['Год'].unique()],
            value=df['Год'].max(),
            clearable=False
        ),
    ], style={'width': '40%', 'marginBottom': '30px'}),

    dcc.Graph(id='financial-graph'),

    html.Div(id='top-companies-output', style={'marginTop': '30px', 'fontSize': '16px'})
])
@callback(
    Output('financial-graph', 'figure'),
    Output('top-companies-output', 'children'),
    Input('industry-dropdown', 'value'),
    Input('year-dropdown', 'value')
)
def update_graph(selected_industry, selected_year):
    # Фильтруем данные
    filtered_df = df[(df['Отрасль'] == selected_industry) & (df['Год'] == selected_year)]

    # --- График по выручке и прибыли ---
    df_melt = filtered_df.melt(
        id_vars='Компания',
        value_vars=['Выручка', 'Прибыль'],
        var_name='Показатель',
        value_name='Значение'
    )

    fig = px.bar(
        df_melt,
        x='Компания',
        y='Значение',
        color='Показатель',
        barmode='group',
        text='Значение',
        title=f"Выручка и прибыль компаний отрасли {selected_industry} за {selected_year}"
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(yaxis_title="Сумма (тыс. ₽)", xaxis_title="Компания")

    # --- Топ-5 компаний по объему реализации ---
    top5 = filtered_df.sort_values(by='Объем_реализации', ascending=False).head(5)
    top_text = [html.P(f"{row['Компания']} — объём реализации {row['Объем_реализации']}")
                for _, row in top5.iterrows()]
    header = html.H2(f"Топ компаний по объему реализации в отрасли {selected_industry} за {selected_year}",
                     style={'marginTop': '20px'})

    return fig, [header] + top_text
