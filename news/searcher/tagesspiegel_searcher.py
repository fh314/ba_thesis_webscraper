import html

from bs4 import BeautifulSoup
from dateutil import parser
import logging

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class TagesspiegelSearcher(ArticleSearcher):

    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        from news.newsarticle import NewsArticle
        base_url = "https://background.tagesspiegel.de/suche"
        articles = []
        page = 0

        # Iterate over all pages until all articles are fetched
        while True:
            params = {
                'text': "+".join([f"\"{s}\"" for s in search_term_str.split()]),
                'page': page
            }
            response = session.get(base_url, params=params)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check if the request was successful
            if page == 0:
                total_results_elem = soup.find('h2', class_='ts-type-alt-bold-xxxl')
                if total_results_elem:
                    total_results_text = total_results_elem.get_text(strip=True)
                    total_results = int(total_results_text.split()[0])
                    logger.info(f"Found {total_results} results for \"{search_term_str}\"")

            # Check if the search results are found
            search_results = soup.find('ul', class_='ts-list list-unstyled')
            if not search_results:
                logger.info(f"No search results found for \"{search_term_str}\"")
                break

            # Iterate over each article in the list
            if search_results.find_all('div', class_='py-5'):
                for result in search_results.find_all('div', class_='py-5'):
                    title_elem = result.find('span', class_='ts-type-alt-bold-lg')
                    if title_elem:

                        link = ""
                        synopsis = ""
                        date = ""
                        author = ""

                        title = title_elem.text.strip()

                        link_elem = result.find('a', class_='ts-list-item-link')
                        if link_elem:
                            link = "https://background.tagesspiegel.de" + link_elem['href']

                        synopsis_elem = result.find('p', class_='ts-type-teaser')
                        if synopsis_elem:
                            synopsis = synopsis_elem.text.strip()

                        date_elem = result.find('p', class_='ts-type-date')
                        if date_elem:
                            date_str = date_elem.text.strip()
                            date = parser.parse(timestr=date_str, dayfirst=True)

                        author_elem = result.find('p', class_='ts-type-author')
                        if author_elem:
                            author = author_elem.text.strip().replace('von', '').strip()

                        # Create an instance of NewsArticle
                        news_article = NewsArticle(title, link, synopsis, author, date, outlet, search_term)
                        articles.append(news_article)
            else:
                break

            # Move to the next page
            page += 1

        return articles
