# NewsArticle class represents the metadata and possibly content of
# scraped articles
class NewsArticle:
    def __init__(self, title, url, description, author, date, news_outlet, search_term):
        self.title = title
        self.url = url
        self.description = description
        self.author = author
        self.date = date
        self.news_outlet = news_outlet
        self.full_text = None
        self.search_terms = [search_term]

    def add_search_term(self, term):
        if term not in self.search_terms:
            self.search_terms.append(term)
