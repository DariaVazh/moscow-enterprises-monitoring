from dash import Dash, html, dcc, Input, Output, State, callback
import pandas as pd
import io
import base64
layout = html.Div([
    html.H2("Загрузка Excel файла", style={'textAlign': 'center', 'marginBottom': '30px'}),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Перетащите файл сюда или ',
            html.A('выберите файл')
        ]),
        style={
            'width': '400px',
            'height': '100px',
            'lineHeight': '100px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'margin': '0 auto 30px auto',
            'backgroundColor': '#f9f9f9'
        },
        multiple=False
    ),

    html.Div(id='output-data-upload', style={
        'width': '80%',
        'margin': '0 auto',
        'padding': '20px',
        'border': '1px solid #ddd',
        'borderRadius': '10px',
        'backgroundColor': '#fcfcfc',
        'whiteSpace': 'pre-wrap',
        'overflowX': 'auto'
    })
])


@callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_upload(contents, filename):
    if contents is None:
        return "Файл не загружен"

    if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
        return html.Div([
            html.H5(f"Файл {filename} имеет некорректный формат. Загрузите Excel файл (.xlsx или .xls).")
        ])

    content_type, content_string = contents.split(',')
    decoded = io.BytesIO(base64.b64decode(content_string))

    try:
        df = pd.read_excel(decoded)
        return html.Div([
            html.H5(f"Файл {filename} успешно загружен!")
        ])

    except Exception as e:
        return html.Div([
            'Ошибка при чтении файла:',
            str(e)
        ])