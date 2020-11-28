from scrapy_official_newspapers.spiders import BaseSpider
from scrapy import Request
from scrapy.selector import Selector
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
import time
import json
import re
import datetime
from dateutil.rrule import rrule, DAILY


class MexicoDOF(BaseSpider):
    name = "MexicoDOF"
    country = "Mexico"
    geo_code = "MEX-000-00000-0000000"
    level = "0"
    source = "Diario Oficial de la Federacion"
    title = "None"
    url = "https://dof.gob.mx"
    years = [year for year in range(2018, 2020)]
    collector = "Francisco Canales"
    scrapper_name = "Francisco Canales"
    scrapable = "True"
    allowed_domains = ["dof.gob.mx"]
    doc_name = None
    doc_type = 'HTML'
    with open('./keywords_knowledge_domain.json', 'r') as dict:
        keyword_dict = json.load(dict)
    with open('./negative_keywords_knowledge_domain.json', 'r') as dict:
        negative_keyword_dict = json.load(dict)

    def __init__(self, date = datetime.datetime(2015,1,1)):
        if type(date) == str:
            try:
                self.from_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            except:
                self.from_date = datetime.datetime.strptime(date, '%d-%m-%Y').date()
        else:
            self.from_date = date.date()
        self.today = datetime.date.today()

    def create_url_DOF_list(self):
        URLs = []
        for dt in rrule(DAILY, dtstart=self.from_date, until=self.today):
            url = self.url + f"/index_113.php?year=" + self.add_leading_zero_two_digits(
                        dt.year) + "&month=" + self.add_leading_zero_two_digits(
                        dt.month) + "&day=" + self.add_leading_zero_two_digits(dt.day)

            URLs.append(url)
        return URLs

    def start_requests(self):
        for url in self.create_url_DOF_list():
            yield Request(url, dont_filter=True)

    def parse(self, response):
        if len(response.xpath("//*[contains(text(), 'No hay datos para la fecha')]")):
            print("No publication in this date")
            pass
        else:
            url = response.url
            year = int(url.split("=")[1][:4])
            month = int(url.split("=")[2][:2])
            day = int(url.split("=")[3][:2])
            date = datetime.datetime(year=year,month=month,day=day)
            item = ScrapyOfficialNewspapersItem()
            trs = response.xpath('/html//td[@class = "subtitle_azul"]')[0].xpath('//tr').xpath('following-sibling::tr[1]')

            authorship = None
            for tr in trs:
                authorship_new = tr.xpath('td[@class = "subtitle_azul"]/text()').get()
                resume_aux = tr.xpath('td/a[@class = "enlaces"]/text()').get()
                url_aux = tr.xpath('td/a[@class = "enlaces"]/@href').get()

                if authorship != authorship_new and authorship_new != None:
                    authorship = authorship_new
                if resume_aux and resume_aux != "Ver más":
                    resume = resume_aux.replace('\t', '').replace('\n', '')
                    if self.search_keywords(resume, self.keyword_dict, self.negative_keyword_dict):
                        doc_url = self.url + url_aux + "&print=true"
                        reference = doc_url.split("codigo=")[1][:7]
                        item['country'] = self.country
                        item['geo_code'] = self.geo_code
                        item['level'] = self.level
                        item['data_source'] = self.source
                        item['title'] = resume
                        item['reference'] = reference
                        item['authorship'] = str(authorship)
                        item['resume'] = resume
                        item['publication_date'] = date
                        item['enforcement_date'] = date
                        item['url'] = self.url
                        item['doc_url'] = doc_url
                        item['doc_name'] = reference+'html'
                        item['doc_type'] = self.doc_type
                        item['doc_class'] = ''
                        item['file_urls'] = [doc_url]
                        yield item


