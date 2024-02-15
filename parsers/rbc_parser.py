import requests
from bs4 import BeautifulSoup
import json
from create_tag import rewrite_text_with_gen_api


# URL веб-страницы и API-конечной точки
url = 'https://www.rbc.ru/gorod/'
api_endpoint = 'https://mosmap.bpium.ru/api/webrequest/parsers?token=123qwe'

# Функция для получения содержимого новости
def get_news_content(news_url):
    resp = requests.get(news_url)
    if resp.status_code == 200:
        news_soup = BeautifulSoup(resp.content, "html.parser")
        content_blocks = news_soup.select('.article__text')
        article_text = ' '.join(block.get_text().strip() for block in content_blocks)
        return article_text if article_text else "Содержимое не найдено"
    else:
        return "Ошибка при получении страницы: {}".format(resp.status_code)

# Отправляем GET-запрос и получаем HTML страницы
page = requests.get(url)

if page.status_code == 200:
    soup = BeautifulSoup(page.content, 'html.parser')

    # Поиск всех элементов с ссылками на статьи
    articles = soup.find_all('a', class_="item__link rm-cm-item-link js-rm-central-column-item-link")

    articles_data = []  # Список для хранения данных статей

    # Загрузка существующих статей из JSON-файла
    try:
        with open('rbc_parser.json', 'r') as file:
            existing_articles = json.load(file)
    except FileNotFoundError:
        existing_articles = []

    for article in articles:
        link = article.get('href')  # Получаем ссылку на полный текст статьи

        # Переходим по ссылке каждой статьи
        article_page = requests.get(link)
        article_soup = BeautifulSoup(article_page.content, 'html.parser')

        # Ищем текст статьи
        article_text = get_news_content(link)

        # Ищем изображение
        image_tag = article_soup.select_one('.article__main-image__wrap img')
        image_src = image_tag['src'] if image_tag else 'Изображение отсутствует'

        # Ищем заголовок статьи, используя класс 'article__header__title-in'
        title_tag = article_soup.select_one('.article__header__title-in')
        title = title_tag.get_text(strip=True) if title_tag else 'Заголовок отсутствует'
        # Проверяем, есть ли статья в existing_articles
        if any(article['title'] == title for article in existing_articles):
            continue  # Переход к следующей итерации цикла

        # проставляем теги
        news_tag = rewrite_text_with_gen_api(title, article_text)

        #проверяем, мб сервер чат гпт прилег
        if news_tag == "Ошибка при запросе к OpenAI: 'choices'":
            continue  # Переходим к следующей итерации цикла

        # Добавляем данные в список как словарь
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

    headers = {'Content-Type': 'application/json'}  # Устанавливаем заголовок для JSON данных

    # Отправляем список словарей в формате JSON
    response = requests.post(api_endpoint, data=json.dumps(articles_data), headers=headers)

    if response.status_code != 200:
        print(f"Ошибка при отправке данных на API: {response.status_code}")

    existing_articles.extend(articles_data)

    # Записываем данные в файл
    with open('rbc_parser.json', 'w') as file:
        json.dump(existing_articles, file)

    print(articles_data)
    # Печатаем ответ сервера
    print(response.text)

else:
    print("Ошибка при получении страницы:", page.status_code)
