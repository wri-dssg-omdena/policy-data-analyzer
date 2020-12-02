import scrapy
import json
import datetime
import math
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider


class ElPeruano(BaseSpider):
    name = "ElPeruano"
    country = "Peru"
    geo_code = "PER-000-00000-0000000"
    level = "0"
    source = "busquedas.elperuano.pe"
    collector = "Ignacio Fernandez"
    scrapper_name = "Ignacio Fernandez"
    scrapable = "True"
    with open('./keywords_knowledge_domain.json', 'r') as dict:
        keyword_dict = json.load(dict)
    with open('./negative_keywords_knowledge_domain.json', 'r') as dict:
        negative_keyword_dict = json.load(dict)


    def __init__(self, date="2020-09-01"):
        try:
            self.from_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except:
            self.from_date = datetime.datetime.strptime(date, '%d-%m-%Y').date()
        self.from_date = self.from_date.strftime('%d-%m-%Y')
        date_today = datetime.date.today()
        self.today = date_today.strftime('%d-%m-%Y')
        self.start_urls = [
            f'https://busquedas.elperuano.pe/api/v1/elvis?from_date={self.from_date}&page=0&scope=false&to_date={self.today}']

    def parse(self, response):
        hits = json.loads(response.text)['totalHits']
        hits = math.ceil(hits / 10)
        URLs = [
            f'https://busquedas.elperuano.pe/api/v1/elvis?from_date={self.from_date}&page={i}&scope=false&to_date={self.today}'
            for i in range(1, hits)]
        ref_lst = []
        self.ref_lst = ref_lst
        for url in URLs:
            yield scrapy.Request(url, dont_filter=True, callback=self.parse_other)

    def parse_other(self, response):
        item = ScrapyOfficialNewspapersItem()
        for norm in json.loads(response.text)['hits']:
            if 'subjectOrganizationCode' in norm['metadata']:
                ref = norm['metadata']['subjectOrganizationCode']
            else:
                ref = ""
            try:
                item['reference'] = ref
                item['doc_url'] = 'https://busquedas.elperuano.pe/download/url/' + str(norm['metadata']['slug'])
                text_to_search = self.clean_text(norm['metadata']['description']) + " " + self.clean_text(
                    norm['metadata']['slug']) + " " + self.clean_text(norm['highlightedText'])
                if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
                    item['country'] = self.country
                    item['geo_code'] = self.geo_code
                    item['level'] = self.level
                    item['data_source'] = self.source
                    item['authorship'] = norm['metadata']['editionName']
                    item['resume'] = self.clean_text(norm['metadata']['description'])
                    item['title'] = self.clean_text(norm['metadata']['description'])
                    item['publication_date'] = norm['metadata']['publicationDate']['formatted']
                    item['enforcement_date'] = item['publication_date']
                    item['url'] = 'https://busquedas.elperuano.pe' + str(norm['url_link'])
                    item['doc_name'] = ('PER/policy_' + norm['metadata']['name'])
                    item['doc_type'] = 'pdf'
                    item['doc_class'] = norm['metadata']['industry']
                    item['file_urls'] = [item['doc_url']]
                    yield item
            except Exception as e:
                print(e)
                pass

