import csv
import os
import re
from datetime import datetime


# Export articles to a CSV file
def export_articles(all_articles, config):
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Get the export path from the configuration file
    export_path = config["Webscraper"]["EXPORT_PATH"]

    # Append timestamp to the filename
    filename = f"export_{timestamp}.csv"

    # Construct full path
    full_export_path = f"{export_path}/{filename}"

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(full_export_path), exist_ok=True)

    # Write the articles to the CSV file
    with open(full_export_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Adding 'Search Terms' to the header
        writer.writerow(['Title', 'URL', 'Description', 'Author', 'Date', 'News Outlet', 'Search Terms'])
        for article in all_articles:
            # Concatenate all search terms into a single string separated by commas
            search_terms_str = ', '.join(term.label for term in article.search_terms)

            # Clean and prepare each field before writing to the CSV
            title = clean_text(article.title)

            url = article.url

            description = clean_text(article.description)

            author = clean_text(article.author)

            date = article.date.strftime("%Y-%m-%d %H:%M:%S") if article.date else None

            news_outlet = article.news_outlet_enum().abbr if article.news_outlet_enum() else None

            # Include the concatenated search terms in the row
            writer.writerow([title, url, description, author, date, news_outlet, search_terms_str])


# Clean and prepare text for CSV export to remove non-printable characters
def clean_text(text):
    if text is not None:
        text = re.sub(r'\s', ' ', text)  # Replace all whitespace with a normal space
        text = re.sub(r'[^\x20-\x7EäöüÄÖÜß]', '', text)  # Preserve German characters
    return text
