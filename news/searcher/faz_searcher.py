from datetime import datetime
import logging

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class FAZSearcher(ArticleSearcher):

    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):

        # extracts NewsArticle object from json object, see docs/examples/faz_article.json for example
        def extract_article_information(json, outlet_val, search_term_val):
            # internal import to prevent circular dependency
            from news.newsarticle import NewsArticle

            # extract date from json string looking like this "2024-05-23T12:47:40Z"
            date = datetime.strptime(json["date"], "%Y-%m-%dT%H:%M:%SZ")

            # return news article
            return NewsArticle(
                title=json["title"],
                # use "canonical_url" instead of "url" to prevent faz-archive urls
                url=json["canonical_url"],
                description=json["teaser"],
                author=json["author"],
                date=date,
                news_outlet=outlet_val,
                search_term=search_term_val
            )

        # base url of faz search-API
        base_url = "https://www.faz.net/api/faz-content-search"
        articles = []
        page = 1  # max value is 20

        total_articles_collected = 0

        # iterate for pagination and only abort if page 20 (API-limit) is reached or all results were found
        while True:
            params = {
                "q": search_term_str,
                "page": page,
                "rows": 100,  # max value to reduce number of total requests
                "sort_by": "date",
                "sort_order": "desc",
                "paid_content": "include"
            }

            # get response for url and parameters
            response = ArticleSearcher.get_page(base_url, params, None, session, logger)

            # if no response, skip to the next page
            if not response:
                page += 1
                continue

            # extract json from response
            data = response.json()

            # extract number of found results from json response
            num_found = data.get("num_found", 0)

            # in first iteration of while loop, log total number of results found
            if page == 1:
                logger.info(f"Found {num_found} articles for \"{search_term_str}\"")

            # API can be used to retrieve a maximum of 2000 articles (20 pages a 100 results),
            # warn if more results were found. This shouldn't be a problem in most cases, because
            # the results are sorted in descending order by date, so only older articles get lost.
            if num_found >= 2000:
                logger.warning(f"Number of found articles: {num_found} exceeds API-limit of 2000 articles")

            # for every article found in json, extract NewsArticle object
            for doc in data.get("docs", []):
                # catch errors when dealing with "dirty" data
                try:
                    article = extract_article_information(doc, outlet, search_term)
                    articles.append(article)
                    total_articles_collected += 1
                except Exception as error:
                    logger.error(f"Error: {error} occurred while extracting article information from json: {doc}")

            # increase page number for next iteration
            page += 1

            # check if we need to paginate further, abort if all articles have been collected
            # or page 20 has been reached
            if (total_articles_collected >= num_found) or (page > 20):
                break

        return articles
