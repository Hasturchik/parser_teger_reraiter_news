import requests
from bs4 import BeautifulSoup
import json
from create_tag import rewrite_text_with_gen_api

# Отправляем GET-запрос на страницу с новостями
url = "https://news.rambler.ru/"
response = requests.get(url)

# API-конечная точка для отправки данных
api_endpoint = 'https://mosmap.bpium.ru/api/webrequest/parsers?token=123qwe'

def get_news_content(news_url):
    resp = requests.get(news_url)
    if resp.status_code == 200:
        news_soup = BeautifulSoup(resp.content, "html.parser")
        content_blocks = news_soup.find_all("div", {"class": "_17zPo"})
        article_text = ' '.join(block.get_text().strip() for block in content_blocks)
        return article_text if article_text else "Содержимое не найдено"
    else:
        return "Ошибка при получении страницы: {}".format(resp.status_code)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    news_blocks = soup.find_all("div", class_="_4Niiv")

    articles_data = []  # Список для хранения данных статей

    # Загрузка существующих статей из JSON-файла
    try:
        with open('rambler_parser.json', 'r') as file:
            existing_articles = json.load(file)
    except FileNotFoundError:
        existing_articles = []

    for block in news_blocks:
        headline = block.find("div", class_="_2C1Rd")
        news_a = block.find('a')
        image = block.find('img', class_="_3hvpU")

        if headline and news_a and image:
            title = headline.text.strip()
            news_url = news_a['href']
            image_url = image.get('srcset').split(", ")[0].split(" ")[0] if image.get('srcset') else image.get('src')
            image_url = image_url if image_url.startswith('http') else 'https:' + image_url

            # Проверяем, есть ли статья в existing_articles
            if any(article['title'] == title for article in existing_articles):
                continue  # Переход к следующей итерации цикла

            article_text = get_news_content(news_url)

            # проставляем теги
            news_tag = rewrite_text_with_gen_api(title, article_text)

            # вдруг чат гпт лежит
            if news_tag == "Ошибка при запросе к OpenAI: 'choices'":
                continue  # Переходим к следующей итерации цикла

            articles_data.append({
                'title': title,
                'text': article_text,
                'image': image_url,
                "news_tag": news_tag,
                "news_url": news_url,
                "site_name": url
            })

            # Проверяем, что в файле не больше 20 записей. Если больше, удаляем лишние
            if len(existing_articles) + len(articles_data) > 20:
                existing_articles = existing_articles[-(20 - len(articles_data)):]  # Оставляем только последние 20 значений

    if not articles_data:
        pass

    headers = {'Content-Type': 'application/json'}  # Заголовки запроса

    # Сериализуем данные в JSON и отправляем POST-запрос на API
    response = requests.post(api_endpoint, headers=headers, json=articles_data)

    if response.status_code != 200:
        print(f"Ошибка при отправке данных на API: {response.status_code}")

    existing_articles.extend(articles_data)

    # Записываем данные в файл
    with open('rambler_parser.json', 'w') as file:
        json.dump(existing_articles, file)

    print(articles_data)
    # Печатаем ответ сервера
    print(response.text)

else:
    print("Ошибка при получении страницы:", response.status_code)
