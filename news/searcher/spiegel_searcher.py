from datetime import datetime

from news.newsarticle import NewsArticle
from news.searcher.article_searcher import ArticleSearcher


class SpiegelSearcher(ArticleSearcher):
    def fetch_articles(self, search_term, session, outlet):
        articles = []
        base_url = "https://www.spiegel.de/services/sitesearch/search"
        page = 1
        page_size = 50  # max value is 50

        printed_total_results = False

        while True:
            params = {
                "segments": "spon,spon_paid,spon_international,mmo,mmo_paid,hbm,hbm_paid,elf,elf_paid",
                "q": search_term,
                "page_size": page_size,
                "page": page
            }
            response = session.get(base_url, params=params)
            data = response.json()

            if response.status_code != 200:
                print(f"{outlet.abbr}: Failed to fetch articles"
                      f"Status code: {response.status_code} for url: {response.url}")
                break

            if page > 200: # seems to be a max given that max page size is 50 and 10000 is the limit for found results
                break

            if not printed_total_results:
                total_results = data["num_results"]
                print(f"Spiegel: Found {total_results} results")
                printed_total_results = True

            # Process each result item
            for item in data["results"]:
                publish_date = datetime.fromtimestamp(item["publish_date"])
                #TODO: Debug why authors dont always work
                # author_names = ', '.join([author["name"] for author in item["authors"]]) if item["authors"] else "Unknown"

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