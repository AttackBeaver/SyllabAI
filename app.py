"""
SyllabAI MVP — Исправление отображения аннотаций
"""
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from utils.parser import parse_excel, parse_docx_table
from utils.llm import generate_annotation

st.set_page_config(page_title="SyllabAI", page_icon="📚", layout="wide")

def convert_df_to_csv_utf8_sig(df):
    return df.to_csv(index=False).encode('utf-8-sig')

# ---------- Инициализация session_state ----------
if 'plan_data' not in st.session_state:
    st.session_state.plan_data = None

# ---------- Интерфейс ----------
st.title("📚 SyllabAI — Помощник преподавателя")
st.markdown("Загрузите тематический план и получите аннотации к занятиям с помощью ИИ.")

with st.sidebar:
    st.header("⚙️ Настройки генерации")
    provider = st.selectbox(
        "ИИ-провайдер",
        ["github", "yandex", "ollama"],
        format_func=lambda x: {
            "github": "GitHub Models (GPT-4o-mini)",
            "yandex": "YandexGPT",
            "ollama": "Ollama (локально)"
        }[x]
    )
    temperature = st.slider("Креативность", 0.0, 1.0, 0.7, 0.1)
    st.markdown("---")
    st.markdown("""
    **Как работать:**
    1. Загрузите Excel или Word с таблицей.
    2. В таблице ниже выберите тему из списка.
    3. Нажмите «Сгенерировать выбранную» или «Все пустые».
    4. Аннотации появятся в колонке «Аннотация».
    5. Скачайте итоговый CSV.
    """)

uploaded_file = st.file_uploader("📎 Загрузите файл темплана", type=["xlsx", "xls", "docx"])

if uploaded_file:
    ext = uploaded_file.name.split('.')[-1].lower()
    try:
        with st.spinner("🔄 Парсинг файла..."):
            if ext in ['xlsx', 'xls']:
                df = parse_excel(uploaded_file)
            else:
                df = parse_docx_table(uploaded_file)

        if 'Тема' in df.columns:
            df = df.dropna(subset=['Тема'])
            df = df[df['Тема'].astype(str).str.strip() != '']

        if 'Аннотация' not in df.columns:
            df['Аннотация'] = ""

        # Инициализируем session_state только один раз при загрузке файла
        if st.session_state.plan_data is None or uploaded_file.name not in st.session_state.get('loaded_file', ''):
            st.session_state.plan_data = df
            st.session_state.loaded_file = uploaded_file.name

        st.success(f"✅ Загружено занятий: {len(st.session_state.plan_data)}")

        # ---------- Отображение таблицы ----------
        st.subheader("📋 Тематический план")
        
        # Используем data_editor с key, изменения будут автоматически отражаться в session_state
        edited_df = st.data_editor(
            st.session_state.plan_data,
            column_config={
                "Аннотация": st.column_config.TextColumn(
                    "Аннотация",
                    help="Сгенерированный текст. Можно редактировать.",
                    width="large"
                ),
                "Тип занятия": st.column_config.TextColumn(width="small"),
                "Часы": st.column_config.TextColumn(width="small"),
                "Тема": st.column_config.TextColumn(width="medium")
            },
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="plan_editor"
        )

        if 'generation_done' not in st.session_state:
            st.session_state.generation_done = False

        if not st.session_state.generation_done:
            st.session_state.plan_data = edited_df
        else:
            # Если была генерация, сбрасываем флаг и не перезаписываем (edited_df может быть старым)
            st.session_state.generation_done = False

        # ---------- Управление генерацией ----------
        st.markdown("---")
        st.subheader("⚡ Генерация аннотаций")

        all_topics = st.session_state.plan_data['Тема'].tolist()
        selected_topic = st.selectbox(
            "Выберите тему для генерации",
            options=[""] + all_topics,
            index=0,
            key="topic_select"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ Сгенерировать для выбранной темы", use_container_width=True):
                if not selected_topic:
                    st.warning("Пожалуйста, выберите тему из списка.")
                else:
                    idx = st.session_state.plan_data[st.session_state.plan_data['Тема'] == selected_topic].index[0]
                    lesson_type = st.session_state.plan_data.at[idx, 'Тип занятия'] if 'Тип занятия' in st.session_state.plan_data.columns else 'Лекция'
                    with st.spinner(f"Генерация: {selected_topic[:50]}..."):
                        try:
                            ann = generate_annotation(
                                topic=selected_topic,
                                lesson_type=lesson_type,
                                provider=provider,
                                temperature=temperature
                            )
                            st.session_state.plan_data.at[idx, 'Аннотация'] = ann
                            st.session_state.generation_done = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка генерации: {e}")

        with col2:
            empty_count = (st.session_state.plan_data['Аннотация'].isna() | (st.session_state.plan_data['Аннотация'] == "")).sum()
            if st.button(f"🚀 Сгенерировать для всех пустых ({empty_count})", use_container_width=True):
                if empty_count == 0:
                    st.info("Все аннотации уже заполнены.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    count_done = 0
                    for idx, row in st.session_state.plan_data.iterrows():
                        if pd.isna(row['Аннотация']) or str(row['Аннотация']).strip() == "":
                            status_text.text(f"Генерация {count_done+1}/{empty_count}: {row['Тема'][:40]}...")
                            try:
                                ann = generate_annotation(
                                    topic=row['Тема'],
                                    lesson_type=row.get('Тип занятия', 'Лекция'),
                                    provider=provider,
                                    temperature=temperature
                                )
                                st.session_state.plan_data.at[idx, 'Аннотация'] = ann
                            except Exception as e:
                                st.warning(f"Ошибка для '{row['Тема']}': {e}")
                            count_done += 1
                            progress_bar.progress(count_done / empty_count)
                    status_text.text("Генерация завершена!")
                    progress_bar.empty()
                    st.session_state.generation_done = True
                    st.rerun()

        # ---------- Просмотр аннотаций ----------
        with st.expander("📝 Просмотреть все аннотации", expanded=False):
            for idx, row in st.session_state.plan_data.iterrows():
                if pd.notna(row['Аннотация']) and str(row['Аннотация']).strip():
                    st.markdown(f"**{row['Тема']}**")
                    st.info(row['Аннотация'])
                    st.divider()

        # ---------- Экспорт ----------
        st.markdown("---")
        st.subheader("💾 Экспорт результата")
        csv_data = convert_df_to_csv_utf8_sig(st.session_state.plan_data)
        st.download_button(
            label="📥 Скачать CSV с аннотациями (UTF-8)",
            data=csv_data,
            file_name=f"themplan_annotated_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        st.caption("Файл в кодировке UTF-8 с BOM — корректно откроется в Excel.")

    except Exception as e:
        st.error(f"❌ Ошибка обработки файла: {e}")
        st.exception(e)
else:
    st.info("👆 Пожалуйста, загрузите файл тематического плана.")