from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary)

from scrapy.utils.project import get_project_settings
import datetime


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Policy(DeclarativeBase):
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
    username = Column(String(20), default=get_project_settings().get("DB_USER"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    processing_id = Column(Integer, ForeignKey('processing.id'))

    def save_to_db(self, session):
        try:
            session.add(self)
            session.commit()


        except Exception as e:
            session.rollback()
            return print(getattr(e, 'message', str(e)))
        finally:
            return self


class URLsToScrape(DeclarativeBase):
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
    username = Column(String(20), default=get_project_settings().get("DB_USER"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Processing(DeclarativeBase):
    __tablename__ = 'processing'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    s3_raw = Column(String(200))
    s3_txt = Column(String(200))
    s3_pos = Column(String(200))
    s3_ner = Column(String(200))
    policy_id = relationship('Policy', backref='processing')

    def save_to_db(self, session):
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            return print(getattr(e, 'message', str(e)))
        finally:
            return self
