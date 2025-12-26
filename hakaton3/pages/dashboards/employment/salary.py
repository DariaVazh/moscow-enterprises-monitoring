import plotly.express as px
import pandas as pd
from dash import html, dcc
import SQLLL

import sqlite3
conn = sqlite3.connect('organizations.db')

data_salary = {
    "Год": [2017]*6 + [2018]*6 + [2019]*6 + [2020]*6 + [2021]*6 + [2022]*6,
    "Компания": ["ЗАО «ФАРМЦЕНТР ВИЛАР»", "ООО «НПП «ПОЛИПЛАСТИК»", "ЗАО «МОСКОВСКАЯ ФАРМАЦЕВТИЧЕСКАЯ ФАБРИКА»", "ООО «СЕРВЬЕ РУС»", "ООО «ИЗВАРИНО ФАРМА»", "ООО «НПП «НЕФТЕХИМИЯ»"]*6,
    "Отрасль": ["Химическая промышленность", "Химическая промышленность", "Химическая промышленность", "Химическая промышленность", "Химическая промышленность", "Химическая промышленность"]*6,
    "Средняя_зарплата": [50000, 70000, 65000, 40000, 80000, 55000,
                          52000, 71000, 66000, 42000, 82000, 56000,
                          54000, 73000, 67000, 45000, 85000, 58000,
                          56000, 74000, 68000, 47000, 87000, 60000,
                          58000, 76000, 69000, 48000, 89000, 61000,
                          60000, 78000, 70000, 50000, 90000, 62000]
}
df_salary = pd.DataFrame(data_salary)
# df_salary = SQLLL.middle_zp_of_staff7(conn)
top_companies = df_salary.groupby("Компания")["Средняя_зарплата"].mean().sort_values(ascending=False).head(5).index
df_top = df_salary[df_salary["Компания"].isin(top_companies)]
# df_top = df_salary.head(5)

fig = px.bar(
    df_top,
    x="Год",
    y="Средняя_зарплата",
    color="Компания",
    barmode='group',
    text="Средняя_зарплата",
    title="Топ-5 компаний с самыми высокими средними зарплатами (2017-2022)",
    color_discrete_sequence=["#C0392B", "#7F8C8D", "#D7B49E", "#A04000", "#ECECEC"]
)
fig.update_traces(texttemplate='%{text}', textposition='outside')
fig.update_layout(
    yaxis_title="Средняя зарплата (₽)",
    xaxis_title="Год",
    legend_title="Компания"
)
avg_by_industry = df_salary.groupby("Отрасль")["Средняя_зарплата"].mean().sort_values(ascending=False)
avg_text = [html.P(f"Средняя зарплата в отрасли {industry}: {int(salary)} ₽")
            for industry, salary in avg_by_industry.items()]
layout = html.Div([
    html.H1("Топ-5 компаний по зарплатам", className="mb-4"),
    dcc.Graph(figure=fig),
    html.H2("Средняя зарплата по отраслям за последний год", style={'margin-top': '30px'}),
    html.Div(avg_text)
])