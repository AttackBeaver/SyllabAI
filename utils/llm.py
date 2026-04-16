# utils/llm.py
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PROVIDERS = {
    "github": {
        "base_url": "https://models.inference.ai.azure.com",
        "api_key": os.getenv("GITHUB_TOKEN"),
        "model": "gpt-4o-mini"
    },
    "yandex": {
        "base_url": "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        "folder_id": os.getenv("YANDEX_FOLDER_ID"),
        "iam_token": os.getenv("YANDEX_IAM_TOKEN"),
        "model": "yandexgpt/latest"
    },
    "ollama": {
        "base_url": "http://localhost:11434/api/chat",
        "model": "llama3"
    }
}

def generate_annotation(topic: str, lesson_type: str, provider: str = "github", temperature: float = 0.7) -> str:
    """Генерирует аннотацию занятия с помощью выбранного провайдера."""
    if provider == "github":
        return _generate_with_github(topic, lesson_type, temperature)
    elif provider == "yandex":
        return _generate_with_yandex(topic, lesson_type, temperature)
    elif provider == "ollama":
        return _generate_with_ollama(topic, lesson_type, temperature)
    else:
        raise ValueError(f"Неизвестный провайдер: {provider}")

def _generate_with_github(topic: str, lesson_type: str, temperature: float) -> str:
    client = OpenAI(
        base_url=PROVIDERS["github"]["base_url"],
        api_key=PROVIDERS["github"]["api_key"]
    )
    prompt = (
        f"Ты — ассистент преподавателя вуза/колледжа. Напиши краткую аннотацию (3-5 предложений) "
        f"о том, что должно содержаться в занятии типа '{lesson_type}' по теме '{topic}'. "
        f"Укажи ключевые понятия и ожидаемые результаты обучения. Отвечай только по-русски."
    )
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Ты — эксперт по разработке учебных программ."},
            {"role": "user", "content": prompt}
        ],
        model=PROVIDERS["github"]["model"],
        temperature=temperature,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def _generate_with_yandex(topic: str, lesson_type: str, temperature: float) -> str:
    prompt = {
        "modelUri": f"gpt://{PROVIDERS['yandex']['folder_id']}/{PROVIDERS['yandex']['model']}",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": "500"
        },
        "messages": [
            {"role": "system", "text": "Ты — эксперт по разработке учебных программ."},
            {"role": "user", "text": (
                f"Напиши краткую аннотацию (3-5 предложений) о том, что должно содержаться "
                f"в занятии типа '{lesson_type}' по теме '{topic}'. Укажи ключевые понятия. На русском."
            )}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PROVIDERS['yandex']['iam_token']}"
    }
    response = requests.post(PROVIDERS["yandex"]["base_url"], json=prompt, headers=headers)
    response.raise_for_status()
    return response.json()["result"]["alternatives"][0]["message"]["text"].strip()

def _generate_with_ollama(topic: str, lesson_type: str, temperature: float) -> str:
    prompt = (
        f"Напиши краткую аннотацию (3-5 предложений) о том, что должно содержаться "
        f"в занятии типа '{lesson_type}' по теме '{topic}'. На русском языке."
    )
    response = requests.post(
        PROVIDERS["ollama"]["base_url"],
        json={
            "model": PROVIDERS["ollama"]["model"],
            "messages": [
                {"role": "system", "content": "Ты — эксперт по учебным программам."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": temperature}
        }
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()