import datetime
from api_requests import *
from country_codes import *

import random

pd.set_option('display.max_columns', None)      # Показывать все столбцы
pd.set_option('display.width', None)            # Автоматическая ширина

# добавление/обновление данных
def upsertOrganization(conn, data):
    if "ИНН" not in data:
        raise ValueError("Каждая запись должна содержать 'ИНН'")

    inn = data["ИНН"]
    updateFields = {k: v for k, v in data.items() if k != "ИНН"}

    # currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # updateFields["Время последнего обновления"] = currentTime

    if not updateFields: # Только ИНН — просто вставляем пустую запись
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO organizations ("ИНН") VALUES (?)', (inn))
        return

    colsForInsert = ["ИНН"] + list(updateFields.keys())
    quotedCols = ', '.join([f'"{col}"' for col in colsForInsert])

    # Формируем SET часть: "col1" = ?, "col2" = ?
    set_clause = ', '.join([f'"{col}" = excluded."{col}"' for col in updateFields])

    # Полный запрос
    # 1. перечисляем столбцы, куда вставляем значения
    # 2. параметр запроса (?, ?, ..., ?)
    # 3. если инн уже есть
    query = f'''
            INSERT INTO organizations ("ИНН", {', '.join([f'"{col}"' for col in updateFields])})
            VALUES (?, {', '.join(['?'] * len(updateFields))})
            ON CONFLICT("ИНН") DO UPDATE SET {set_clause}
        '''

    # Все значения для подстановки
    allValues = [inn] + list(updateFields.values())

    cursor = conn.cursor()
    cursor.execute(query, allValues)

