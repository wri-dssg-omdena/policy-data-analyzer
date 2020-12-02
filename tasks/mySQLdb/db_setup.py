from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import datetime

from db_config import Base, engine, db_user, DBSession
session = DBSession()

class Policy(Base):

    __tablename__ = 'policies'
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True)
    country = Column(String(60), nullable=False)
    geo_code = Column(String(20))
    level = Column(Integer())
    urls_to_scrape_id = Column(Integer, ForeignKey('urlstoscrape.id'))
    data_source = Column(String(100))
    title = Column(String(100))
    reference = Column(String(100))
    authorship = Column(String(50))
    resume = Column(Text)
    publication_date = Column(Date)
    enforcement_date = Column(Date)
    affected_locations = Column(String(200))
    url = Column(String(2048))
    doc_url = Column(String(2048))
    doc_name = Column(String(50))
    doc_type = Column(String(4))
    doc_class = Column(String(30))
    doc_tags = Column(String(500))
    related_docs = Column(String(500))
    comment = Column(Text)
    processing_id = Column(Integer, ForeignKey('processing.id'))
    username = Column(String(20), default=db_user, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def save_to_db(self):
        session.add(self)
        try:
            session.commit()
            return print(str(self.source)+ ' ' +  str(self.title) + ' has successfully been added to the database')
        except Exception as e:
            session.rollback()
            return print(getattr(e, 'message', str(e)))


class URLsToScrape(Base):

    __tablename__ = 'urlstoscrape'
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True)
    country = Column(String(60), nullable=False)
    geo_code = Column(String(20))
    spatial_id = Column(String(50))
    source_name = Column(String(50))
    scrapable = Column(Boolean())
    scrape_method = Column(String(15))
    scraper_name = Column(String(30))
    scraper_creator = Column(String(30)) 
    collector = Column(String(30))
    url = Column(String(2048), nullable=False)
    comment = Column(Text)
    username = Column(String(20), default=db_user, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Processing(Base):

    __tablename__ = 'processing'
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'))
    s3_raw = Column(String(200))
    s3_txt = Column(String(200))
    s3_pos = Column(String(200))
    s3_ner = Column(String(200))

session.close()        
    
#engine = create_engine(connection_string) #, echo=True)
Base.metadata.create_all(engine)