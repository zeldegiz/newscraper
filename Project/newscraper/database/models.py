from sqlalchemy import Column, String, Integer, DateTime, LargeBinary, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

base = declarative_base()

class Tag(base):
    __tablename__ = 'tags'
    id = Column('id', Integer, primary_key=True)
    tag = Column('tag', String, unique=True, nullable=False)
    news = relationship('News', back_populates = "tags", secondary='news_tags')
    
    def __repr__(self):
        return self.tag
        
class News(base):
    __tablename__ = 'news'
    id = Column('id', Integer, primary_key=True)
    url = Column('url', String, unique=True, nullable=False)
    header = Column('header', String, nullable=False)
    datetime = Column('datetime', DateTime, nullable=False)
    image = Column('image', String)
    news_content = Column('news_content', String, nullable=False)
    category = Column('category', String, nullable=False)
    author = Column('author', String)
    tags = relationship("Tag", back_populates = "news", secondary='news_tags')
    
    def __repr__(self):
        return self.header

class News_Tags(base):
    __tablename__ = 'news_tags'
    id = Column('id', Integer, primary_key=True)
    news_id = Column('news_id', Integer, ForeignKey('news.id'))
    tag_id = Column('tag_id', Integer, ForeignKey('tags.id'))