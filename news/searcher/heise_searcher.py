from bs4 import BeautifulSoup
from dateutil import parser

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class HeiseSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        base_url = "https://www.heise.de/suche/"
        params = {
            'q': search_term,
            'sort_by': 'date',
            'make': '',
            'offset': 0
        }
        response = session.get(base_url, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')

        total_results_div = soup.find('div', class_='search-form__total')
        if total_results_div:
            total_results = int(total_results_div.text.strip().replace(".", "").split()[0])
            print(f"Heise: Found {total_results} results")
            pages = (total_results + 19) // 20
        else:
            return "No results found"

        articles = []
        for page in range(pages):
            params['offset'] = page * 20
            response = session.get(base_url, params=params)
            soup = BeautifulSoup(response.content, 'html.parser')
            article_div = soup.find('div', class_='article-index')

            if not article_div:
                continue

            for raw_article in article_div.find_all('article', class_='a-article-teaser'):
                title = raw_article.find('h1', class_='a-article-teaser__title').get_text(strip=True, separator=" ")
                link = raw_article.find('a', class_='a-article-teaser__link')['href']
                synopsis = raw_article.find('p', class_='a-article-teaser__synopsis').get_text(strip=True, separator=" ")
                date = parser.parse(raw_article.find('time', class_='a-datetime')['datetime']).replace(tzinfo=None)
                author = "Unknown"
                news_outlet = outlet

                # Create an instance of NewsArticle
                news_article = NewsArticle(title, link, synopsis, author, date, news_outlet, search_term)
                articles.append(news_article)

        return articles
