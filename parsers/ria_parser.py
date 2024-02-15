import requests
from bs4 import BeautifulSoup
import json
from create_tag import rewrite_text_with_gen_api

# URL веб-страницы и API-конечной точки
url = 'https://ria.ru/location_Moskva/'
api_endpoint = 'https://mosmap.bpium.ru/api/webrequest/parsers?token=123qwe'

def get_article_content(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        article_soup = BeautifulSoup(response.content, "html.parser")
        article_text_parts = article_soup.select('.article__text')
        article_text = ' '.join(part.get_text(strip=True) for part in article_text_parts)
        return article_text if article_text else "Содержимое не найдено"
    else:
        return "Ошибка при получении страницы: {}".format(response.status_code)

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all('a', class_="list-item__title color-font-hover-only")

    articles_data = []  # Список для хранения данных статей

    # Загрузка существующих статей из JSON-файла
    try:
        with open('ria_parser.json', 'r') as file:
            existing_articles = json.load(file)
    except FileNotFoundError:
        existing_articles = []

    for article in articles:
        title = article.get_text(strip=True)
        link = article.get('href')

        # Проверяем, есть ли статья в existing_articles
        if any(existing_article['title'] == title for existing_article in existing_articles):
            continue  # Переход к следующей итерации цикла

        article_text = get_article_content(link)

        # Ищем изображение
        image_tag = soup.select_one('.photoview__open img')
        image_src = image_tag.get('src') if image_tag else 'Изображение отсутствует'

        # проставляем теги
        news_tag = rewrite_text_with_gen_api(title, article_text)

        # вдруг чат гпт лежит
        if news_tag == "Ошибка при запросе к OpenAI: 'choices'":
            continue  # Переходим к следующей итерации цикла

        articles_data.append({
            'title': title,
            'text': article_text,
            'image': image_src,
            "news_tag": news_tag,
            "news_url": link,
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
    with open('ria_parser.json', 'w') as file:
        json.dump(existing_articles, file)

    print(articles_data)
    # Печатаем ответ сервера
    print(response.text)

else:
    print("Ошибка при получении страницы:", response.status_code)
