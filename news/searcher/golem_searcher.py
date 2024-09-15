from datetime import datetime
from bs4 import BeautifulSoup
from news.searcher.article_searcher import ArticleSearcher

import logging

logger = logging.getLogger(__name__)


class GolemSearcher(ArticleSearcher):

    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        from news.newsarticle import NewsArticle
        articles = []
        base_url = "https://suche.golem.de/search.php"
        page = 1
        total_articles_fetched = 0

        # Setup cookies required by the website, need to be manually extracted from the browser
        cookies = {
            'consentUUID': '',
            'euconsent-v2': '',
            'golem_consent20': 'cmp|220101'
        }

        # Iterate over all pages until all articles are fetched
        while True:
            params = {
                'q': search_term_str,
                'l': 10,  # Number of results per page
                's': 1,  # Start index (?)
                'f_abs': 1,
                'bf': 3,
                'p': page  # Current page
            }

            # Fetch the page
            response = session.get(base_url, params=params, cookies=cookies)

            # Check if the request was successful
            if response.status_code != 200:
                logger.warning(f"Failed to fetch data, status code: {response.status_code} for url: {response.url}")
                break

            # Parse the response content
            soup = BeautifulSoup(response.content, 'html.parser')
            article_list = soup.find('ol', class_='list-articles')
            if not article_list:
                break
            header = soup.find('h3', class_='head2')
            total_articles = int(header.text.split()[0]) if header else 0  # Extract total articles count from header

            # Iterate over each article in the list
            if total_articles_fetched >= total_articles:
                break  # Break if no article list is found or all articles have been fetched

            articles_li = article_list.find_all('li')

            # Iterate over each article in the list
            for li in articles_li:
                title_tag = li.find('h2')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                url = li.find('a')['href']
                p_tag = li.find('p')
                date_text = p_tag.find('span', class_='text1')
                date = datetime.strptime(date_text.get_text(strip=True), '(%d.%m.%Y)') if date_text else None

                # Extracting author and description
                author_tag = p_tag.find('em')
                author = author_tag.get_text(strip=True).split('\n')[-1].strip() if author_tag else "Unknown"
                # Remove author text and date text to isolate the description
                if author_tag:
                    author_tag.extract()  # Remove the author element from the paragraph
                if date_text:
                    date_text.extract()  # Remove the date element from the paragraph
                description = p_tag.get_text(separator=" ").strip()

                articles.append(NewsArticle(title, url, description, author, date, outlet, search_term))
                total_articles_fetched += 1

            if len(articles_li) < 10:
                break

            page += 1  # Increment to fetch the next page

        return articles