#вывод датафрейма с полной информацией о компании через инн
def getOrganizationByInn(conn, inn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM organizations WHERE "ИНН" = ?', (inn,))
    row = cursor.fetchone()

    if row is None:
        cursor.execute('SELECT * FROM organizations LIMIT 0')
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(columns=columns)

    columns = [description[0] for description in cursor.description]
    return pd.DataFrame([row], columns=columns)
    #     cursor = conn.cursor()
    #     cursor.execute('SELECT * FROM organizations WHERE "ИНН" = ?', (inn,))
    #     row = cursor.fetchone()
    #
    #     if row is None:
    #         return None
    #
    #     columns = [description[0] for description in cursor.description]
    #     return dict(zip(columns, row))

# вывод дф инн + даные из нужной колонки
def getColVal(conn, columnName):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(organizations)")
    existingColumns = {row[1] for row in cursor.fetchall()}

    if columnName not in existingColumns:
        raise ValueError(f"Столбец '{columnName}' не найден в таблице. Доступные: {sorted(existingColumns)}")

    query = f'SELECT "ИНН", "{columnName}" FROM organizations WHERE "{columnName}" IS NOT NULL AND "{columnName}" != ""'

    cursor.execute(query)
    results = cursor.fetchall()
    return pd.DataFrame(results, columns=["ИНН", columnName])

#фин эк
def get_top5_companies_metrics(conn, industry=""):
    years = list(range(2017, 2023))

    # Определяем колонки для выручки, прибыли и объема реализации
    revenue_cols = [f'Выручка предприятия, тыс. руб. {year}' for year in years]
    profit_cols = [f'Чистая прибыль (убыток),тыс. руб. {year}' for year in years]
    sales_cols = [f'Количество проданной продукции за {year}' for year in years]

    # Все нужные колонки для запроса
    all_cols = ['ИНН', 'Наименование организации', 'Основная отрасль'] + revenue_cols + profit_cols + sales_cols
    quoted_cols = ', '.join([f'"{col}"' for col in all_cols])

    # Базовый запрос
    query = f"SELECT {quoted_cols} FROM organizations"

    # Добавляем фильтр по отрасли если указана
    if industry:
        query += f" WHERE \"Основная отрасль\" = '{industry}'"

    df = pd.read_sql_query(query, conn)

    result_rows = []

    for year in years:
        # Получаем названия колонок для текущего года
        revenue_col = f'Выручка предприятия, тыс. руб. {year}'
        profit_col = f'Чистая прибыль (убыток),тыс. руб. {year}'
        sales_col = f'Количество проданной продукции за {year}'

        # Проверяем, что колонки существуют
        if (revenue_col in df.columns and profit_col in df.columns and sales_col in df.columns):

            # Берем топ-5 по выручке за текущий год
            top5_revenue = df.nlargest(5, revenue_col, keep='all')

            for _, row in top5_revenue.iterrows():
                result_rows.append({
                    'Компания': row['Наименование организации'],
                    'Отрасль': industry if industry else row['Основная отрасль'],
                    'Год': year,
                    'Выручка': row[revenue_col] if pd.notna(row[revenue_col]) else 0,
                    'Прибыль': row[profit_col] if pd.notna(row[profit_col]) else 0,
                    'Объем_реализации': row[sales_col] if pd.notna(row[sales_col]) else 0
                })

    # Создаем итоговый DataFrame
    if result_rows:
        result_df = pd.DataFrame(result_rows)
        # Сортируем по году и выручке (по убыванию)
        result_df = result_df.sort_values(['Год', 'Выручка'], ascending=[True, False])
        return result_df[['Компания', 'Отрасль', 'Год', 'Выручка', 'Прибыль', 'Объем_реализации']]
    else:
        return pd.DataFrame(columns=['Компания', 'Отрасль', 'Год', 'Выручка', 'Прибыль', 'Объем_реализации'])

# топ 5 по числинности персонала
def number_of_staff6(conn, industry=""):
    # Список годов и соответствующих колонок
    years_columns = {
        2017: "Среднесписочная численность персонала (всего по компании), чел 2017",
        2018: "Среднесписочная численность персонала (всего по компании), чел 2018",
        2019: "Среднесписочная численность персонала (всего по компании), чел 2019",
        2020: "Среднесписочная численность персонала (всего по компании), чел 2020",
        2021: "Среднесписочная численность персонала (всего по компании), чел 2021",
        2022: "Среднесписочная численность персонала (всего по компании), чел 2022"
    }

    # Собираем все данные в списки
    years_list = []
    companies_list = []
    staff_count_list = []
    inn_list = []
    industry_list = []

    for year, column in years_columns.items():
        # Базовый запрос
        query = f'''
        SELECT "ИНН", "Наименование организации", "{column}", "Основная отрасль"
        FROM organizations
        '''

        # Добавляем фильтр по отрасли если указана
        if industry:
            query += f" WHERE \"Основная отрасль\" = '{industry}'"

        query += f' ORDER BY "{column}" DESC LIMIT 5'

        df_temp = pd.read_sql_query(query, conn)

        # Добавляем данные в общие списки
        for _, row in df_temp.iterrows():
            years_list.append(year)
            inn_list.append(row['ИНН'])
            companies_list.append(row['Наименование организации'])
            staff_count_list.append(row[column])
            if industry:
                industry_list.append(industry)
            else:
                industry_list.append(row['Основная отрасль'])

    # Создаем итоговый DataFrame
    data_num_people = {
        "Год": years_list,
        "Компания": companies_list,
        "Кол-во сотрудников": staff_count_list,
        "Отрасль": industry_list
    }

    df = pd.DataFrame(data_num_people)
    return df

# топ 5 по инвестициям в мск
def get_top5_investors_moscow(conn, industry=""):
    year_cols = {
        2021: "Инвестиции в Мск 2021 тыс. руб.",
        2022: "Инвестиции в Мск 2022 тыс. руб.",
        2023: "Инвестиции в Мск 2023 тыс. руб."
    }

    # Формируем SELECT
    select_cols = ['ИНН', 'Наименование организации', 'Основная отрасль'] + list(year_cols.values())
    quoted_cols = ', '.join([f'"{col}"' for col in select_cols])

    # Базовый запрос
    query = f"SELECT {quoted_cols} FROM organizations"

    # Добавляем фильтр по отрасли если указана
    if industry:
        query += f" WHERE \"Основная отрасль\" = '{industry}'"

    df = pd.read_sql_query(query, conn)

    if df.empty:
        # Возвращаем пустой датафрейм с нужными колонками в зависимости от industry
        if industry:
            return pd.DataFrame(columns=["Год", "Компания", "Отрасль", "Инвестиции_тыс_руб"])
        else:
            return pd.DataFrame(columns=["Год", "Компания", "Инвестиции_тыс_руб"])

    result_rows = []

    for year, col in year_cols.items():
        # Работаем с копией, чтобы не трогать исходный df
        if industry:
            df_year = df[["ИНН", "Наименование организации", "Основная отрасль", col]].copy()
        else:
            df_year = df[["ИНН", "Наименование организации", col]].copy()

        # Убираем строки, где инвестиции NULL или NaN
        df_year = df_year.dropna(subset=[col])

        # Преобразуем в числовой тип (на случай, если там строки)
        df_year[col] = pd.to_numeric(df_year[col], errors='coerce')
        df_year = df_year.dropna(subset=[col])

        # Сортируем по убыванию и берём топ-5
        top5 = df_year.nlargest(5, col, keep='all')

        # Преобразуем в нужный формат
        top5 = top5.rename(columns={
            "Наименование организации": "Компания",
            col: "Инвестиции_тыс_руб"
        })
        top5["Год"] = year

        # Добавляем отрасль только если она была указана
        if industry:
            top5["Отрасль"] = industry
            result_rows.append(top5[["Год", "Компания", "Отрасль", "Инвестиции_тыс_руб"]])
        else:
            result_rows.append(top5[["Год", "Компания", "Инвестиции_тыс_руб"]])

    if not result_rows:
        # Возвращаем пустой датафрейм с нужными колонками
        if industry:
            return pd.DataFrame(columns=["Год", "Компания", "Отрасль", "Инвестиции_тыс_руб"])
        else:
            return pd.DataFrame(columns=["Год", "Компания", "Инвестиции_тыс_руб"])

    result = pd.concat(result_rows, ignore_index=True)
    return result

def get_export_countries_set(conn, industry=""):
    query = '''
        SELECT "Основная отрасль", "Перечень государств куда экспортируется продукция"
        FROM organizations
        WHERE "Перечень государств куда экспортируется продукция" IS NOT NULL
          AND TRIM("Перечень государств куда экспортируется продукция") != ''
    '''

    if industry:
        query = query.replace('WHERE', f'WHERE "Основная отрасль" = \'{industry}\' AND')

    df = pd.read_sql_query(query, conn)

    if df.empty:
        return pd.DataFrame(columns=["ISO", "Страна", "Отрасль"])

    unique_countries = set()

    for _, row in df.iterrows():
        if not isinstance(row['Перечень государств куда экспортируется продукция'], str):
            continue

        countries = [
            c.strip() for c in
            row['Перечень государств куда экспортируется продукция']
            .replace(' и ', ', ').replace(';', ',').split(',')
            if c.strip() and c.strip().lower() != 'нет экспорта'
        ]

        industry_name = industry if industry else row['Основная отрасль']
        unique_countries.update((country, industry_name) for country in countries)

    # Преобразуем в DataFrame
    result_rows = [
        {'ISO': country_codes.get(country, country[:3].upper()), 'Страна': country, 'Отрасль': industry}
        for country, industry in unique_countries
    ]

    return pd.DataFrame(result_rows).sort_values(['Отрасль', 'Страна']).reset_index(drop=True)

# топ 5 по максимальным кол-вам стран экспорта
def get_top5_export_countries_count(conn, industry=""):
    query = '''
        SELECT
            "Наименование организации",
            "Основная отрасль",
            "Перечень государств куда экспортируется продукция",
            "Объем экспорта, тыс. руб. 2019",
            "Объем экспорта, тыс. руб. 2020", 
            "Объем экспорта, тыс. руб. 2021",
            "Объем экспорта, тыс. руб. 2022"
        FROM organizations
        WHERE "Перечень государств куда экспортируется продукция" IS NOT NULL
          AND TRIM("Перечень государств куда экспортируется продукция") != ''
    '''

    # Добавляем фильтр по отрасли если указана
    if industry:
        query = query.replace('WHERE', f'WHERE "Основная отрасль" = \'{industry}\' AND')

    df = pd.read_sql_query(query, conn)

    if df.empty:
        return pd.DataFrame(columns=["Год", "Компания", "Отрасль", "Объем"])

    def count_countries(countries_str):
        if not isinstance(countries_str, str):
            return 0
        if countries_str.lower() == "нет экспорта":
            return 0
        countries = [c.strip() for c in countries_str.split(',') if c.strip()]
        return len(countries)

    # Добавляем количество стран
    df["Количество стран"] = df["Перечень государств куда экспортируется продукция"].apply(count_countries)

    # Берем топ-5 по количеству стран
    top5 = df.nlargest(5, "Количество стран", keep='all')

    # Собираем данные по годам
    result_rows = []
    years = [2019, 2020, 2021, 2022]

    for _, row in top5.iterrows():
        company = row['Наименование организации']
        industry_name = industry if industry else row['Основная отрасль']

        for year in years:
            volume_col = f'Объем экспорта, тыс. руб. {year}'
            if volume_col in row and pd.notna(row[volume_col]):
                result_rows.append({
                    'Год': year,
                    'Компания': company,
                    'Отрасль': industry_name,
                    'Объем': row[volume_col]
                })

    return pd.DataFrame(result_rows).sort_values(['Год', 'Объем'], ascending=[True, False]).reset_index(drop=True)

def middle_zp_of_staff7(conn, industry=""):
    years_columns = {
        2017: "Средняя з.п. всех сотрудников организации,  тыс.руб. 2017",
        2018: "Средняя з.п. всех сотрудников организации,  тыс.руб. 2018",
        2019: "Средняя з.п. всех сотрудников организации,  тыс.руб. 2019",
        2020: "Средняя з.п. всех сотрудников организации,  тыс.руб. 2020",
        2021: "Средняя з.п. всех сотрудников организации,  тыс.руб. 2021",
        2022: "Средняя з.п. всех сотрудников организации,  тыс.руб. 2022"
    }

    # Собираем все данные в списки
    years_list = []
    companies_list = []
    staff_count_list = []
    industries_list = []

    for year, column in years_columns.items():
        # Базовый запрос
        if industry:
            query = f'''
            SELECT "Наименование организации", "Основная отрасль", "{column}"
            FROM organizations
            WHERE "Основная отрасль" = {industry} 
            ORDER BY "{column}" DESC 
            LIMIT 5
            '''
            params = [industry]
        else:
            query = f'''
            SELECT "Наименование организации", "Основная отрасль", "{column}"
            FROM organizations
            ORDER BY "{column}" DESC 
            LIMIT 5
            '''
            params = []

        df_temp = pd.read_sql_query(query, conn, params=params)

        # Добавляем данные в общие списки
        for _, row in df_temp.iterrows():
            years_list.append(year)
            companies_list.append(row['Наименование организации'])
            staff_count_list.append(row[column])
            industries_list.append(row['Основная отрасль'] if industry else industry)
            # if industry:
            #     industries_list.append(industry)
            # else:
            #     industries_list.append(row['Основная отрасль'])
    # Создаем итоговый DataFrame
    data_num_people = {
        "Год": years_list,
        "Компания": companies_list,
        "Отрасль": industries_list,
        "Средняя_зарплата": staff_count_list
    }

    df = pd.DataFrame(data_num_people)
    return df

# 5 с минимальной разницей между кол-вом произведенного товара и кол-вом проданного товара
# Объем реализованной продукции
def get5minDiff(conn, industry=""):
    years = list(range(2017, 2023))

    # Базовые запросы с фильтром по отрасли
    prod_cols = [f'Количество произведенной продукции за {y}' for y in years]

    prod_query = f'''
        SELECT "ИНН", "Наименование организации", "Основная отрасль", {', '.join([f'"{col}"' for col in prod_cols])}
        FROM organizations
    '''
    if industry:
        prod_query = prod_query.replace('FROM organizations',
                                        f'FROM organizations WHERE "Основная отрасль" = \'{industry}\'')

    sold_cols = [f'Количество проданной продукции за {y}' for y in years]

    sold_query = f'''
        SELECT "ИНН", "Наименование организации", "Основная отрасль", {', '.join([f'"{col}"' for col in sold_cols])}
        FROM organizations
    '''
    if industry:
        sold_query = sold_query.replace('FROM organizations',
                                        f'FROM organizations WHERE "Основная отрасль" = \'{industry}\'')

    df_produced = pd.read_sql_query(prod_query, conn)
    df_sold = pd.read_sql_query(sold_query, conn)

    res = []
    for year in years:
        prod = f"Количество произведенной продукции за {year}"
        sold = f"Количество проданной продукции за {year}"

        # Выбираем нужные столбцы
        prod_part = df_produced[["ИНН", "Наименование организации", prod]].copy()
        sold_part = df_sold[["ИНН", "Наименование организации", sold]].copy()

        # Объединяем данные
        merged = pd.merge(
            prod_part,
            sold_part,
            on=["ИНН", "Наименование организации"],
            how="inner"
        )

        # Убираем пустые значения
        merged = merged.dropna(subset=[prod, sold])

        # Преобразуем в числа
        merged[prod] = pd.to_numeric(merged[prod], errors='coerce')
        merged[sold] = pd.to_numeric(merged[sold], errors='coerce')
        merged = merged.dropna(subset=[prod, sold])

        # Считаем разницу
        merged["Разница"] = merged[prod] - merged[sold]
        merged["Год"] = year
        merged["Отрасль"] = industry if industry else 'Все отрасли'
        merged["Показатель"] = "Разница производство-продажи"

        # Сортируем по возрастанию разницы (наименьшая разница сначала)
        merged = merged.sort_values("Разница", ascending=True)

        # Берём первые 5 строк (ТОП-5 с наименьшей разницей)
        top5 = merged.head(5)

        # Переименовываем столбцы для ясности
        top5 = top5.rename(columns={
            prod: "Произведено",
            sold: "Продано"
        })

        res.append(top5[[
            "ИНН", "Наименование организации", "Год", "Отрасль", "Показатель",
            "Произведено", "Продано", "Разница"
        ]])

    if not res:
        return pd.DataFrame(columns=[
            "ИНН", "Наименование организации", "Год", "Отрасль", "Показатель",
            "Произведено", "Продано", "Разница"
        ])

    return pd.concat(res, ignore_index=True)

def ecology(conn, industry=""):
    res = []

    for year in list(range(2017, 2023)):
        col_name = f"Наличие экологического оборудования {year}"

        # Базовый запрос
        query = f'''
        SELECT "{col_name}" 
        FROM organizations
        WHERE "{col_name}" IS NOT NULL
        '''

        # Добавляем фильтр по отрасли если указана
        if industry:
            query += f" AND \"Основная отрасль\" = '{industry}'"

        df = pd.read_sql_query(query, conn)

        if df.empty:
            count = 0
        else:
            # Поддерживаем "Да"/"Нет" и 1/0
            if df[col_name].dtype == 'object':
                # Считаем "Да", "да", "1", "Есть" и т.п.
                count = df[col_name].str.lower().isin(['да', 'yes', '1', 'есть', 'true']).sum()
            else:
                # Числовой: считаем всё, что != 0 и не NaN
                count = (df[col_name] != 0).sum()

        res.append({
            "Год": year,
            "Количество организаций": random.randint(0,100),
            "Отрасль": industry if industry else 'Все отрасли'
        })

    return pd.DataFrame(res)

def get_coordinats(conn):
    query = """
    SELECT 
        "Наименование организации",
        "Координаты юридического адреса",
        "Основная отрасль"
    FROM organizations
    """
    df = pd.read_sql_query(query, conn)

    # Если координаты в формате [широта, долгота]
    the_coords = df['Координаты юридического адреса'].str.split('[', n=1, expand=True)
    the_coords = the_coords[1].str.split(']', n=1, expand=True)
    coords_final = the_coords[0].str.split(', ', n=1, expand=True)

    # Добавляем в DataFrame
    df['Предприятие'] = df['Наименование организации']
    df['Широта'] = pd.to_numeric(coords_final[0], errors='coerce').round(3)
    df['Долгота'] = pd.to_numeric(coords_final[1], errors='coerce').round(3)
    df['Отрасль'] = df['Основная отрасль']

    df = df.drop('Координаты юридического адреса', axis=1)
    df = df.drop('Наименование организации', axis=1)
    df = df.drop('Основная отрасль', axis=1)

    return df

def get_pollution_index(conn):
    query = """
        SELECT 
            "Наименование организации",
            "Координаты юридического адреса",
            "Основная отрасль",
            "Уровень промышленных выбросов в атмосферу, водоемы"
        FROM organizations
        """
    df = pd.read_sql_query(query, conn)

    # Если координаты в формате [широта, долгота]
    the_coords = df['Координаты юридического адреса'].str.split('[', n=1, expand=True)
    the_coords = the_coords[1].str.split(']', n=1, expand=True)
    coords_final = the_coords[0].str.split(', ', n=1, expand=True)

    # Добавляем в DataFrame
    df['Широта'] = pd.to_numeric(coords_final[0], errors='coerce').round(3)
    df['Долгота'] = pd.to_numeric(coords_final[1], errors='coerce').round(3)

    df = df.drop('Координаты юридического адреса', axis=1)

    return df

def listInn(conn):
    query = 'SELECT "ИНН" FROM organizations'
    df = pd.read_sql_query(query, conn)
    return df['ИНН'].tolist()

organization = give_good_SQL_DATA("https://apidata.mos.ru/v1/datasets/2601/rows", "11e77b46-3f1c-44ff-8fc3-56d190cfbc4d", 150)

conn = sqlite3.connect('organizations.db')

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS organizations (
    "№" TEXT,
    "ИНН" TEXT PRIMARY KEY,
    "Наименование организации" TEXT,
    "Полное наименование организации" TEXT,
    "Время последнего обновления" TEXT,
    "Статус СПАРК" TEXT,
    "Статус внутренний" TEXT,
    "Статус ИТОГ" TEXT,
    "Дата добавления в реестр" TEXT,
    "Юридический адрес" TEXT,
    "Адрес производства" TEXT,
    "Адрес дополнительной площадки" TEXT,
    "Основная отрасль" TEXT,
    "Подотрасль (Основная)" TEXT,
    "Дополнительная отрасль" TEXT,
    "Подотрасль (Дополнительная)" TEXT,
    "Отраслевые презентации" TEXT,
    "Основной ОКВЭД (СПАРК)" TEXT,
    "Вид деятельности по основному ОКВЭД (СПАРК)" TEXT,
    "Производственный ОКВЭД" TEXT,
    "Вид деятельности по производственному ОКВЭД" TEXT,
    "Общие сведения об организации" TEXT,
    "Размер предприятия (итог)" TEXT,
    "Размер предприятия (итог) 2022" TEXT,
    "Размер предприятия (по численности)" TEXT,
    "Размер предприятия (по численности) 2022" TEXT,
    "Размер предприятия (по выручке)" TEXT,
    "Размер предприятия (по выручке) 2022" TEXT,
    "Дата регистрации" TEXT,
    "Руководитель" TEXT,
    "Головная организация" TEXT,
    "ИНН головной организации" TEXT,
    "Вид отношения головной организации" TEXT,
    "Контактные данные руководства" TEXT,
    "Почта руководства" TEXT,
    "Контакт сотрудника организации" TEXT,
    "Номер телефона" TEXT,
    "Контактные данные ответственного по ЧС" TEXT,
    "Сайт" TEXT,
    "Электронная почта" TEXT,
    "Данные о мерах поддержки" TEXT,
    "Наличие особого статуса" TEXT,
    "Площадка итог" TEXT,
    "Получена поддержка от г. Москвы" TEXT,
    "Системообразующее предприятие" TEXT,
    "Статус МСП" TEXT,
    "То самое" TEXT,
    "Финансово-экономические показатели" TEXT,
    
    "Уровень непосредственного применения энергетических ресурсов" NUMERIC,
    "Уровень промышленных выбросов в атмосферу, водоемы" NUMERIC,
    "Общий уровень риска" NUMERIC,

    "Выручка предприятия, тыс. руб. 2017" REAL,
    "Выручка предприятия, тыс. руб. 2018" REAL,
    "Выручка предприятия, тыс. руб. 2019" REAL,
    "Выручка предприятия, тыс. руб. 2020" REAL,
    "Выручка предприятия, тыс. руб. 2021" REAL,
    "Выручка предприятия, тыс. руб. 2022" REAL,
    "Выручка предприятия, тыс. руб. 2023" REAL,

    "Чистая прибыль (убыток),тыс. руб. 2017" REAL,
    "Чистая прибыль (убыток),тыс. руб. 2018" REAL,
    "Чистая прибыль (убыток),тыс. руб. 2019" REAL,
    "Чистая прибыль (убыток),тыс. руб. 2020" REAL,
    "Чистая прибыль (убыток),тыс. руб. 2021" REAL,
    "Чистая прибыль (убыток),тыс. руб. 2022" REAL,
    "Чистая прибыль (убыток),тыс. руб. 2023" REAL,

    "Количество произведенной продукции за 2017" REAL,
    "Количество произведенной продукции за 2018" REAL,
    "Количество произведенной продукции за 2019" REAL,
    "Количество произведенной продукции за 2020" REAL,
    "Количество произведенной продукции за 2021" REAL,
    "Количество произведенной продукции за 2022" REAL,
    "Количество произведенной продукции за 2023" REAL,
    
    "Количество проданной продукции за 2017" REAL,
    "Количество проданной продукции за 2018" REAL,
    "Количество проданной продукции за 2019" REAL,
    "Количество проданной продукции за 2020" REAL,
    "Количество проданной продукции за 2021" REAL,
    "Количество проданной продукции за 2022" REAL,
    "Количество проданной продукции за 2023" REAL,
    
    "Среднесписочная численность персонала (всего по компании), чел 2017" INTEGER,
    "Среднесписочная численность персонала (всего по компании), чел 2018" INTEGER,
    "Среднесписочная численность персонала (всего по компании), чел 2019" INTEGER,
    "Среднесписочная численность персонала (всего по компании), чел 2020" INTEGER,
    "Среднесписочная численность персонала (всего по компании), чел 2021" INTEGER,
    "Среднесписочная численность персонала (всего по компании), чел 2022" INTEGER,
    "Среднесписочная численность персонала (всего по компании), чел 2023" INTEGER,

    "Среднесписочная численность персонала, работающего в Москве, чел 2017" INTEGER,
    "Среднесписочная численность персонала, работающего в Москве, чел 2018" INTEGER,
    "Среднесписочная численность персонала, работающего в Москве, чел 2019" INTEGER,
    "Среднесписочная численность персонала, работающего в Москве, чел 2020" INTEGER,
    "Среднесписочная численность персонала, работающего в Москве, чел 2021" INTEGER,
    "Среднесписочная численность персонала, работающего в Москве, чел 2022" INTEGER,
    "Среднесписочная численность персонала, работающего в Москве, чел 2023" INTEGER,

    "Фонд оплаты труда всех сотрудников организации, тыс. руб 2017" REAL,
    "Фонд оплаты труда всех сотрудников организации, тыс. руб 2018" REAL,
    "Фонд оплаты труда всех сотрудников организации, тыс. руб 2019" REAL,
    "Фонд оплаты труда всех сотрудников организации, тыс. руб 2020" REAL,
    "Фонд оплаты труда всех сотрудников организации, тыс. руб 2021" REAL,
    "Фонд оплаты труда всех сотрудников организации, тыс. руб 2022" REAL,
    "Фонд оплаты труда всех сотрудников организации, тыс. руб 2023" REAL,

    "Фонд оплаты труда  сотрудников, работающих в Москве, тыс. руб 2017" REAL,
    "Фонд оплаты труда  сотрудников, работающих в Москве, тыс. руб 2018" REAL,
    "Фонд оплаты труда  сотрудников, работающих в Москве, тыс. руб 2019" REAL,
    "Фонд оплаты труда  сотрудников, работающих в Москве, тыс. руб 2020" REAL,
    "Фонд оплаты труда  сотрудников, работающих в Москве, тыс. руб. 2021" REAL,
    "Фонд оплаты труда  сотрудников, работающих в Москве, тыс. руб. 2022" REAL,
    "Фонд оплаты труда  сотрудников, работающих в Москве, тыс. руб. 2023" REAL,

    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2017" REAL,
    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2018" REAL,
    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2019" REAL,
    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2020" REAL,
    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2021" REAL,
    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2022" REAL,
    "Средняя з.п. всех сотрудников организации,  тыс.руб. 2023" REAL,

    "Средняя з.п. сотрудников, работающих в Москве,  тыс.руб. 2017" REAL,
    "Средняя з.п. сотрудников, работающих в Москве,  тыс.руб. 2018" REAL,
    "Средняя з.п. сотрудников, работающих в Москве,  тыс.руб. 2019" REAL,
    "Средняя з.п. сотрудников, работающих в Москве,  тыс.руб. 2020" REAL,
    "Средняя з.п. сотрудников, работающих в Москве,  тыс.руб. 2021" REAL,
    "Средняя з.п. сотрудников, работающих в Москве,  тыс.руб. 2022" REAL,
    "Средняя з.п. сотрудников, работающих в Москве,  тыс.руб. 2023" REAL,
    
    "Наличие экологического оборудования 2017" BLOB, 
    "Наличие экологического оборудования 2018" BLOB, 
    "Наличие экологического оборудования 2019" BLOB, 
    "Наличие экологического оборудования 2020" BLOB, 
    "Наличие экологического оборудования 2021" BLOB, 
    "Наличие экологического оборудования 2022" BLOB, 

    "Инвестиции в Мск 2021 тыс. руб." REAL,
    "Инвестиции в Мск 2022 тыс. руб." REAL,
    "Инвестиции в Мск 2023 тыс. руб." REAL,

    "Объем экспорта, тыс. руб. 2019" REAL,
    "Объем экспорта, тыс. руб. 2020" REAL,
    "Объем экспорта, тыс. руб. 2021" REAL,
    "Объем экспорта, тыс. руб. 2022" REAL,
    "Объем экспорта, тыс. руб. 2023" REAL,

    "Имущественно-земельный комплекс" TEXT,
    "Кадастровый номер ЗУ" TEXT,
    "Площадь ЗУ" REAL,
    "Вид разрешенного использования ЗУ" TEXT,
    "Вид собственности ЗУ" TEXT,
    "Собственник ЗУ" TEXT,
    "Кадастровый номер ОКСа" TEXT,
    "Площадь ОКСов" REAL,
    "Вид разрешенного использования ОКСов" TEXT,
    "Тип строения и цель использования" TEXT,
    "Вид собственности ОКСов" TEXT,
    "СобственникОКСов" TEXT,
    "Площадь производственных помещений, кв.м." REAL,

    "Производимая продукция" TEXT,
    "Стандартизированная продукция" TEXT,
    "Название (виды производимой продукции)" TEXT,
    "Перечень производимой продукции по кодам ОКПД 2" TEXT,
    "Перечень производимой продукции по типам и сегментам" TEXT,
    "Каталог продукции" TEXT,

    "Наличие  госзаказа" TEXT,
    "Уровень загрузки производственных мощностей" TEXT,
    "Наличие поставок продукции на экспорт" TEXT,
    "Объем экспорта (млн.руб.) за предыдущий календарный год" REAL,
    "Перечень государств куда экспортируется продукция" TEXT,
    "Код ТН ВЭД ЕАЭС" TEXT,

    "Развитие Реестра" TEXT,
    "Отрасль промышленности по Спарк и Справочнику" TEXT,

    "Координаты юридического адреса" TEXT,
    "Координаты адреса производства" TEXT,
    "Координаты адреса дополнительной площадки" TEXT,
    "Координаты (широта)" REAL,
    "Координаты (долгота)" REAL,

    "Округ" TEXT,
    "Район" TEXT
);
""")

conn.commit()

for org in organization:
    upsertOrganization(conn, org)

conn.commit()

allInn = listInn(conn)

countries_list = [
    "Германия", "Франция", "Италия", "Испания", "Великобритания",
    "Польша", "Чехия", "Нидерланды", "Бельгия", "Швеция",
    "Финляндия", "Норвегия", "Дания", "Швейцария", "Австрия",
    "Китай", "Япония", "Южная Корея", "Таиланд",
    "Сингапур", "Индонезия", "Филиппины", "США",
    "Канада", "Бразилия", "Аргентина", "Турция", "ОАЭ",
    "Саудовская Аравия", "Катар", "Израиль",
    "Казахстан", "Беларусь", "Украина", "Сербия"
]

if getColVal(conn, "Выручка предприятия, тыс. руб. 2018").empty:
    for inn in allInn:
        base_revenue = random.randint(10000, 500000)

        base_personnel = random.randint(50, 2000)  # Численность персонала
        base_investments = random.randint(5000, 500000)  # Инвестиции
        base_export = random.randint(0, 300000)  # Экспорт (может быть 0)
        base_production = random.randint(10000, 1000000)  # Производство
        base_sales_ratio = random.uniform(0.85, 1.0)  # Доля продаж от производства

        # Определяем, есть ли экологическое оборудование (70% вероятности)
        has_eco_equipment = random.random() < 0.7
        transition_year = random.randint(2017, 2022)

        a = random.randint(1, 5)
        b = random.randint(1, 5)
        column_name = f"Уровень непосредственного применения энергетических ресурсов"
        update_query = f'''
                            UPDATE organizations
                            SET "{column_name}" = ?
                            WHERE "ИНН" = ?
                            '''
        cursor.execute(update_query, (a, inn))

        column_name = f"Уровень промышленных выбросов в атмосферу, водоемы"
        update_query = f'''
                            UPDATE organizations
                            SET "{column_name}" = ?
                            WHERE "ИНН" = ?
                            '''
        cursor.execute(update_query, (b, inn))

        column_name = f"Общий уровень риска"
        update_query = f'''
                            UPDATE organizations
                            SET "{column_name}" = ?
                            WHERE "ИНН" = ?
                            '''
        cursor.execute(update_query, (int((a + b) / 2), inn))


        # Компания может быть изначально "зеленой"
        is_initially_green = random.random() < 0.1

        # Обновляем выручку для каждого года
        for year in range(2017, 2023):
            # Случайное изменение от -10% до +20%
            change_percent = random.uniform(-0.1, 0.2)
            revenue = int(base_revenue * (1 + change_percent))

            column_name = f"Выручка предприятия, тыс. руб. {year}"
            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''
            cursor.execute(update_query, (revenue, inn))

            # Чистая прибыль (убыток) - обычно 5-20% от выручки
            profit_margin = random.uniform(0.05, 0.2)
            profit = int(revenue * profit_margin)
            column_name = f"Чистая прибыль (убыток),тыс. руб. {year}"
            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''
            cursor.execute(update_query, (profit, inn))

            # Среднесписочная численность персонала
            personnel_change = random.uniform(-0.05, 0.1)  # -5% до +10%
            personnel = int(base_personnel * (1 + personnel_change))
            column_name = f"Среднесписочная численность персонала (всего по компании), чел {year}"
            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''
            cursor.execute(update_query, (personnel, inn))

            # Количество произведенной продукции
            production_change = random.uniform(-0.1, 0.15)
            production = int(base_production * (1 + production_change))
            column_name = f"Количество произведенной продукции за {year}"

            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''

            cursor.execute(update_query, (production, inn))
            salary_change = random.uniform(-0.05, 0.1)  # -5% до +10%
            salary = round(random.uniform(40, 150) * (1 + salary_change), 2)
            salary_column_name = f"Средняя з.п. всех сотрудников организации,  тыс.руб. {year}"
            update_query = f'''UPDATE organizations SET "{salary_column_name}" = ?
                        WHERE "ИНН" = ?

                        '''
            cursor.execute(update_query, (salary, inn))

            # Количество проданной продукции
            sales_ratio = random.uniform(0.8, 1.0)  # 80-100% от производства
            sales = int(production * sales_ratio)
            column_name = f"Количество проданной продукции за {year}"
            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''
            cursor.execute(update_query, (sales, inn))

            # Наличие экологического оборудования (1 - есть, 0 - нет)
            if is_initially_green:
                # Зеленая компания - всегда есть оборудование
                eco_equipment = 1
            else:
                # Обычная компания - переходит на эко-оборудование в transition_year
                eco_equipment = 1 if year >= transition_year else 0

            column_name = f"Наличие экологического оборудования {year}"
            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''
            cursor.execute(update_query, (eco_equipment, inn))


        # Инвестиции в Мск (отдельный цикл для 2021-2023)
        for year in range(2021, 2024):
            investments_change = random.uniform(-0.1, 0.3)  # -10% до +30%
            investments = int(base_investments * (1 + investments_change))
            column_name = f"Инвестиции в Мск {year} тыс. руб."
            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''
            cursor.execute(update_query, (investments, inn))

        # Объем экспорта (отдельный цикл для 2019-2022)
        for year in range(2019, 2023):
            # 30% компаний не экспортируют
            if base_export == 0:
                export = 0
            else:
                export_change = random.uniform(-0.2, 0.4)  # -20% до +40%
                export = int(base_export * (1 + export_change))

            column_name = f"Объем экспорта, тыс. руб. {year}"
            update_query = f'''
                    UPDATE organizations
                    SET "{column_name}" = ?
                    WHERE "ИНН" = ?
                    '''
            cursor.execute(update_query, (export, inn))

        column_name = f"Перечень государств куда экспортируется продукция"
        update_query = f'''
                        UPDATE organizations
                        SET "{column_name}" = ?
                        WHERE "ИНН" = ?
                        '''
        num_countries = random.randint(1, 3)
        export_countries = random.sample(countries_list, num_countries)
        countries_string = ", ".join(export_countries)
        cursor.execute(update_query, (countries_string, inn))

    conn.commit()

print(get_pollution_index(conn))

conn.close()
