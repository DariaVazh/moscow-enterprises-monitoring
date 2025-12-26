from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import SQLLL
import sqlite3
conn = sqlite3.connect('organizations.db')


# Создаем DataFrame
df_enterprises = SQLLL.get_coordinats(conn)

# Создаем простую карту с ограничениями
fig_map = px.scatter_map(
    df_enterprises,
    lat="Долгота",
    lon="Широта",
    color="Отрасль",
    hover_name="Предприятие",
    # hover_data={"Адрес": True, "Количество_сотрудников": True},
    color_discrete_map={
        "Химическая": "green",
        "Машиностроение": "blue",
        "Электроника": "orange",
        "Пищевая": "red"
    }
)

# Ограничиваем карту только Москвой
fig_map.update_layout(
    mapbox_style="open-street-map",
    mapbox=dict(
        center=dict(lat=55.7558, lon=37.6173),
        zoom=10.5,
        bounds=dict(
            west=37.35,
            east=37.85,
            south=55.55,
            north=55.92
        )
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=500
)

layout = html.Div([
    html.Img(
        src="/assets/pic_2.png",  # Убрал localhost для корректной работы
        style={'width': '50px', 'height': '50px', 'float': 'left', 'marginRight': '10px'}
    ),
    html.H1("Индустриальные данные Москвы", className="mb-4"),
    html.Img(
        src="/assets/pic_1.jpg",
        style={'width': '40%', 'height': '188px', 'objectFit': 'cover'}
    ),

    # KPI карточки
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("45.2 млрд ₽", className="card-title"),
                html.P("Объем производства", className="card-text"),
                html.Small("+5.2% за месяц", className="text-success")
            ])
        ], color="black", inverse=True), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("18.7 млрд ₽", className="card-title"),
                html.P("Экспорт", className="card-text"),
                html.Small("+12.1% за месяц", className="text-success")
            ])
        ], color="danger", inverse=True), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("125,430", className="card-title"),
                html.P("Занятость", className="card-text"),
                html.Small("+2.3% за месяц", className="text-success")
            ])
        ], color="black", inverse=True), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("8.9 млрд ₽", className="card-title"),
                html.P("Инвестиции", className="card-text"),
                html.Small("+8.7% за месяц", className="text-success")
            ])
        ], color="danger", inverse=True), width=3),
    ], className="mb-5"),

    html.H3("Быстрый доступ", className="mb-3"),
    dbc.Row([
        dbc.Col(dbc.Button(
            "Производство →",
            color="danger",
            size="lg",
            href="/dashboard/production",
            className="w-100 py-3"
        ), width=3),
        dbc.Col([
            dbc.Button(
                "Экспорт →",
                color="secondary",
                size="lg",
                className="w-100 py-3",
                id="export-popover-target"
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Анализ экспорта"),
                    dbc.PopoverBody([
                        dbc.NavLink(
                            "Объем экспорта(ТОП-5)",
                            href="/dashboard/export-max_ex",
                            className="p-2 text-dark",
                            style={'textDecoration': 'none', 'borderRadius': '5px'}
                        ),
                        dbc.NavLink(
                            "Структура по странам",
                            href="/dashboard/export-countries",
                            className="p-2 text-dark",
                            style={'textDecoration': 'none', 'borderRadius': '5px'}
                        ),
                    ])
                ],
                target="export-popover-target",
                placement="bottom",
                trigger="hover"
            )
        ], width=3),
        dbc.Col([
            dbc.Button(
                "Занятость →",
                color="danger",
                size="lg",
                className="w-100 py-3",
                id="employment-popover-target"
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Анализ занятости"),
                    dbc.PopoverBody([
                        dbc.NavLink(
                            "Количество сотрудников",
                            href="/dashboard/employment-people",
                            className="p-2 text-dark",
                            style={'textDecoration': 'none', 'borderRadius': '5px'}
                        ),
                        dbc.NavLink(
                            "Средняя зарплата сотрудников",
                            href="/dashboard/employment-salary",
                            className="p-2 text-dark",
                            style={'textDecoration': 'none', 'borderRadius': '5px'}
                        ),
                    ])
                ],
                target="employment-popover-target",
                placement="bottom",
                trigger="hover"
            )
        ], width=3),
        dbc.Col(dbc.Button(
            "Инвестиции →",
            color="secondary",
            size="lg",
            href="/dashboard/investments",
            className="w-100 py-3"
        ), width=3),
    ]),

    html.H4("Промышленные предприятия Москвы"),
    html.P("Карта предприятий с цветовой кодировкой по отраслям", className="text-muted mb-3"),
    dcc.Graph(figure=fig_map, className="mb-4")

#     dbc.Row([
#         dbc.Col(html.Div([
#             html.Span("🟢 Химическая промышленность", className="me-3"),
#             html.Span("🔵 Машиностроение", className="me-3"),
#             html.Span("🟠 Электроника", className="me-3"),
#             html.Span("🔴 Пищевая промышленность")
#         ], className="text-center p-2"), width=12)
#     ], className="mb-4"),
])