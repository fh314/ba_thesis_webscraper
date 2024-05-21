from datetime import datetime

from bs4 import BeautifulSoup

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class FAZSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        base_url = "https://www.faz.net/api/faz-content-search"
        articles = []
        page = 1 #max value is 20
        rows_per_page = 100 #max value
        total_articles_collected = 0

        while True:
            params = {
                "q": search_term,
                "page": page,
                "rows": rows_per_page,
                "sort_by": "date",
                "sort_order": "desc",
                "paid_content": "include"
            }

            response = session.get(base_url, params=params)
            if response.status_code != 200:
                print(f"{outlet.abbr}: Failed to fetch data. "
                      f"Status code: {response.status_code} for url: {response.url}")
                break

            data = response.json()
            num_found = data.get("num_found", 0)
            if page == 1:
                print(f"{outlet.abbr}: Found {num_found} articles for \"{search_term}\"")

            for doc in data.get("docs", []):
                date = datetime.strptime(doc["date"], "%Y-%m-%dT%H:%M:%SZ")
                article = NewsArticle(
                    title=doc["title"],
                    url=doc["url"],
                    description=doc["teaser"],
                    author=doc["author"],
                    date=date,
                    news_outlet=outlet,
                    search_term=search_term
                )
                articles.append(article)
                total_articles_collected += 1

            # Check if we need to paginate further
            if total_articles_collected >= num_found:
                break
            page += 1

            if page > 20: #max value
                break

        return articles