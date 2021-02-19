from scrapy_official_newspapers.spiders import BaseSpider
import scrapy
from scrapy.selector import Selector
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
import datetime
import json
import re
import time


class MexicoDOF(BaseSpider):
    name = "Mexico"
    country = "Mexico"
    country_code = "MX" # You can find the ISO3166 country code here: https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
    state = "Federal"
    state_code = "" # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "Diario Oficial de la Federacion"
    spider_builder = "Jordi Planas"
    scrapable = "True"
    allowed_domains = ["sidofqa.segob.gob.mx"]
    start_date = "2021-02-17"

    def __init__(self):
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain.json')
        self.from_date, self.today = self.create_date_span(self.start_date)
    
    def start_requests(self):
        for day in self.create_date_list(self.from_date, self.today, 1, "days", self.country_code):
            self.debug(day)
            self.day_doc_url = day.strftime('%d/%m/%Y')
            day = day.strftime('%d-%m-%Y')
            self.debug(day)
            self.start_url = f'https://sidofqa.segob.gob.mx/dof/sidof/notas/{day}'
            #print(start_urls)
            yield scrapy.Request(self.start_url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        for nota in json.loads(response.text)["NotasMatutinas"]:
            self.debug(nota)

        text_to_search = nota["titulo"]
        if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
            item['country'] = self.country
            item['state'] = self.state
            item['data_source'] = self.source
            item['law_class'] = nota['tipoNota']
            item['title'] = nota["titulo"]
            codigo_nota = nota['codNota']
            item['reference'] = codigo_nota
            if 'codOrgaDos' in nota:
                item['authorship'] = nota['nombreCodOrgaUno'] + "/" + nota['codOrgaDos']
            else:
                item['authorship'] = nota['nombreCodOrgaUno']
            item['summary'] = ""
            item['publication_date'] = nota['fecha']
            item['url'] = self.start_url
            if nota['existeDoc'] == 'S':
                item['doc_url'] = f'https://sidofqa.segob.gob.mx/dof/sidof/documentos/doc/{codigo_nota}'
                item['doc_name'] = self.HSA1_encoding(f'https://sidofqa.segob.gob.mx/dof/sidof/documentos/doc/{codigo_nota}')
            else:
                item['doc_url'] = f'https://www.dof.gob.mx/nota_detalle.php?codigo={codigo_nota}&fecha={self.day_doc_url}&print=true'



            #yield item

            #url = granule["granuleLink"] + f'?api_key={self.API_key}'
            #yield scrapy.Request(url, dont_filter=True, callback=self.parse_other)

    #def __init__(self, date = datetime.datetime(2020,9,1)):
    #    self.keyword_dict, self.negative_keyword_dict = self.import_filtering_keywords()
    #    if type(date) == str:
    #        try:
    #            self.from_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    #        except:
    #            self.from_date = datetime.datetime.strptime(date, '%d-%m-%Y').date()
    #    else:
    #        self.from_date = date.date()
    #    self.today = datetime.date.today()

    #def create_url_DOF_list(self):
    #    URLs = []
    #    for dt in rrule(DAILY, dtstart=self.from_date, until=self.today):
    #        url = self.url + f"/index_113.php?year=" + self.add_leading_zero_two_digits(
    #                    dt.year) + "&month=" + self.add_leading_zero_two_digits(
    #                    dt.month) + "&day=" + self.add_leading_zero_two_digits(dt.day)

    #        URLs.append(url)
    #    return URLs

    #def start_requests(self):
    #    for url in self.create_url_DOF_list():
    #        yield Request(url, dont_filter=True)

    #def parse(self, response):
    #    if len(response.xpath("//*[contains(text(), 'No hay datos para la fecha')]")):
    #        print("No publication in this date")
    #        pass
    #    else:
    #        url = response.url
    #        year = int(url.split("=")[1][:4])
    #        month = int(url.split("=")[2][:2])
    #        day = int(url.split("=")[3][:2])
    #        date = datetime.datetime(year=year,month=month,day=day)
    #        item = ScrapyOfficialNewspapersItem()
    #        trs = response.xpath('/html//td[@class = "subtitle_azul"]')[0].xpath('//tr').xpath('following-sibling::tr[1]')

    #        authorship = None
    #        for tr in trs:
    #            authorship_new = tr.xpath('td[@class = "subtitle_azul"]/text()').get()
    #            summary_aux = tr.xpath('td/a[@class = "enlaces"]/text()').get()
    #            url_aux = tr.xpath('td/a[@class = "enlaces"]/@href').get()

    #            if authorship != authorship_new and authorship_new != None:
    #                authorship = authorship_new
    #            if summary_aux and summary_aux != "Ver más":
    #                text_to_search = summary_aux.replace('\t', '').replace('\n', '')
    #                if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
    #                    doc_url = self.url + url_aux + "&print=true"
    #                    reference = doc_url.split("codigo=")[1][:7]
    #                    item['country'] = self.country
    #                    item['state'] = self.state
    #                    item['data_source'] = self.source
    #                    item["law_class"] = ""
    #                    item['title'] = text_to_search
    #                    item['reference'] = reference
    #                    item['authorship'] = str(authorship)
    #                    item['summary'] = resume
    #                    item['publication_date'] = date
    #                    item['url'] = self.url
    #                    item['doc_url'] = doc_url
    #                    item['doc_name'] = self.HSA1_encoding(doc_url)


