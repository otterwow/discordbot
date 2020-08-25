import requests
from bs4 import BeautifulSoup

easy_news_url = 'https://www3.nhk.or.jp/news/easy/'
easy_news_links = 'https://www3.nhk.or.jp/news/easy/news-list.json?'


# go to the main page and get a link to the latest news article
def get_latest_news_id():
    r = requests.get(easy_news_links).json()[0]
    latest_values = next(iter(r.values()))[0]
    return latest_values['news_id'], latest_values['title']


# get the text contents of the latest news article
def get_latest_news():
    news_id, title = get_latest_news_id()
    url = easy_news_url + news_id + '/' + news_id + '.html'
    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    body = soup.find(class_="article-main__body article-body")
    return title, url, scrape_news(body)


# remove unwanted contents from a news article
def scrape_news(body):
    # remove rt tags
    [rt.decompose() for rt in body.findAll('rt')]
    return body.text
