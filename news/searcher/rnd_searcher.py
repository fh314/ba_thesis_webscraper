import json

from dateutil import parser

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class RNDSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        base_url = "https://api.queryly.com/json.aspx"
        params = {
            "queryly_key": "779542eeca9144e3",
            "query": search_term,
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
                print(f"{outlet.abbr}: Exception {e} while processing {data}")
                return []

            total_results = json_data["metadata"]["total"]

            if not printedTotalResults:
                print(f"RND: Found {total_results} results")
                printedTotalResults = True

            items = json_data.get('items', [])
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

            if total_retrieved >= total_results:
                break

            params["endindex"] = json_data["metadata"]["endindex"]

        return articles
