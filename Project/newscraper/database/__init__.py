from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from .models import *

class database:
    def __init__(self, url, username, password, port = '5432'):
        db_str = f'postgresql://{username}:{password}@{url}:{port}'
        self.engine = create_engine(db_str)
        Session = sessionmaker(self.engine)
        self.session = Session()
        
    def create_tables(self):
        table_names = [name for name in inspect(self.engine).get_table_names(schema = 'public')]
        if(all(map(lambda name: name in table_names, ['tags', 'news', 'news_tags']))):
            return
        models.base.metadata.create_all(self.engine)
        
    def insert(self, **kwargs):
        tags = kwargs['tags']
        exist_tags = self.session.query(Tag).filter(Tag.tag.in_(tags)).all()
        for tag in exist_tags:
            tags.remove(tag.tag)
        not_existed_tags = [Tag(tag = tag) for tag in tags]
        del kwargs['tags']
        news = News(**kwargs)
        for tag in exist_tags:
            news.tags.append(tag)
        for tag in not_existed_tags:
            news.tags.append(tag)
        self.session.add(news)
        self.session.commit()