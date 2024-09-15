from bs4 import BeautifulSoup
from dateutil import parser
import logging

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class ZeitSearcher(ArticleSearcher):
    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        from news.newsarticle import NewsArticle
        base_url = f"https://www.zeit.de/suche/index?q={search_term_str}&type=article"
        page_number = 1
        articles = []

        printed_total_results = False

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
                logger.info(f"Zeit: Found no results for \"{search_term_str}\"")
                return []

            # Extract total results count
            if not printed_total_results:
                total_results_text = counter_hits.get_text(strip=True)
                try:
                    total_results = int(total_results_text.split()[0].replace(".", ""))
                    logger.info(f"Zeit: Found {total_results} results for \"{search_term_str}\"")
                except ValueError:
                    logger.info(f"Zeit: Found no results for \"{search_term_str}\", message:\"{total_results_text}\"")
                    break
                printed_total_results = True

            article_items = soup.find_all('article', class_='zon-teaser')

            if not article_items:
                break

            # Iterate over each article in the list
            for item in article_items:
                title_elem = item.find('span', class_='zon-teaser__title')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = item.find('a', class_='zon-teaser__link')['href']
                synopsis_elem = item.find('p', class_='zon-teaser__summary')
                synopsis = synopsis_elem.get_text(strip=True) if synopsis_elem else None
                date_element = item.find('time', class_='zon-teaser__datetime')
                date_str = date_element['datetime'] if date_element else None
                date = parser.parse(date_str).replace(tzinfo=None) if date_str else ""
                author_elem = item.find('span', class_='zon-teaser__author')
                author = author_elem.get_text(strip=True) if author_elem else "Unknown"

                # Create an instance of NewsArticle
                news_article = NewsArticle(title, link, synopsis, author, date, outlet, search_term)
                articles.append(news_article)

            page_number += 1

        return articles
