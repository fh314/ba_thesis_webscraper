from enum import Enum

from news.searcher import (
    GolemSearcher, HeiseSearcher,
    NporgSearcher, RNDSearcher,
    SpiegelSearcher, SZSearcher,
    TazSearcher, WeltSearcher,
    FAZSearcher, ZeitSearcher,
    TagesspiegelSearcher
)


class NewsOutlet(Enum):
    SZ = ("Süddeutsche Zeitung", "SZ", SZSearcher())
    WELT = ("Die Welt",  "Welt", WeltSearcher())
    RND = ("Redaktionsnetzwerk Deutschland",  "RND", RNDSearcher())
    HEISE = ("Heise",  "Heise", HeiseSearcher())
    NP_ORG = ("netzpolitik.org",  "np_org", NporgSearcher())
    SPIEGEL = ("Der Spiegel",  "Spiegel", SpiegelSearcher())
    TAZ = ("Die Tageszeitung (taz)",  "taz", TazSearcher())
    GOLEM = ("golem.de",  "golem", GolemSearcher())
    FAZ = ("Frakfurter Allgemeine Zeitung",  "FAZ", FAZSearcher())
    ZEIT = ("Zeit Online",  "Zeit", ZeitSearcher())
    TAGESSPIEGEL = ("Tagesspiegel Background",  "Tagesspiegel", TagesspiegelSearcher())

    def __init__(self, name, abbr, article_searcher):
        self._outlet_name = name
        self._abbr = abbr
        self._article_searcher = article_searcher

    @property
    def name(self):
        return self._outlet_name

    @property
    def abbr(self):
        return self._abbr

    @classmethod
    def from_name(cls, name):
        for member in cls:
            if member.name == name:
                return member
        raise ValueError(f"'{name}' is not a valid NewsOutlet name")

    def __str__(self):
        return self.name

    def fetch_search_results(self, search_term, session):
        results = []
        for spelling in search_term.spellings:
            results.extend(self._article_searcher.fetch_articles_for_searchterm(search_term, spelling, session, self))
        return results
