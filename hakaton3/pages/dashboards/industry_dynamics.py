import dash
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

import sqlite3
conn = sqlite3.connect('organizations.db')


# Тестовые данные по отраслям
def generate_industry_data():
    industries = {
        'Химическая': {
            'enterprises': ['Московский НПЗ', 'Каучук', 'Полимерсинтез', 'Химзавод №1'],
            'growth_trend': 1.15  # 15% рост в год
        },
        'Машиностроение': {
            'enterprises': ['ЗИЛ', 'Станколит', 'Автокомплекс', 'Машзавод'],
            'growth_trend': 1.08
        },
        'Пищевая': {
            'enterprises': ['Черкизово', 'Бабаевский', 'Красный Октябрь', 'Мясокомбинат'],
            'growth_trend': 1.12
        },
        'Электроника': {
            'enterprises': ['Микрон', 'Ангстрем', 'Элтеза', 'Миландр'],
            'growth_trend': 1.25
        },
        'Металлообработка': {
            'enterprises': ['Металлозавод', 'Спецсталь', 'Металлоконструкция'],
            'growth_trend': 1.05
        }
    }

    data = []
    for year in [2021, 2022, 2023, 2024]:
        for industry, info in industries.items():
            base_value = 10000000  # Базовая стоимость производства
            production = base_value * (info['growth_trend'] ** (year - 2021))

            data.append({
                'year': year,
                'industry': industry,
                'production': int(production * np.random.uniform(0.9, 1.1)),
                'export': int(production * 0.3 * np.random.uniform(0.8, 1.2)),
                'employees': int(production / 10000 * np.random.uniform(0.8, 1.2)),
                'investments': int(production * 0.15 * np.random.uniform(0.7, 1.3)),
                'energy_consumption': int(production * 0.02 * np.random.uniform(0.9, 1.1)),
                'productivity': production / (production / 10000) * np.random.uniform(0.95, 1.05)
            })

    return pd.DataFrame(data)


df = generate_industry_data()

layout = html.Div([
    html.H1("🏭 Динамика по отраслям", className="mb-4"),

    # Фильтры
    dbc.Row([
        dbc.Col([
            html.Label("Выберите отрасль:"),
            dcc.Dropdown(
                id='industry-selector',
                options=[{'label': industry, 'value': industry} for industry in df['industry'].unique()],
                value='Химическая',
                clearable=False
            )
        ], width=4),

        dbc.Col([
            html.Label("Показатель:"),
            dcc.Dropdown(
                id='metric-selector',
                options=[
                    {'label': 'Производство (руб)', 'value': 'production'},
                    {'label': 'Экспорт (руб)', 'value': 'export'},
                    {'label': 'Занятость (чел)', 'value': 'employees'},
                    {'label': 'Инвестиции (руб)', 'value': 'investments'},
                    {'label': 'Энергопотребление', 'value': 'energy_consumption'},
                    {'label': 'Производительность', 'value': 'productivity'}
                ],
                value='production',
                clearable=False
            )
        ], width=4),

        dbc.Col([
            html.Label("Тип графика:"),
            dcc.Dropdown(
                id='chart-type-selector',
                options=[
                    {'label': 'Линейный график', 'value': 'line'},
                    {'label': 'Столбчатая диаграмма', 'value': 'bar'},
                    {'label': 'Сравнение с другими', 'value': 'comparison'}
                ],
                value='line',
                clearable=False
            )
        ], width=4),
    ], className="mb-4"),

    # KPI выбранной отрасли
    html.Div(id='industry-kpi-cards', className="mb-4"),

    # Основной график
    dbc.Row([
        dbc.Col(dcc.Graph(id='industry-dynamics-chart'), width=12),
    ], className="mb-4"),

    # Дополнительная информация
    dbc.Row([
        dbc.Col(dcc.Graph(id='industry-pie-chart'), width=6),
        dbc.Col(dcc.Graph(id='industry-growth-chart'), width=6),
    ]),
])


