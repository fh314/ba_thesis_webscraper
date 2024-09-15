import json
import html
import re
import logging

from bs4 import BeautifulSoup
from dateutil import parser

from news.searcher.article_searcher import ArticleSearcher

logger = logging.getLogger(__name__)


class RNDSearcher(ArticleSearcher):

    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        from news.newsarticle import NewsArticle
        base_url = "https://api.queryly.com/json.aspx"
        params = {
            # Needs to be extracted from the browser
            "queryly_key": "",
            "query": search_term_str,
            "endindex": 0,
            "batchsize": 99,
            "callback": "searchPage.resultcallback",
            "showfaceted": "true",
            "extendeddatafields": "overline,subheadline,items,creator,section,imageresizer,promo_image",
            "timezoneoffset": -60
        }
        total_retrieved = 0
        articles = []

        printedTotalResults = False

        # Iterate over all pages until all articles are fetched
        while True:
            response = session.get(base_url, params=params)
            data = response.text
            try:
                start = data.index('back({') + 5
                end = data.rindex(');')
                # print(data[start:end])
                json_data = json.loads(data[start:end])
                # print(json_data)
            except Exception as e:
                logger.warning(f"{outlet.abbr}: Exception {e} while processing {data}")
                return []

            total_results = json_data["metadata"]["total"]

            # Log the total number of results
            if not printedTotalResults:
                logger.info(f"RND: Found {total_results} results")
                printedTotalResults = True

            items = json_data.get('items', [])

            # Iterate over each article in the list
            for item in items:
                new_article = NewsArticle(
                    title=item["title"],
                    url="https://www.rnd.de" + item["link"],
                    description=item["description"],
                    author=item.get("creator", "Unknown"),
                    date=parser.parse(item["pubdate"]),
                    news_outlet=outlet,
                    search_term=search_term
                )
                articles.append(new_article)
                total_retrieved += 1

            # Break if all articles have been fetched
            if total_retrieved >= total_results:
                break

            params["endindex"] = json_data["metadata"]["endindex"]

        return articles
