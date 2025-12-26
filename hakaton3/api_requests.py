import os
import sqlite3
import pandas as pd
import json
from datetime import datetime

import requests
import random
def make_api_request(base_url, key, top):

    query_params = {
        "api_key": key,
        "$top": top
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url=base_url,
            params=query_params,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print("Запрос выполнен успешно!")
            print(f"Получено записей: {len(data)}")
            return data
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            return None

    except requests.exceptions.Timeout:
        print("Таймаут запроса")
    except requests.exceptions.ConnectionError:
        print("Ошибка соединения")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


def process_raw_data(raw_data):
    """Обрабатывает сырые данные"""
    print(f"Тип данных: {type(raw_data)}")  # <class 'list'>
    print(f"Количество элементов: {len(raw_data)}")

    # Данные доступны как список словарей
    for item in raw_data[:2]:  # Первые 2 элемента
        print(f"Элемент: {item}")
        print(f"Тип элемента: {type(item)}")  # <class 'dict'>
    return raw_data

def extract_nested_data(raw_data, nested_field, subfields=None):
    """Извлекает данные из вложенных структур"""
    if not raw_data:
        return []

    extracted_data = []

    for item in raw_data:
        nested_data = item.get(nested_field, {})

        if subfields:
            extracted_item = {}
            for field in subfields:
                extracted_item[field] = nested_data.get(field)
            extracted_data.append(extracted_item)
        else:
            extracted_data.append(nested_data)

    return extracted_data

def convert_for_sql(value):
    """Конвертирует значения в SQL-совместимый формат"""
    if value is None:
        return None
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, bool):
        return int(value)  # В SQL обычно 0/1 для boolean
    elif isinstance(value, str):
        # Экранируем кавычки для SQL
        return value.replace("'", "''")
    elif isinstance(value, (list, dict)):
        # Сериализуем сложные структуры в JSON
        import json
        return json.dumps(value, ensure_ascii=False)
    else:
        # Для неизвестных типов преобразуем в строку
        return str(value)

def data_for_SQL_structured(raw_data, desired_fields=None):
    """Подготавливает структурированные данные для SQL с выбранными полями"""
    if not raw_data:
        return []

    # Поля по умолчанию, если не указаны
    if desired_fields is None:
        desired_fields = ['FullName', 'ShortName', 'INN', 'OKPO', 'AdmArea', 'District', 'Category', 'Specialization',
                          'OKVED', 'OKVED_Description', 'Address', 'geoData']

    # Извлекаем только нужные поля из Cells
    cells_data = extract_nested_data(raw_data, 'Cells', desired_fields)

    if not cells_data:
        print("Не удалось извлечь данные из Cells")
        return []

    print(f"Извлечено {len(cells_data)} записей с полями: {desired_fields}")

    # Подготавливаем для SQL
    sql_data = []

    for i, item in enumerate(cells_data):
        sql_item = {}

        for key, value in item.items():
            if value is not None:  # Пропускаем None значения
                sql_item[key] = convert_for_sql(value)

        sql_data.append(sql_item)

    return sql_data

def rename_keys_in_data(data, key_mapping):
    """
    Переименовывает ключи в данных согласно mapping

    Args:
        data: список словарей
        key_mapping: словарь {старый_ключ: новый_ключ}
    """
    if not data:
        return []

    renamed_data = []

    for item in data:
        renamed_item = {}
        for old_key, value in item.items():
            # Используем новый ключ если есть mapping, иначе оставляем старый
            new_key = key_mapping.get(old_key, old_key)
            renamed_item[new_key] = value
        renamed_data.append(renamed_item)

    return renamed_data

