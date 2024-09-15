from dateutil import parser
import logging

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class SZSearcher(ArticleSearcher):
    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        from news.newsarticle import NewsArticle
        articles = []
        base_url = "https://www.sueddeutsche.de/api/public/search/teasers"
        params = {"term": search_term_str}

        printed_total_results = False

        # Iterate over all pages until all articles are fetched
        while base_url:
            response = session.get(base_url, params=params)
            data = response.json()

            # Check if the request was successful
            if not printed_total_results:
                total_results = data['total']
                logger.info(f"Found {total_results} results  for \"{search_term_str}\"")
                printed_total_results = True

            # Process each result item
            for item in data["teasers"]:
                content = item["content"]
                # print(content)
                new_article = NewsArticle(
                    title=content["title"],
                    url=content["url"],
                    description=content.get("teaserText", ""),
                    author=content.get("byline", ""),
                    date=parser.parse(content["date"]).replace(tzinfo=None),
                    news_outlet=outlet,
                    search_term=search_term
                )
                articles.append(new_article)

            base_url = data.get("nextTeasersUrl", None)
            params = {}

        return articles
