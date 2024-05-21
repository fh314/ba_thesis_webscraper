from abc import ABC, abstractmethod


class ArticleSearcher(ABC):
    @abstractmethod
    def fetch_articles(self, search_term, session, outlet):
        pass
