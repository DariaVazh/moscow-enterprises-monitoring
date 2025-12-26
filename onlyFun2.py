import pandas as pd
import datetime
pd.set_option('display.max_columns', None)      # Показывать все столбцы
pd.set_option('display.width', None)            # Автоматическая ширина

# добавление/обновление данных
def upsertOrganization(conn, data):
    if "ИНН" not in data:
        raise ValueError("Каждая запись должна содержать 'ИНН'")

    inn = data["ИНН"]
    updateFields = {k: v for k, v in data.items() if k != "ИНН"}

    currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updateFields["Время последнего обновления"] = currentTime

    if not updateFields: # Только ИНН — просто вставляем пустую запись
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO organizations ("ИНН", "Время последнего обновления") VALUES (?, ?)', (inn, currentTime))
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

# топ 5 с максимальной выручкой
def get5revenue(conn, industry=""):
    years = list(range(2017, 2023))
    revenueCols = [f'Выручка предприятия, тыс. руб. {year}' for year in years]

    # Добавляем название организации и отрасль в запрос
    allCols = ['ИНН', 'Наименование организации', 'Основная отрасль'] + revenueCols
    quotedCols = ', '.join([f'"{col}"' for col in allCols])

    # Базовый запрос
    query = f"SELECT {quotedCols} FROM organizations"

    # Добавляем фильтр по отрасли если указана
    if industry:
        query += f" WHERE \"Основная отрасль\" = '{industry}'"

    df = pd.read_sql_query(query, conn)

    top_revenue_list = []
    for year in years:
        col = f'Выручка предприятия, тыс. руб. {year}'
        # Проверяем, что столбец существует и есть данные
        if col in df.columns and not df[col].isna().all():
            # Берем топ-5 по выручке за текущий год
            top5 = df.nlargest(5, col, keep='all')[['ИНН', 'Наименование организации', col]]
            top5 = top5.rename(columns={col: 'Значение'})
            top5['Год'] = year
            top5['Показатель'] = 'Выручка'
            top5['Отрасль'] = industry if industry else 'Все отрасли'
            top_revenue_list.append(top5)

    if top_revenue_list:
        return pd.concat(top_revenue_list, ignore_index=True)
    else:
        return pd.DataFrame(columns=['ИНН', 'Наименование организации', 'Значение', 'Год', 'Показатель', 'Отрасль'])

