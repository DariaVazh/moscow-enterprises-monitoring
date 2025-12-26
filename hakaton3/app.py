from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from pages.dashboards.employment import salary, people

app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN ],suppress_callback_exceptions=True,
           assets_folder="assets")
app.title = "Индустриальные данные Москвы"
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            [
                html.I(className="fas fa-industry me-2"),
                "Индустриальные данные Москвы"
            ],
            href="/",
            className="fs-4"
        ),
        dbc.Nav([
            dbc.NavLink(
                [html.I(className="fas fa-home me-1"), "Главная"],
                href="/",
                active="exact"
            ),
            dbc.NavLink(
                [html.I(className="fas fa-chart-bar me-1"), "Производство"],
                href="/dashboard/production"
            ),
            dbc.NavLink(
                [html.I(className="fas fa-leaf me-1"), "Экология"],
                href="/dashboard/ecology"),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem(
                        dcc.Link(
                            "Страны экспорта",
                            href="/dashboard/export-countries",
                            style={
                                'color': 'inherit',
                                'textDecoration': 'none',
                                'display': 'block',
                                'padding': '8px 16px'
                            }
                        )
                    ),
                    dbc.DropdownMenuItem(
                        dcc.Link(
                            "Объем экспорта(ТОП-5)",
                            href="/dashboard/export-max_ex",
                            style={
                                'color': 'inherit',
                                'textDecoration': 'none',
                                'display': 'block',
                                'padding': '8px 16px'
                            }
                        )
                    ),
                ],
                label="Экспорт",
                nav=True,
                className="ms-2",
                id="export-dropdown"
            ),

            dbc.NavLink([html.I(className="fas fa-chart-line me-1"), "Инвестиции"],href="/dashboard/investments"),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem(
                        dcc.Link(
                            "Количество сотрудников",
                            href="/dashboard/employment-people",
                            style={
                                'color': 'inherit',
                                'textDecoration': 'none',
                                'display': 'block',
                                'padding': '8px 16px'
                            }
                        )
                    ),
                    dbc.DropdownMenuItem(
                        dcc.Link(
                            "Средняя зарплата сотрудников",
                            href="/dashboard/employment-salary",
                            style={
                                'color': 'inherit',
                                'textDecoration': 'none',
                                'display': 'block',
                                'padding': '8px 16px'
                            }
                        )
                    ),
                ],
                label="Занятость",
                nav=True,
                className="ms-2",
                id="employment-dropdown"
            ),
            dbc.NavLink(
                ["Для сотрудников Департамента"],
                href="/dashboard/employees"
            ),
            dbc.NavLink(
                ["Для предприятий"],
                href="/dashboard/company"
            ),

        ], navbar=True)

    ]),
    color="dark",
    dark=True,
    sticky="top"
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', style={'padding': '20px'})
])

from pages import home, ecology
from pages.dashboards import production, investments, employees, company
from pages.dashboards.export import countries, max_ex

PAGES = {
    '/': home.layout,
    '/dashboard/production': production.layout,
    '/dashboard/investments': investments.layout,
    '/dashboard/export-countries': countries.layout,
    '/dashboard/export-max_ex': max_ex.layout,
    '/dashboard/employment-salary': salary.layout,
    '/dashboard/employment-people': people.layout,
    '/dashboard/ecology': ecology.layout,
    '/dashboard/employees': employees.layout,
    '/dashboard/company': company.layout,
}

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    return PAGES.get(pathname, home.layout)

def set_export_dropdown_active(pathname):
    return pathname and pathname.startswith('/dashboard/export-')


if __name__ == '__main__':
    app.run(debug=True,port=8053)