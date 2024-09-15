from datetime import datetime
import logging

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class SpiegelSearcher(ArticleSearcher):

    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        from news.newsarticle import NewsArticle
        articles = []
        base_url = "https://www.spiegel.de/services/sitesearch/search"
        page = 1
        page_size = 50  # max value is 50

        printed_total_results = False

        # Iterate over all pages until all articles are fetched
        while True:
            params = {
                "segments": "spon,spon_paid,spon_international,mmo,mmo_paid,hbm,hbm_paid,elf,elf_paid",
                "q": search_term_str,
                "page_size": page_size,
                "page": page
            }
            response = session.get(base_url, params=params)
            data = response.json()

            # Check if the request was successful
            if response.status_code != 200:
                logger.warning(f"{outlet.abbr}: Failed to fetch articles"
                               f"Status code: {response.status_code} for url: {response.url}")
                break

            if page > 200:  # seems to be a max given that max page size is 50 and 10000 is the limit for found results
                break

            if not printed_total_results:
                total_results = data["num_results"]
                logger.info(f"Found {total_results} results for \"{search_term_str}\"")
                printed_total_results = True

            # Process each result item
            for item in data["results"]:
                publish_date = datetime.fromtimestamp(item["publish_date"])

                news_article = NewsArticle(
                    title=item["title"],
                    url=item["url"],
                    description=item.get("intro", ""),
                    author="",
                    date=publish_date,
                    news_outlet=outlet,
                    search_term=search_term
                )
                articles.append(news_article)

            # Check if there are more pages to fetch
            if len(data["results"]) < page_size:
                break  # Exit the loop if the number of results is less than the page size

            page += 1  # Increment page number to fetch the next page

        return articles
