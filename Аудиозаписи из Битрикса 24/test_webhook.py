import requests
import json

# URL вашего вебхука
url = "http://127.0.0.1:5000/webhook"

# Данные, которые вы хотите отправить
data = {
    "lead_id": "890139",
    "file_url": "1724837812752278-out-977754910-208-20240828-143555-1724837755.931502.wav"
}

# Преобразуем данные в формат JSON
headers = {'Content-Type': 'application/json'}

# Отправляем POST-запрос
response = requests.post(url, headers=headers, data=json.dumps(data))

# Выводим статус-код и ответ сервера
print(f"Статус-код: {response.status_code}")
print(f"Ответ сервера: {response.text}")
import os
import requests
import json
from flask import Flask, request, jsonify
from google.cloud import speech_v1p1beta1 as speech
import openai
import logging

# Установка переменных окружения
os.environ['GOOGLE_CLOUD_API_KEY'] = '551e78be31d04450451e69544848b347594fd2e8'
os.environ['CHATGPT_API_KEY'] = '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'
os.environ['BITRIX24_WEBHOOK_URL'] = 'https://xonsaroy.bitrix24.ru/rest/57183/0t6iw32dow7oykzw'

# Извлечение ключей из переменных окружения
GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY')
BITRIX24_WEBHOOK_URL = os.getenv('BITRIX24_WEBHOOK_URL')

# Проверка на наличие ключей
if not GOOGLE_CLOUD_API_KEY or not CHATGPT_API_KEY or not BITRIX24_WEBHOOK_URL:
    raise EnvironmentError("API keys must be set in environment variables")

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def download_audio_file(file_url):
    response = requests.get(file_url)
    response.raise_for_status()  # Поднимает исключение при ошибке HTTP
    audio_content = response.content
    return audio_content

def transcribe_audio(audio_content):
    url = f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_CLOUD_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": 16000,
            "languageCode": "uz-UZ"
        },
        "audio": {
            "content": audio_content.decode('ISO-8859-1')  # Проверьте корректность кодировки
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    result = response.json()
    transcript = ' '.join(result['results'][0]['alternatives'][0]['transcript'])
    return transcript

def generate_dialogue(transcript):
    openai.api_key = CHATGPT_API_KEY
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Mana qo'ng'iroq matni:\n\n{transcript}\n\nIltimos, ushbu matn asosida mijoz va qo'ng'iroq markazi xodimi o'rtasidagi muloqotni yarating.",
        max_tokens=500
    )
    dialogue = response.choices[0].text.strip()
    return dialogue

def update_bitrix24_lead(lead_id, dialogue):
    url = f"{BITRIX24_WEBHOOK_URL}/crm.lead.update.json"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'ID': lead_id,
        'FIELDS': {
            'COMMENTS': dialogue
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    lead_id = data.get('890139')
    file_url = data.get('file_url')

    if lead_id and file_url:
        logging.debug(f"Received lead_id: {lead_id}, file_url: {file_url}")

        # Шаг 1: Загрузка аудиофайла из Битрикс24
        audio_content = download_audio_file(file_url)
        logging.debug("Audio file downloaded")

        # Шаг 2: Распознавание текста на узбекском языке
        transcript = transcribe_audio(audio_content)
        logging.debug(f"Transcript: {transcript}")

        if transcript:
            # Шаг 3: Генерация диалога на узбекском языке
            dialogue = generate_dialogue(transcript)
            logging.debug(f"Generated dialogue: {dialogue}")

            # Шаг 4: Обновление лида в Bitrix24
            result = update_bitrix24_lead(lead_id, dialogue)
            logging.debug(f"Update result: {result}")
            return jsonify(result)
    return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(port=5000)
# Инструкции по тестированию:
# Замените значения в переменных окружения:

# Замените YOUR_GOOGLE_CLOUD_API_KEY, YOUR_CHATGPT_API_KEY и YOUR_BITRIX24_WEBHOOK_URL на ваши реальные ключи и URL.
# Запустите приложение Flask:

# python your_flask_app.py

# Отправьте тестовый POST-запрос: Используйте инструмент, такой как curl или Postman, чтобы отправить запрос на ваш вебхук:

# curl -X POST http://localhost:5000/webhook \
# -H "Content-Type: application/json" \
# -d '{"lead_id": "890139", "file_url": "1724837812752278-out-977754910-208-20240828-143555-1724837755.931502.wav"}'


