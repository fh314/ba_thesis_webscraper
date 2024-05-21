from enum import Enum

from news.searcher import (
    GolemSearcher, HeiseSearcher,
    NporgSearcher, RNDSearcher,
    SpiegelSearcher, SZSearcher,
    TazSearcher, WeltSearcher,
    FAZSearcher, ZeitSearcher
)


class NewsOutlet(Enum):
    SZ = ("Süddeutsche Zeitung", "", "SZ", "#66c2a5", SZSearcher())
    WELT = ("Die Welt", "", "Welt", "#004488", WeltSearcher())
    RND = ("Redaktionsnetzwerk Deutschland", "", "RND", "#8a2be2", RNDSearcher())
    HEISE = ("Heise", "", "Heise", "#959595", HeiseSearcher())
    NP_ORG = ("netzpolitik.org", "", "np_org", "#00a1e0", NporgSearcher())
    SPIEGEL = ("Der Spiegel", "", "Spiegel", "#ff7300", SpiegelSearcher())
    TAZ = ("Die Tageszeitung (taz)", "", "taz", "#d50d2e", TazSearcher())
    GOLEM = ("golem.de", "", "golem", "#7fb71e", GolemSearcher())
    FAZ = ("Frakfurter Allgemeine Zeitung", "", "FAZ", "#33363b", FAZSearcher())
    Zeit = ("Zeit Online", "", "Zeit", "#FFC0CB", ZeitSearcher())

    def __init__(self, name, description, abbr, color, article_searcher):
        self._name = name
        self._description = description
        self._abbr = abbr
        self._color = color
        self._article_searcher = article_searcher

    @property
    def name(self):
        return self._name

    @property
    def abbr(self):
        return self._abbr

    @property
    def color(self):
        return self._color

    def fetch_search_results(self, search_term, session):
        return self._article_searcher.fetch_articles(search_term, session, self)