@callback(
    [Output('industry-kpi-cards', 'children'),
     Output('industry-dynamics-chart', 'figure'),
     Output('industry-pie-chart', 'figure'),
     Output('industry-growth-chart', 'figure')],
    [Input('industry-selector', 'value'),
     Input('metric-selector', 'value'),
     Input('chart-type-selector', 'value')]
)
def update_industry_dashboard(selected_industry, selected_metric, chart_type):
    # Фильтруем данные по выбранной отрасли
    industry_data = df[df['industry'] == selected_industry]
    all_industries_data = df.copy()

    # Метрики для отображения
    metric_names = {
        'production': 'Производство, руб',
        'export': 'Экспорт, руб',
        'employees': 'Занятость, чел',
        'investments': 'Инвестиции, руб',
        'energy_consumption': 'Энергопотребление',
        'productivity': 'Производительность'
    }

    # 1. KPI карточки
    current_year_data = industry_data[industry_data['year'] == 2024].iloc[0]
    previous_year_data = industry_data[industry_data['year'] == 2023].iloc[0]

    current_value = current_year_data[selected_metric]
    previous_value = previous_year_data[selected_metric]
    growth = ((current_value - previous_value) / previous_value) * 100

    kpi_cards = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{current_value:,.0f}", className="text-primary"),
                html.P(metric_names[selected_metric]),
                html.Small(f"2024 год", className="text-muted")
            ])
        ]), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{growth:+.1f}%",
                        className="text-success" if growth > 0 else "text-danger"),
                html.P("Рост к 2023 году"),
                html.Small("динамика", className="text-muted")
            ])
        ]), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{current_year_data['employees']:,.0f}", className="text-warning"),
                html.P("Занятость"),
                html.Small("сотрудников", className="text-muted")
            ])
        ]), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{current_year_data['export']:,.0f}", className="text-info"),
                html.P("Экспорт"),
                html.Small("объем", className="text-muted")
            ])
        ]), width=3),
    ])

    # 2. Основной график динамики
    if chart_type == 'comparison':
        # Сравнение с другими отраслями
        fig_dynamics = px.line(all_industries_data,
                               x='year', y=selected_metric,
                               color='industry',
                               title=f"Сравнение {metric_names[selected_metric]} по отраслям")
    else:
        # Динамика выбранной отрасли
        if chart_type == 'line':
            fig_dynamics = px.line(industry_data, x='year', y=selected_metric,
                                   title=f"Динамика {metric_names[selected_metric]} - {selected_industry}")
        else:
            fig_dynamics = px.bar(industry_data, x='year', y=selected_metric,
                                  title=f"Динамика {metric_names[selected_metric]} - {selected_industry}")

    # 3. Круговая диаграмма - структура отрасли
    current_year_all = all_industries_data[all_industries_data['year'] == 2024]
    fig_pie = px.pie(current_year_all, values=selected_metric, names='industry',
                     title=f"Доля {selected_industry} в общем {metric_names[selected_metric]} (2024)")

    # 4. График роста по годам
    growth_data = []
    for industry in all_industries_data['industry'].unique():
        ind_data = all_industries_data[all_industries_data['industry'] == industry]
        values = ind_data[selected_metric].values
        growth_rates = [(values[i] - values[i - 1]) / values[i - 1] * 100
                        for i in range(1, len(values))]
        for i, growth in enumerate(growth_rates):
            growth_data.append({
                'year': f'{2021 + i}-{2022 + i}',
                'industry': industry,
                'growth': growth
            })

    growth_df = pd.DataFrame(growth_data)
    fig_growth = px.bar(growth_df, x='year', y='growth', color='industry',
                        title="Темпы роста по отраслям (%)",
                        barmode='group')

    return kpi_cards, fig_dynamics, fig_pie, fig_growth