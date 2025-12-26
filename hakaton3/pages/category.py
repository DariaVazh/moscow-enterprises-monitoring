import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

import sqlite3
conn = sqlite3.connect('organizations.db')


def get_layout(category):
    category_names = {
        'production': 'Производство',
        'export': 'Экспорт',
        'employment': 'Занятость',
        'investments': 'Инвестиции'
    }

    return html.Div([
        html.H1(f"📈 {category_names[category]}"),

        # Фильтры
        dbc.Row([
            dbc.Col([
                html.Label("Отрасль:"),
                dcc.Dropdown(
                    id=f'{category}-industry-filter',
                    options=[
                        {'label': 'Все отрасли', 'value': 'all'},
                        {'label': 'Машиностроение', 'value': 'machinery'},
                        {'label': 'Химическая', 'value': 'chemical'},
                        {'label': 'Пищевая', 'value': 'food'},
                        {'label': 'Электроника', 'value': 'electronics'}
                    ],
                    value='all'
                )
            ], width=4),

            dbc.Col([
                html.Label("Округ:"),
                dcc.Dropdown(
                    id=f'{category}-district-filter',
                    options=[
                        {'label': 'Все округа', 'value': 'all'},
                        {'label': 'ЦАО', 'value': 'cao'},
                        {'label': 'ЮАО', 'value': 'uao'},
                        {'label': 'ЗелАО', 'value': 'zelao'}
                    ],
                    value='all'
                )
            ], width=4),

            dbc.Col([
                html.Label("Период:"),
                dcc.Dropdown(
                    id=f'{category}-period-filter',
                    options=[
                        {'label': 'За месяц', 'value': 'month'},
                        {'label': 'За квартал', 'value': 'quarter'},
                        {'label': 'За год', 'value': 'year'}
                    ],
                    value='month'
                )
            ], width=4),
        ], className="mb-4"),

        # Графики
        dbc.Row([
            dbc.Col(dcc.Graph(id=f'{category}-trend-chart'), width=8),
            dbc.Col(dcc.Graph(id=f'{category}-pie-chart'), width=4),
        ]),

        # Таблица данных
        html.H3("Таблица данных", className="mt-4"),
        html.Div(id=f'{category}-data-table')
    ])