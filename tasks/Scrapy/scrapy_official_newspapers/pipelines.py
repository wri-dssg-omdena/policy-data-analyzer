# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
from datetime import date
import hashlib
import os
from scrapy.utils.python import to_bytes

from scrapy.exporters import CsvItemExporter
from sqlalchemy.orm import sessionmaker
from scrapy_official_newspapers.models import Policy, Processing, db_connect, create_table
from scrapy_official_newspapers.__init__ import hello_world

class ScrapyOfficialNewspapersMySQLPipeline:
    def __init__(self):
        API_key_file = 'C:/Users/jordi/Google Drive/Els_meus_documents/projectes/CompetitiveIntelligence/WRI/Notebooks/credentials/us_gov_api_key.json'
        self.API_key = self.import_json(self.API_key_file)["us gov apikey jp"]
        engine = db_connect()
        create_table(engine)
        self.session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.session()
        processing = Processing(s3_raw=hashlib.sha1(to_bytes(item['doc_url'])).hexdigest())
        session.add(processing)

        policy = Policy(
            country=item['country'],
            state = item['state'],
            data_source=item['data_source'],
            law_class = item['law_class'],
            title=item['title'],
            reference=item['reference'],
            authorship=item['authorship'],
            resume=item['summary'],
            publication_date=item['publication_date'],
            url=item['url'],
            doc_url=item['doc_url'] + self.API_key,
            doc_name=item['doc_name'],
            processing = processing
        )
        session.merge(policy)
        #print(policy)
        session.commit()


from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter


class ScrapyOfficialNewspapersPipeline:
    def __init__(self):
        self.files = ()
        today = datetime.date.today()
        self.today = today.strftime('%Y%m%d')

    def open_spider(self, spider):
        dir = "./output/"
        self.file = open(f"{spider.name}_{self.today}.csv", "wb") #open(dir + "USFR_20210702.csv", 'ab') 
        self.exporter_1 = CsvItemExporter(self.file, include_headers_line = False, encoding = 'Latin1')
        self.exporter_2 = CsvItemExporter(self.file, include_headers_line = False, encoding = 'utf-8')		
        self.exporter_1.start_exporting()
        self.exporter_2.start_exporting()

    def close_spider(self, spider):
        self.exporter_1.finish_exporting()
        self.exporter_2.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        try:
            self.exporter_1.export_item(item)
        except:
            self.exporter_2.export_item(item)
        return item