import logging
from datetime import timedelta, datetime

import requests_cache
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from news.newsoutlet import NewsOutlet
from news.newsarticle import Base as ArticleBase
from utility.db_connector import save_articles_to_db, create_or_update_search_term
from utility.exporter import export_articles

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache http requests locally to improve performance and prevent overloading webserver
req_session = requests_cache.CachedSession('cache', expire_after=timedelta(hours=168))
req_session.headers.update({'User-Agent': 'Research Project'})

# Load database configuration
config = yaml.safe_load(open('config.yml'))

DATABASE_URL = (f"postgresql://{config['Webscraper']['Database']['POSTGRES_USER']}:"
                f"\"{config['Webscraper']['Database']['POSTGRES_PASSWORD']}\"@localhost:5432/"
                f"{config['Webscraper']['Database']['POSTGRES_DB']}?client_encoding=utf8")

# Set up database connection
engine = create_engine(DATABASE_URL)
db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


# Create tables in database
def init_db():
    ArticleBase.metadata.create_all(bind=engine)


# Filter articles to only include those from January 1, 2014, onward
def filter_last_10years(all_articles):
    cutoff_date = datetime(2014, 1, 1)

    filtered_articles = [article for article in all_articles if article.date and article.date >= cutoff_date]
    return filtered_articles


# Collect articles for a list of search terms
def collect_articles_for_searchterms(search_terms, filter_10y):
    articles_dict = {}
    for term in search_terms:
        results = collect_articles_for_searchterm(term, filter_10y)

        # Add articles to dictionary, using URL as key to prevent duplicates
        for article in results:
            if article.url in articles_dict:
                articles_dict[article.url].add_search_term(term)
            else:
                articles_dict[article.url] = article

    logger.info(f"Collected :{len(articles_dict.values())} articles")
    return list(articles_dict.values())


# Collect articles for a single search term
def collect_articles_for_searchterm(search_term, filter_10y):
    collected_articles = []

    # Fetch articles for each news outlet
    for news_outlet in NewsOutlet:
        logger.info(f"{news_outlet.abbr}: Fetching results for \"{search_term.label}\"")
        a = news_outlet.fetch_search_results(search_term, req_session)
        collected_articles.extend(a)

    if filter_10y:
        collected_articles = filter_last_10years(collected_articles)

    return collected_articles


if __name__ == '__main__':

    # Initialize database
    init_db()

    search_terms_data = [
        {"label": "Hackback", "spellings": ["Hackback", "Hackbacks"]},
        {"label": "Gefahrenabwehr Cyberraum", "spellings": ["Gefahrenabwehr Cyberraum"]},
        {"label": "Aktive Cyberabwehr", "spellings": ["aktive Cyberabwehr"]}
    ]

    session = db_session()

    search_terms = []

    # Create or update search terms in database
    for term_data in search_terms_data:
        search_term = create_or_update_search_term(session, term_data)
        search_terms.append(search_term)

    all_articles = []

    # Collect articles for each search term
    articles_for_terms = collect_articles_for_searchterms(search_terms, True)
    all_articles.extend(articles_for_terms)

    # Export and save articles
    export_articles(all_articles, config)

    # Save articles to database
    save_articles_to_db(session, all_articles)

    session.close()
