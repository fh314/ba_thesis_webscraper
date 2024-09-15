import logging

from news.newsarticle import NewsArticle, SearchTerm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_articles_to_db(session, articles):
    total_articles = len(articles)
    new_articles_count = 0
    existing_articles_count = 0

    logger.info("Saving articles to database")
    for index, article in enumerate(articles):
        # Check if 10% of the articles have been processed
        if (index + 1) % (total_articles // 10) == 0:
            progress = ((index + 1) / total_articles) * 100
            logger.info(f"{progress:.0f}% of articles processed")
        try:
            # Check if an article with the same URL already exists in the database
            existing_article = session.query(NewsArticle).filter_by(url=article.url).first()
            if existing_article:
                existing_articles_count += 1
                logger.debug(f"Article with URL {article.url} already exists. Deleting.")
                session.delete(existing_article)

            session.commit()

            logger.debug(f"Saving article to DB: [{article.news_outlet_enum().abbr}] {article.title}")

            session.add(article)
            session.commit()
            new_articles_count += 1
        except Exception as e:
            logger.error(f"Error while saving to database: {e}")
            session.rollback()

    logger.info(
        f"All articles have been processed. {new_articles_count} articles were updated or newly added, {existing_articles_count} articles already existed.")
    session.expunge_all()


def create_or_update_search_term(session, term_data):
    existing_search_term = session.query(SearchTerm).filter_by(label=term_data["label"]).first()
    if existing_search_term:
        new_spellings = set(term_data["spellings"]) - set(existing_search_term.spellings)
        if new_spellings:
            existing_search_term.spellings = list(set(existing_search_term.spellings + list(new_spellings)))
        return existing_search_term
    else:
        search_term = SearchTerm(term=term_data["label"], spellings=term_data["spellings"])
        session.add(search_term)
        session.commit()
        return search_term
