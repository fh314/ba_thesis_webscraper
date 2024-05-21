from bs4 import BeautifulSoup
from dateutil import parser

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class ZeitSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        base_url = f"https://www.zeit.de/suche/index?q={search_term}&type=article"
        page_number = 1
        articles = []

        while True:
            url = f"{base_url}&p={page_number}"
            response = session.get(url)

            # Check if no more documents are found
            if response.status_code == 404:
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            counter_hits = soup.find('h2', class_='search-counter__hits')

            # If no search results found
            if not counter_hits:
                return "No results found"

            total_results_text = counter_hits.get_text(strip=True)
            total_results = int(total_results_text.split()[0])
            print(f"Zeit: Found {total_results} results")

            article_items = soup.find_all('article', class_='zon-teaser')

            for item in article_items:
                title_elem = item.find('span', class_='zon-teaser__title')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = item.find('a', class_='zon-teaser__link')['href']
                synopsis_elem = item.find('p', class_='zon-teaser__summary')
                synopsis = synopsis_elem.get_text(strip=True) if synopsis_elem else None
                date_str = item.find('time', class_='zon-teaser__datetime')['datetime']
                date = parser.parse(date_str).replace(tzinfo=None)
                author_elem = item.find('span', class_='zon-teaser__author')
                author = author_elem.get_text(strip=True) if author_elem else "Unknown"

                # Create an instance of NewsArticle
                news_article = NewsArticle(title, link, synopsis, author, date, outlet, search_term)
                articles.append(news_article)

            page_number += 1

        return articles
