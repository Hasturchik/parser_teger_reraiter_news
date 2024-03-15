import requests
from flask import Flask, request
import json

app = Flask(__name__)

api_key = ""  # Замените на ваш ключ API
url_endpoint = "https://api.gen-api.ru/api/v1/networks/chat-gpt-3"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + api_key
}

@app.route("/", methods=['POST'])
def handle_request():
    data = request.get_json()
    text = data['text']
    rewritten_text = rewrite_text_with_openai(text)
    return {'text': rewritten_text}

def rewrite_text_with_openai(text):
    try:
        input_data = {
            "messages": json.dumps([
                {
                    "role": "user",
                    "content": text
                }
            ]),
            "is_sync": True
        }
        response = requests.post(url_endpoint, json=input_data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:  # Обработка возможных исключений
        print(e)
        return 'Ошибка при запросе к API: ' + str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
