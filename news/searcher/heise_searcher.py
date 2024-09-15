from datetime import datetime
import json
import re
from dateutil import parser
import logging

from requests import Request

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class HeiseSearcher(ArticleSearcher):

    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):

        articles = []
        base_url = "https://www.heise.de/suche/query"
        page = 1

        # Iterate over all pages until all articles are fetched
        while True:
            params = {
                'p': page,
                'q': " ".join([f"\"{s}\"" for s in search_term_str.split()])
            }
            req = Request('GET', base_url,
                          params=params
                          )
            prepped = req.prepare()
            prepped.url = (prepped.url).replace("%2B", "+")
            response = session.send(prepped)

            if response.status_code != 200:
                logger.error(f"Failed to retrieve data from Heise API. Status code: {response.status_code}")
                break

            data = response.json()
            hits = data.get('hits', [])

            if not hits:
                break

            # Iterate over each article in the list
            for hit in hits:
                try:
                    article = self.parse_article(hit, outlet, search_term)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Failed to parse article from Heise API: {e}, with json {hit}")

            page += 1

        # Log the number of articles found
        logger.info(f"Found {len(articles)} results for \"{search_term_str}\"")
        return articles

    # Parse the article data from the json response
    def parse_article(self, article_data, outlet, search_term):
        from news.newsarticle import NewsArticle
        title = article_data.get('headline')
        if not title:
            return None

        # Check if the url is a full url, if not add the base url
        url = article_data.get('url', {}).get('url')
        if url and not url.startswith("http"):
            url = f"https://www.heise.de{url}"

        # Extract the author from the article data
        description = article_data.get('synopsis')
        authors = article_data.get('authors', [])
        author = ', '.join(author.get('name', '') for author in authors)

        # Extract the date from the article data
        display_date = article_data.get('displayDate')
        date = parser.parse(display_date).replace(tzinfo=None) if display_date else datetime.utcnow().replace(
            tzinfo=None)

        news_article = NewsArticle(title, url, description, author, date, outlet, search_term)

        return news_article
