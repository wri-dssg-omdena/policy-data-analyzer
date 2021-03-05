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
    state_name = "Federal"
    state_code = "" # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "Diario Oficial de la Federacion"
    spider_builder = "Jordi Planas"
    scrapable = "True"
    allowed_domains = ["sidofqa.segob.gob.mx"]
    start_date = "2021-01-01"
    #This is a category that appears in the database which yields a lot of documents that announce job posts. We exclude them from the search
    authorship_to_exclude = 'CONVOCATORIAS PARA CONCURSOS DE PLAZAS VACANTES DEL SERVICIO PROFESIONAL DE CARRERA EN LA ADMINISTRACION PUBLICA FEDERAL'

    def __init__(self):
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_ES.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain_ES.json')
        self.from_date, self.today = self.create_date_span(self.start_date)
    
    def start_requests(self):
        for day in self.create_date_list(self.from_date, self.today, 1, "days", self.country_code):
            #self.debug(day)
            self.day_doc_url = day.strftime('%d/%m/%Y')
            day = day.strftime('%d-%m-%Y')
            #self.debug(day)
            self.start_url = f'https://sidofqa.segob.gob.mx/dof/sidof/notas/{day}'
            #print(start_urls)
            yield scrapy.Request(self.start_url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        notas = []
        notas.append(json.loads(response.text)["NotasMatutinas"])
        notas.append(json.loads(response.text)["NotasVespertinas"])
        notas.append(json.loads(response.text)["NotasExtraordinarias"])

        for nota in json.loads(response.text)["NotasMatutinas"]:
            if 'titulo' in nota:
                text_to_search = nota["titulo"]
                if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict) and nota['nombreCodOrgaUno'] != self.authorship_to_exclude:
                    self.debug("True")
                    item = ScrapyOfficialNewspapersItem()
                    item['country'] = self.country
                    item['state'] = self.state_name
                    item['data_source'] = self.source
                    if 'tipoNota' in nota:
                        item['law_class'] = nota['tipoNota']
                    else:
                        item['law_class'] = ''
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
                    # if nota['existeDoc'] == 'S':
                    #     item['doc_url'] = f'https://sidofqa.segob.gob.mx/dof/sidof/documentos/doc/{codigo_nota}'
                    #     item['doc_name'] = self.HSA1_encoding(f'https://sidofqa.segob.gob.mx/dof/sidof/documentos/doc/{codigo_nota}')
                    # else:
                    item['pdf_url'] = f'https://www.dof.gob.mx/nota_detalle.php?codigo={codigo_nota}&fecha={self.day_doc_url}&print=true'
                    item['doc_name'] = self.HSA1_encoding(f'https://www.dof.gob.mx/nota_detalle.php?codigo={codigo_nota}&fecha={self.day_doc_url}&print=true')
                    yield item
            else:
                pass
