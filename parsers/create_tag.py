import json
import re
import requests

api_key = "sk-XenKoMdgZf9RJTpqiTVZrqKJuCrnNhhfO4xVUIjSjfCxt6lsNz19WtZOXaZX"  # Замените на ваш ключ API
url_endpoint = "https://api.gen-api.ru/api/v1/networks/chat-gpt-3"

def rewrite_text_with_gen_api(title, article_text):
    clean_text = re.sub(r'\s+', ' ', title)
    article_text = clean_text
    content = "Отнеси эту новость к одному из представленных тегов. Если ты считаешь, что ни один тег не подходит - отнеси его к тегу другое. Твой ответ должен содержать только название тега. Вот список тегов : Городские новости, События, ЧП/ДТП, Здравоохранение, Туризм и путешествия,Транспорт и инфраструктура, Наука, Семья, В мире, Культура, Недвижимость, Авто, Дети, Технологии и инновации, Бизнес, Экономика, Культура и искусство, Спорт, Еда/продукты/магазины, Образование, Экология, Развлечения и отдых Лайфхаки и советы, Погода. Вот название и текст новости: " + article_text
    print(content)
    input_data = {
        "messages": json.dumps([
            {
                "role": "user",
                "content": content
            }
        ]),
        "is_sync": True
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    try:
        response = requests.post(url_endpoint, json=input_data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
        # return (response.json())
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong with the request", err)
