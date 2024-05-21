import re
from datetime import datetime

from bs4 import BeautifulSoup

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class TazSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):

        def parse_date(raw_date):
            # Remove any HTML entities and non-standard space characters
            raw_date = re.sub(r'[^\d.,:]', ' ', raw_date)  # Replace all non-standard characters with space
            raw_date = re.sub(r'\s+', ' ', raw_date)  # Replace multiple spaces with a single space
            raw_date = raw_date.strip()  # Trim leading and trailing spaces
            return datetime.strptime(raw_date, '%d. %m. %Y, %H:%M')

        base_url = "https://taz.de/!s={}"
        page = 0
        articles = []

        while True:
            url = base_url.format(search_term) + f"/?search_page={page}"
            response = session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            directory = soup.find('ul', role='directory', class_='sectbody news directory')

            if not directory:
                break  # No more pages or directory not found

            # Safely select <li> elements
            list_items = directory.find_all('li', class_=lambda
                cls: cls and 'article' in cls.split() and 'brief' not in cls.split())

            for li in list_items:
                meta = li.find('div', class_='meta')
                date_text = meta.find('li', class_='date').text.strip()
                date = parse_date(date_text)

                link = li.find('a', role='link')
                title = link.find('h3').get_text(strip=True) if link.find('h3') else None
                description = li.find('p', class_='snippet').text.strip() if li.find('p', class_='snippet') else ""
                author = link.find('span', class_='author').text.strip() if link.find('span',
                                                                                      class_='author') else "Unknown"
                article_url = "https://taz.de" + link['href']

                article = NewsArticle(title, article_url, description, author, date, outlet, search_term)
                articles.append(article)

            page += 1

        return articles

