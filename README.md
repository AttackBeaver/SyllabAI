# 📚 SyllabAI — Интеллектуальный помощник преподавателя

**SyllabAI** — это веб-приложение на базе Streamlit, которое автоматизирует подготовку тематических планов занятий. Загрузите файл с темпланом (Excel или Word), и нейросеть сгенерирует краткие аннотации для каждой темы.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ Возможности (MVP)

- 📂 **Загрузка темпланов** из Excel (.xlsx, .xls) и Word (.docx)
- 🧠 **Автоматическое распознавание** колонок: Тип занятия, Часы, Тема
- 🤖 **Генерация аннотаций** с помощью ИИ (поддерживаются GitHub Models, YandexGPT, Ollama)
- ✏️ **Редактирование** данных прямо в интерфейсе
- 📥 **Экспорт результатов** в CSV

### 🎯 Гибкая генерация аннотаций

- **Построчная генерация** — нажмите ⚡ рядом с нужной темой.
- **Выборочная генерация** — отметьте несколько тем в списке и нажмите «Сгенерировать выбранные».
- **Массовая генерация** — кнопка «Сгенерировать ВСЕ темы» обработает весь план.

Все аннотации сохраняются в таблице и могут быть экспортированы в CSV.

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/syllabai.git
cd syllabai
```

### 2. Создайте виртуальное окружение и установите зависимости

```bash
python -m venv venv
source venv/bin/activate      # для Linux/Mac
venv\Scripts\activate         # для Windows
pip install -r requirements.txt
```

### 3. Настройте ключи API

Создайте файл .env в корне проекта и добавьте токен одного из провайдеров:

GitHub Models (рекомендуется для старта):

```text
GITHUB_TOKEN=ghp_ваш_персональный_токен
Как получить токен: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic). Достаточно создать токен без дополнительных разрешений.
```

### 4. Запустите приложение

```bash
streamlit run app.py
```

Откройте браузер по адресу <http://localhost:8501>.

### 📁 Структура проекта

```text
syllabai/
├── .env.example            # Пример файла с переменными окружения
├── .gitignore              # Исключения для Git
├── app.py                  # Основное приложение Streamlit
├── requirements.txt        # Зависимости Python
├── README.md               # Документация
├── utils/
│   ├── __init__.py
│   ├── parser.py           # Парсинг Excel и Word
│   └── llm.py              # Взаимодействие с ИИ-провайдерами
└── samples/                # Примеры файлов темпланов
```

### 🛠️ Используемые технологии

Frontend: Streamlit

Парсинг файлов: pandas, openpyxl, python-docx

ИИ-провайдеры:

GitHub Models (GPT-4o-mini)

YandexGPT

Ollama (локальные модели)

### 📝 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле LICENSE.

### 🤝 Вклад в проект

Идеи и пул-реквесты приветствуются! Если вы нашли ошибку или хотите предложить улучшение, создайте Issue.