countries_list = [
    "Германия", "Франция", "Италия", "Испания", "Великобритания",
    "Польша", "Чехия", "Нидерланды", "Бельгия", "Швеция",
    "Финляндия", "Норвегия", "Дания", "Швейцария", "Австрия",
    "Китай", "Япония", "Южная Корея", "Индия", "Вьетнам",
    "Таиланд", "Малайзия", "Сингапур", "Индонезия", "Филиппины",
    "США", "Канада", "Мексика", "Бразилия", "Аргентина",
    "Чили", "Перу", "Колумбия", "Турция", "ОАЭ",
    "Саудовская Аравия", "Катар", "Израиль", "Египет", "ЮАР",
    "Казахстан", "Беларусь", "Украина", "Азербайджан", "Армения",
    "Узбекистан", "Туркменистан", "Киргизия", "Монголия", "Сербия"
]
def generate_more_data(factories):
    for fac in factories:
        base_revenue = random.randint(10000, 500000)

        # Базовые значения для других показателей
        base_personnel = random.randint(50, 2000)  # Численность персонала
        base_investments = random.randint(5000, 500000)  # Инвестиции
        base_export = random.randint(0, 300000)  # Экспорт (может быть 0)
        base_production = random.randint(10000, 1000000)  # Производство
        base_sales_ratio = random.uniform(0.85, 1.0)  # Доля продаж от производства

        # Определяем, есть ли экологическое оборудование (70% вероятности)
        has_eco_equipment = random.random() < 0.7

        # Компания может быть изначально "зеленой"
        is_initially_green = random.random() < 0.
        transition_year = random.randint(2017, 2022)

        # Обновляем выручку для каждого года
        for year in range(2017, 2023):
            # Случайное изменение от -10% до +20%
            change_percent = random.uniform(-0.1, 0.2)
            revenue = int(base_revenue * (1 + change_percent))

            column_name = f"Выручка предприятия, тыс. руб. {year}"

            fac[column_name] = revenue

            # Чистая прибыль (убыток) - обычно 5-20% от выручки
            profit_margin = random.uniform(0.05, 0.2)
            profit = int(revenue * profit_margin)
            column_name = f"Чистая прибыль (убыток),тыс. руб. {year}"

            fac[column_name] = profit

            # Среднесписочная численность персонала
            personnel_change = random.uniform(-0.05, 0.1)  # -5% до +10%
            personnel = int(base_personnel * (1 + personnel_change))
            column_name = f"Среднесписочная численность персонала (всего по компании), чел {year}"

            fac[column_name] = personnel

            # Количество произведенной продукции
            production_change = random.uniform(-0.1, 0.15)
            production = int(base_production * (1 + production_change))
            column_name = f"Количество произведенной продукции за {year}"

            fac[column_name] = production

            # Количество проданной продукции
            sales_ratio = random.uniform(0.8, 1.0)  # 80-100% от производства
            sales = int(production * sales_ratio)
            column_name = f"Количество проданной продукции за {year}"

            fac[column_name] = sales

            if is_initially_green:
                # Зеленая компания - всегда есть оборудование
                eco_equipment = 1
            else:
                # Обычная компания - переходит на эко-оборудование в transition_year
                eco_equipment = 1 if year >= transition_year else 0
            column_name = f"Наличие экологического оборудования {year}"
            fac[column_name] = eco_equipment

        # Инвестиции в Мск (отдельный цикл для 2021-2023)
        for year in range(2021, 2024):
            investments_change = random.uniform(-0.1, 0.3)  # -10% до +30%
            investments = int(base_investments * (1 + investments_change))
            column_name = f"Инвестиции в Мск {year} тыс. руб."
            fac[column_name] = investments

        # Объем экспорта (отдельный цикл для 2019-2022)
        for year in range(2019, 2023):
            # 30% компаний не экспортируют
            if base_export == 0:
                export = 0
            else:
                export_change = random.uniform(-0.2, 0.4)  # -20% до +40%
                export = int(base_export * (1 + export_change))

            column_name = f"Объем экспорта, тыс. руб. {year}"

            fac[column_name] = export

        a = random.randint(1, 5)
        b = random.randint(1, 5)
        fac['Уровень непосредственного применения энергетических ресурсов'] = a
        fac['Уровень промышленных выбросов в атмосферу, водоемы'] = b
        fac['Общий уровень риска'] = int((a + b) / 2)

        column_name = f"Перечень государств куда экспортируется продукция"

        num_countries = random.randint(1, 8)
        export_countries = random.sample(countries_list, num_countries)
        countries_string = ", ".join(export_countries)
        fac[column_name] = countries_string


    return factories


def check_key_in_any_dict(data_list, key_to_check):
    """Проверяет есть ли ключ хотя бы в одном словаре списка"""

    if not isinstance(data_list, list) or len(data_list) == 0:
        print("❌ Список пустой или не является списком")
        return False

    # Проверяем наличие ключа в каждом словаре
    for i, item in enumerate(data_list):
        if isinstance(item, dict) and key_to_check in item:
            print(f"✅ Ключ '{key_to_check}' найден в элементе {i}")
            print(f"   Значение: {item[key_to_check]}")
            return True

    print(f"❌ Ключ '{key_to_check}' не найден ни в одном элементе")
    return False

def give_good_SQL_DATA(url, key, top):
    # Выполняем API запрос
    result = make_api_request(url, key, top)

    if not result:
        print("Не удалось получить данные от API")
        return

    # Обрабатываем сырые данные
    raw_data = process_raw_data(result)

    # Подготавливаем данные для SQL
    sql_ready_data = data_for_SQL_structured(raw_data)

    KEY_MAPPING = {
        # Прямые соответствия из изначальных ключей
        'INN': 'ИНН',
        'FullName': 'Полное наименование организации',
        'ShortName': 'Наименование организации',
        'OKPO': '№',  # Предположительно, так как OKPO часто используется как номер
        'AdmArea': 'Округ',
        'District': 'Район',
        'Category': 'Основная отрасль',
        'Specialization': 'Подотрасль (Основная)',
        'OKVED': 'Основной ОКВЭД (СПАРК)',
        'OKVED_Description': 'Вид деятельности по основному ОКВЭД (СПАРК)',
        'Address': 'Юридический адрес',
        'geoData': 'Координаты юридического адреса',
    }

    return rename_keys_in_data(sql_ready_data, KEY_MAPPING)