from dateutil import parser

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class WeltSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        articles = []
        base_url = f"https://www.welt.de/api/search/{search_term}"
        offset = 0
        total_results = float('inf')

        printed_total_results = False

        while (offset < (total_results - 10)) and (offset <= 90):
            params = {
                "time": "all-time",
                "offset": offset,
                "type": "article"
            }
            response = session.get(base_url, params=params)
            data = response.json()
            total_results = data.get("totalResults", total_results)

            if not printed_total_results:
                print(f"Welt: Found {total_results} results")
                printed_total_results = True

            for item in data["items"]:
                # print(item)
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
                # else:
                #     print(f"Welt: Found {item['type']} type article")

            # TODO: Debug why welt API says it has 87 results for "Hackbacks" but only shows 21
            if len(data["items"]) == 0:
                break
            offset += len(data["items"])

        return articles
