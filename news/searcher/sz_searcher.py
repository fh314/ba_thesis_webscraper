from dateutil import parser

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class SZSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        articles = []
        base_url = "https://www.sueddeutsche.de/api/public/search/teasers"
        params = {"term": search_term}

        printed_total_results = False

        while base_url:
            response = session.get(base_url, params=params)
            data = response.json()

            if not printed_total_results:
                total_results = data['total']
                print(f"SZ: Found {total_results} results")
                printed_total_results = True

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
