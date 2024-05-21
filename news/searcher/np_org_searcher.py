from bs4 import BeautifulSoup
from dateutil import parser

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class NporgSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        articles = []
        page = 1

        while True:
            request_url = f"https://netzpolitik.org/page/{page}/?s={search_term}"
            response = session.get(request_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            main_div = soup.find('main', id='main')
            if not main_div or not main_div.find_all('article', class_='teaser'):
                break  # Break if no articles are found or main div is missing

            current_page_articles = 0

            # Iterate over each article tag within the main content area
            for article in main_div.find_all('article', class_='teaser'):
                try:
                    headline_link = article.find('a', class_='teaser__headline-link')
                    title = headline_link.text.strip()
                    url = headline_link['href']
                    excerpt = article.find('div', class_='teaser__excerpt').p.text.strip()
                    author_link = article.find('a', rel='author')
                    author = author_link.text.strip() if author_link else "Unknown Author"
                    time_element = article.find('time', class_='entry-date')
                    if time_element and 'datetime' in time_element.attrs:
                        date = parser.parse(time_element['datetime']).replace(tzinfo=None)
                    else:
                        date = ""

                    # Create an instance of NewsArticle
                    news_article = NewsArticle(title, url, excerpt, author, date, outlet, search_term)
                    articles.append(news_article)
                    current_page_articles += 1
                except Exception as e:
                    print(f"np.org: Exception: {e} for url: {request_url} article: \n{article}\n")
                    continue  # Skip articles throwing excpetions

            if current_page_articles < 20:
                break  # Break if less than batch size, indicating last page
            page += 1

        return articles