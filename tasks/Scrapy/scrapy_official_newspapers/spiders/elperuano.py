import scrapy
import datetime
import math
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider


class ElPeruano(BaseSpider):
    name = "ElPeruano"
    country = "El Peruano, Diario oficial del Perú"
    country_code = "PE" # You can find the ISO3166 country code here: https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
    state = "Federal"
    state_code = "" # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "El peruano"
    spider_builder = "Ignacio Fernandez"
    scrapable = "True"
    allowed_domains = ["elperuano.pe"]
    start_date = "2020-09-01"


    def __init__(self, start_date):
        self.keyword_dict, self.negative_keyword_dict = self.import_filtering_keywords()
        self.from_date, self.today = self.create_date_span(start_date)
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
                    item['state'] = self.state
                    item["law_class"] = "" #TODO: look at the right field when adjusted.
                    item['data_source'] = self.source
                    item['authorship'] = norm['metadata']['editionName']
                    item['summary'] = self.clean_text(norm['metadata']['description'])
                    item['title'] = self.clean_text(norm['metadata']['description'])
                    item['publication_date'] = norm['metadata']['publicationDate']['formatted']
                    item['enforcement_date'] = item['publication_date']
                    item['url'] = 'https://busquedas.elperuano.pe' + str(norm['url_link'])
                    item['doc_name'] = self.HSA1_encoding(doc_url)
                    yield item
            except Exception as e:
                print(e)
                pass

