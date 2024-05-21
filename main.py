import csv
import re
from datetime import timedelta, datetime

import requests_cache
import yaml


from news.newsoutlet import NewsOutlet
from utility.plotter import plot_data, prepare_data, plot_articles

# Cache http requests locally to improve performance and prevent getting IP-address blacklisted
session = requests_cache.CachedSession('cache', expire_after=timedelta(hours=168))
session.headers.update({'User-Agent': 'Temporary test-system for evaluation of research setup'})

config = yaml.safe_load(open('config.yml'))


def filter_last_10years(all_articles):
    cutoff_date = datetime(2014, 1, 1)

    # Filter articles to only include those from January 1, 2014, onward
    filtered_articles = [article for article in all_articles if article.date and article.date >= cutoff_date]
    return filtered_articles


def export_articles(all_articles):
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = config["Webscraper"]["EXPORT_PATH"]
    filename = f"export_{timestamp}.csv"  # Append timestamp to the filename

    # Construct full path
    full_export_path = f"{export_path}/{filename}"

    with open(full_export_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Adding 'Search Terms' to the header
        writer.writerow(['Title', 'URL', 'Description', 'Author', 'Date', 'News Outlet', 'Search Terms'])
        for article in all_articles:
            # Concatenate all search terms into a single string separated by commas
            search_terms_str = ', '.join(article.search_terms)

            # Clean and prepare each field before writing to the CSV
            title = clean_text(article.title)
            url = article.url  # URLs typically do not contain special whitespace or non-printable characters
            description = clean_text(article.description)
            author = clean_text(article.author)
            date = article.date  # Date fields typically do not contain non-printable characters
            news_outlet = article.news_outlet.abbr if article.news_outlet else None

            # Include the concatenated search terms in the row
            writer.writerow([title, url, description, author, date, news_outlet, search_terms_str])


def clean_text(text):
    """Removes special and non-printable characters, and replaces them with normal spaces."""
    if text is not None:
        text = re.sub(r'\s', ' ', text)  # Replace all whitespace with a normal space
        text = re.sub(r'[^\x20-\x7EäöüÄÖÜß]', '', text)  # Preserve German characters
    return text


def collect_articles_for_searchterms(search_terms, filter_10y):
    articles_dict = {}
    for term in search_terms:
        results = collect_articles_for_searchterm(term, filter_10y)
        for article in results:
            if article.url in articles_dict:
                articles_dict[article.url].add_search_term(term)
            else:
                articles_dict[article.url] = article

    return list(articles_dict.values())


def collect_articles_for_searchterm(search_term, filter_10y):
    collected_articles = []
    for news_outlet in NewsOutlet:
        print(f"{news_outlet.abbr}: Fetching results for \"{search_term}\"")
        a = news_outlet.fetch_search_results(search_term, session)
        print(len(a))
        collected_articles.extend(a)

    if filter_10y:
        collected_articles = filter_last_10years(collected_articles)

    return collected_articles


if __name__ == '__main__':
    search_terms = ["Zitis", "Cyberagentur"]
    all_articles = []

    all_articles.extend(collect_articles_for_searchterms(search_terms, False))

    print("Collected :", len(all_articles), " articles")
    # for article in sorted(all_articles, key=lambda news_article: news_article.date):
    #    print(article.news_outlet.abbr + ":", article.date, article.title)


    plot_articles(all_articles, search_terms)
    export_articles(all_articles)
    #extract_topics_from_subscriptions(all_articles)
