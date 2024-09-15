from abc import ABC, abstractmethod


class ArticleSearcher(ABC):

    @staticmethod
    def get_page(base_url, params, cookies, session, logger):

        response = session.get(base_url, params=params, cookies=cookies, allow_redirects=False)

        # check status code, warn if request was unsuccessful
        if response.status_code != 200:
            logger.warning(f"Failed to fetch data, status code: {response.status_code} for url: {response.url}")
            return None

        return response

    @abstractmethod
    def fetch_articles_for_searchterm(self, search_term, search_term_str, session, outlet):
        pass