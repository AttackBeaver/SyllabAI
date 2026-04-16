"""
Модуль для парсинга файлов тематического плана (.xlsx, .docx)
"""
import pandas as pd
from docx import Document

def parse_excel(uploaded_file):
    """Читает Excel-файл, возвращает DataFrame с колонками: Тип занятия, Часы, Тема."""
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        raise ValueError(f"Ошибка чтения Excel: {e}")

    df.columns = df.columns.str.strip()
    col_map = {}

    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['лекция', 'практика', 'тип']):
            col_map[col] = 'Тип занятия'
        elif 'час' in col_lower:
            col_map[col] = 'Часы'
        elif any(keyword in col_lower for keyword in ['тема', 'содержание']):
            col_map[col] = 'Тема'

    if col_map:
        df = df.rename(columns=col_map)

    df = df.dropna(how='all')
    desired_cols = ['Тип занятия', 'Часы', 'Тема']
    existing_cols = [c for c in desired_cols if c in df.columns]

    if not existing_cols:
        raise ValueError(
            "Не удалось найти колонки с типом занятия, часами и темой. "
            "Убедитесь, что в таблице есть соответствующие заголовки."
        )

    return df[existing_cols]


def parse_docx_table(uploaded_file):
    """Извлекает первую таблицу из документа Word."""
    doc = Document(uploaded_file)
    tables = doc.tables

    if not tables:
        raise ValueError("В документе Word не найдено таблиц.")

    table = tables[0]
    data = []
    keys = None

    for i, row in enumerate(table.rows):
        text = [cell.text.strip() for cell in row.cells]
        if i == 0:
            keys = text
        else:
            data.append(text)

    if not keys:
        raise ValueError("Таблица пуста или не содержит заголовков.")

    df = pd.DataFrame(data, columns=keys)
    df.columns = df.columns.str.strip()
    col_map = {}

    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['лекция', 'практика', 'тип']):
            col_map[col] = 'Тип занятия'
        elif 'час' in col_lower:
            col_map[col] = 'Часы'
        elif any(keyword in col_lower for keyword in ['тема', 'содержание']):
            col_map[col] = 'Тема'

    if col_map:
        df = df.rename(columns=col_map)

    desired_cols = ['Тип занятия', 'Часы', 'Тема']
    existing_cols = [c for c in desired_cols if c in df.columns]

    if not existing_cols:
        raise ValueError(
            "Не удалось найти колонки с типом занятия, часами и темой в таблице Word."
        )

    return df[existing_cols]