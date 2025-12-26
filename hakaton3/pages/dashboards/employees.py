from dash import Dash, html, dcc, callback, Input, Output, State
import pandas as pd

df = pd.DataFrame({
    "Уровень загрузки производственных мощностей": [None]*5,
    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2022": [None]*5,
    "Инвестиции в Мск 2022 тыс. руб.": [None]*5
    # "Чистая прибыль (убыток)": [None]*5,
    # "Среднесписочная численность персонала": [None]*5,
    # "Количество произведенной продукции": [None]*5,
    # "Количество проданной продукции": [None]*5,
    # "Средняя з.п. всех сотрудников организации": [None]*5,
    # "Наличие экологического оборудования": [None]*5,
    # "Инвестиции в Мск": [None]*5,
    # "Объем экспорта": [None]*5
})

layout = html.Div([
    html.H2("Страница сотрудников", style={'textAlign': 'center', 'marginBottom': '30px'}),

    # --- Выбор показателей ---
    html.Div([
        html.Label("Выберите показатели:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        dcc.Checklist(
            id='metric-selector',
            options=[{"label": col, "value": col} for col in df.columns],
            value=[col for col in df.columns],
            inline=False,
            style={'marginLeft': '20px'},
            labelStyle={'display': 'block', 'marginBottom': '10px', 'marginLeft': '10px'}
        ),
    ], style={'marginBottom': '20px'}),

    # --- Кнопка экспорта ---
    html.Button(
        "Экспорт в Excel",
        id='export-button',
        n_clicks=0,
        style={
            'backgroundColor': '#119DFF',
            'color': 'white',
            'border': 'none',
            'padding': '10px 20px',
            'borderRadius': '5px',
            'fontSize': '16px',
            'cursor': 'pointer',
            'marginBottom': '20px'
        }
    ),

    # --- Скрытое хранение выбранных галочек ---
    dcc.Store(id='selected-checkboxes-store')
])

# --- Callback: возвращает выбранные метрики ---
@callback(
    Output('selected-checkboxes-store', 'data'),
    Input('metric-selector', 'value')
)
def get_selected_checkboxes(selected_metrics):
    return {"columns": selected_metrics}

# --- Callback для экспорта ---
@callback(
    Output('export-button', 'n_clicks'),
    Input('export-button', 'n_clicks'),
    State('selected-checkboxes-store', 'data'),
    prevent_initial_call=True
)
def export_excel(n_clicks, checkboxes_data):
    if n_clicks > 0 and checkboxes_data:
        import sqlite3
        conn = sqlite3.connect('organizations.db')

        result = for_excel(
            conn=conn,
            columns=checkboxes_data['columns'],
            # rows=None,  # убрали выбор компаний
            sorter=checkboxes_data['columns'][0]
        )

        conn.close()
        return result
    return n_clicks


def for_excel(conn, columns, sorter):
    # Формируем список столбцов с двойными кавычками
    s = ','.join([f'"{c}"' for c in columns])

    # Проверяем, есть ли данные в таблице
    query = f'''
    SELECT {s}
    FROM organizations
    WHERE "{columns[0]}" IS NOT NULL
    ORDER BY "{columns[0]}"
    '''

    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            raise ValueError("Нет данных, соответствующих запросу.")
        from dash import dcc
        return dcc.send_data_frame(df.to_excel, "moscow_production.xlsx", index=False, sheet_name="Данные")
    except pd.errors.DatabaseError as e:
        raise ValueError(f"Ошибка выполнения запроса: {str(e)}")