# топ 5 с максимальной прибылью
def get5profit(conn, industry=""):
    years = list(range(2017, 2023))
    profitCols = [f'Чистая прибыль (убыток),тыс. руб. {year}' for year in years]

    # Добавляем название организации и отрасль в запрос
    allCols = ['ИНН', 'Наименование организации', 'Основная отрасль'] + profitCols
    quotedCols = ', '.join([f'"{col}"' for col in allCols])

    # Базовый запрос
    query = f"SELECT {quotedCols} FROM organizations"

    # Добавляем фильтр по отрасли если указана
    if industry:
        query += f" WHERE \"Основная отрасль\" = '{industry}'"

    df = pd.read_sql_query(query, conn)

    top_profit_list = []
    for year in years:
        col = f'Чистая прибыль (убыток),тыс. руб. {year}'
        # Проверяем, что столбец существует и есть данные
        if col in df.columns and not df[col].isna().all():
            # Берем топ-5 по прибыли за текущий год
            top5 = df.nlargest(5, col, keep='all')[['ИНН', 'Наименование организации', col]]
            top5 = top5.rename(columns={col: 'Значение'})
            top5['Год'] = year
            top5['Показатель'] = 'Чистая прибыль'
            top5['Отрасль'] = industry if industry else 'Все отрасли'
            top_profit_list.append(top5)

    if top_profit_list:
        return pd.concat(top_profit_list, ignore_index=True)
    else:
        return pd.DataFrame(columns=['ИНН', 'Наименование организации', 'Значение', 'Год', 'Показатель', 'Отрасль'])

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
        SELECT "ИНН", "Наименование организации", "{column}"
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
            industry_list.append(industry if industry else 'Все отрасли')

    # Создаем итоговый DataFrame
    data_num_people = {
        "Год": years_list,
        "ИНН": inn_list,
        "Компания": companies_list,
        "Кол-во сотрудников": staff_count_list,
        "Отрасль": industry_list,
        "Показатель": "Численность персонала"
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
        return pd.DataFrame(
            columns=["Год", "ИНН", "Наименование организации", "Инвестиции (тыс. руб.)", "Отрасль", "Показатель"])

    result_rows = []

    for year, col in year_cols.items():
        # Работаем с копией, чтобы не трогать исходный df
        df_year = df[["ИНН", "Наименование организации", col]].copy()

        # Убираем строки, где инвестиции NULL или NaN
        df_year = df_year.dropna(subset=[col])

        # Преобразуем в числовой тип (на случай, если там строки)
        df_year[col] = pd.to_numeric(df_year[col], errors='coerce')
        df_year = df_year.dropna(subset=[col])

        # Сортируем по убыванию и берём топ-5
        top5 = df_year.nlargest(5, col, keep='all')

        # Преобразуем в нужный формат
        top5 = top5.rename(columns={col: "Инвестиции (тыс. руб.)"})
        top5["Год"] = year
        top5["Отрасль"] = industry if industry else 'Все отрасли'
        top5["Показатель"] = "Инвестиции в Москву"

        result_rows.append(
            top5[["Год", "ИНН", "Наименование организации", "Инвестиции (тыс. руб.)", "Отрасль", "Показатель"]])

    if not result_rows:
        return pd.DataFrame(
            columns=["Год", "ИНН", "Наименование организации", "Инвестиции (тыс. руб.)", "Отрасль", "Показатель"])

    result = pd.concat(result_rows, ignore_index=True)
    return result

# топ 5 по экспорту
def get_top5_exporters_by_year(conn, industry=""):
    year_cols = {
        2019: "Объем экспорта, тыс. руб. 2019",
        2020: "Объем экспорта, тыс. руб. 2020",
        2021: "Объем экспорта, тыс. руб. 2021",
        2022: "Объем экспорта, тыс. руб. 2022"
    }

    # Формируем SELECT-запрос
    select_cols = ['ИНН', 'Наименование организации', 'Основная отрасль'] + list(year_cols.values())
    quoted_cols = ', '.join([f'"{col}"' for col in select_cols])

    # Базовый запрос
    query = f"SELECT {quoted_cols} FROM organizations"

    # Добавляем фильтр по отрасли если указана
    if industry:
        query += f" WHERE \"Основная отрасль\" = '{industry}'"

    df = pd.read_sql_query(query, conn)

    if df.empty:
        return pd.DataFrame(
            columns=["Год", "ИНН", "Наименование организации", "Объем экспорта (тыс. руб.)", "Отрасль", "Показатель"])

    result_rows = []

    for year, col in year_cols.items():
        # Выбираем нужные столбцы и удаляем строки с NaN в этом году
        df_year = df[["ИНН", "Наименование организации", col]].copy()
        df_year = df_year.dropna(subset=[col])

        # Приводим к числовому типу
        df_year[col] = pd.to_numeric(df_year[col], errors='coerce')
        df_year = df_year.dropna(subset=[col])

        # Берём ТОП-5 по убыванию
        top5 = df_year.nlargest(5, col, keep='all')
        top5 = top5.rename(columns={col: "Объем экспорта (тыс. руб.)"})
        top5["Год"] = year
        top5["Отрасль"] = industry if industry else 'Все отрасли'
        top5["Показатель"] = "Объем экспорта"

        result_rows.append(
            top5[["Год", "ИНН", "Наименование организации", "Объем экспорта (тыс. руб.)", "Отрасль", "Показатель"]])

    if not result_rows:
        return pd.DataFrame(
            columns=["Год", "ИНН", "Наименование организации", "Объем экспорта (тыс. руб.)", "Отрасль", "Показатель"])

    result = pd.concat(result_rows, ignore_index=True)
    return result

# топ 5 по максимальным кол-вам стран экспорта
def get_top5_export_countries_count(conn, industry=""):
    # Базовый запрос
    query = '''
        SELECT 
            "ИНН",
            "Наименование организации",
            "Основная отрасль",
            "Перечень государств куда экспортируется продукция"
        FROM organizations
        WHERE "Перечень государств куда экспортируется продукция" IS NOT NULL
          AND TRIM("Перечень государств куда экспортируется продукция") != ''
        LIMIT 5
    '''

    # Добавляем фильтр по отрасли если указана
    if industry:
        query = query.replace('WHERE "Перечень государств', f'WHERE "Основная отрасль" = \'{industry}\' AND "Перечень государств')

    df = pd.read_sql_query(query, conn)

    if df.empty:
        return pd.DataFrame(columns=[
            "ИНН", "Наименование организации", "Отрасль",
            "Перечень государств куда экспортируется продукция", "Количество стран", "Показатель"
        ])

    def count_countries(countries_str):
        if not isinstance(countries_str, str):
            return 0
        if countries_str.lower() == "нет экспорта":
            return 0
        countries = [c.strip() for c in countries_str.split(',') if c.strip()]
        return len(countries)

    df["Количество стран"] = df["Перечень государств куда экспортируется продукция"].apply(count_countries)
    df["Отрасль"] = industry if industry else 'Все отрасли'
    df["Показатель"] = "Количество стран экспорта"

    top5 = df.nlargest(5, "Количество стран", keep='all')

    return top5[[
        "ИНН",
        "Наименование организации",
        "Отрасль",
        "Перечень государств куда экспортируется продукция",
        "Количество стран",
        "Показатель"
    ]].reset_index(drop=True)

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
            WHERE "Основная отрасль" = ?
            ORDER BY "{column}"
            LIMIT 5
            '''
            params = [industry]
        else:
            query = f'''
            SELECT "Наименование организации", "Основная отрасль", "{column}"
            FROM organizations
            ORDER BY "{column}"
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

    # Создаем итоговый DataFrame
    data_num_people = {
        "Год": years_list,
        "Компания": companies_list,
        "Отрасль": industries_list,
        "Средняя з. п.": staff_count_list
    }

    df = pd.DataFrame(data_num_people)
    return df

# 5 с минимальной разницей между кол-вом произведенного товара и кол-вом проданного товара
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
            "Количество организаций": count,
            "Отрасль": industry if industry else 'Все отрасли',
            "Показатель": "Наличие экологического оборудования"
        })

    return pd.DataFrame(res)