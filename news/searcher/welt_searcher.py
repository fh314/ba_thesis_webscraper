import urllib.parse

from dateutil import parser
import logging

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class WeltSearcher(ArticleSearcher):
    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        from news.newsarticle import NewsArticle
        articles = []
        base_url = f"https://www.welt.de/api/search/{"%20".join([urllib.parse.quote(f'"{word}"') for word in search_term_str.split()])}"
        offset = 0
        total_results = float('inf')

        printed_total_results = False

        # Iterate over all pages until all articles are fetched
        while (offset < (total_results - 10)) and (offset <= 90):
            params = {
                "time": "all-time",
                "offset": offset,
                "type": "article"
            }

            response = session.get(base_url, params=params)
            print(response.text)
            data = response.json()

            total_results = data.get("totalResults", total_results)

            if not printed_total_results:
                logger.info(f"Found {total_results} results for \"{search_term_str}\"")
                printed_total_results = True

            # Process each result item
            for item in data["items"]:

                if item["type"] == "article":
                    article = NewsArticle(
                        title=item["headline"],
                        url=item["url"],
                        description=item.get("intro", ""),
                        author="Unknown",  # Author is not provided in the data
                        date=parser.parse(item["publicationDate"]).replace(tzinfo=None),
                        news_outlet=outlet,
                        search_term=search_term
                    )
                    articles.append(article)

            if len(data["items"]) == 0:
                break
            offset += len(data["items"])

        return articles
