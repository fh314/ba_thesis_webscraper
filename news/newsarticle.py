from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from news.newsoutlet import NewsOutlet

Base = declarative_base()

# Association table for many-to-many relationship between NewsArticle and SearchTerm
article_searchterm_association = Table(
    'article_searchterm', Base.metadata,
    Column('article_id', ForeignKey('news_articles.id'), primary_key=True),
    Column('searchterm_id', ForeignKey('search_terms.id'), primary_key=True)
)

# Datatype for news articles
class NewsArticle(Base):
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    url = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    news_outlet = Column(String, nullable=False)
    search_terms = relationship('SearchTerm', secondary=article_searchterm_association)

    # Currently not used
    paragraphs = relationship('Paragraph', back_populates='article', cascade='all, delete-orphan')
    links = relationship('Link', back_populates='article', cascade='all, delete-orphan')

    def __init__(self, title, url, description, author, date, news_outlet, search_term):
        self.title = title
        self.url = url
        self.description = description
        self.author = author
        self.date = date
        self.news_outlet = news_outlet.name
        self.search_terms = [search_term]
        self.paragraphs = []
        self.links = []

    def news_outlet_enum(self):
        return NewsOutlet.from_name(self.news_outlet)

    def add_search_term(self, search_term):
        if search_term not in self.search_terms:
            self.search_terms.append(search_term)


    # Currently not used
    def add_paragraphs(self, paragraphs):
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.isspace() and paragraph:
                self.paragraphs.append(Paragraph(content=paragraph, position=i))

    # Currently not used
    def add_links(self, links):
        for display, url in links.items():
            self.links.append(Link(display=display, url=url))

# Currently not used
class Paragraph(Base):

    # Database table for paragraphs
    # Define the table name
    __tablename__ = 'paragraphs'

    # Define the table columns
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    article_id = Column(Integer, ForeignKey('news_articles.id'))
    article = relationship('NewsArticle', back_populates='paragraphs')

    def __init__(self, content, position):
        self.content = content
        self.position = position

# Currently not used
class Link(Base):

    # Database table for links
    # Define the table name
    __tablename__ = 'links'

    # Define the table columns
    id = Column(Integer, primary_key=True)
    display = Column(String, nullable=False)
    url = Column(String, nullable=False)
    article_id = Column(Integer, ForeignKey('news_articles.id'))
    article = relationship('NewsArticle', back_populates='links')

    def __init__(self, display, url):
        self.display = display
        self.url = url


# Datatype for search terms
class SearchTerm(Base):
    __tablename__ = 'search_terms'

    id = Column(Integer, primary_key=True)
    label = Column(String, unique=True, nullable=False)
    spellings = Column(JSON, nullable=False)  # Store spellings as a JSON array

    def __init__(self, term, spellings):
        self.label = term
        self.spellings = spellings
