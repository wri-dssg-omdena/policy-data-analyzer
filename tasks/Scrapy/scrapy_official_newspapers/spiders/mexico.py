import scrapy
from scrapy_official_newspapers.spiders import BaseSpider
from scrapy.selector import Selector
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from bs4 import BeautifulSoup
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
    start_date = "2011-01-01"
    #This is a category that appears in the database which yields a lot of documents that announce job posts. We exclude them from the search
    authorship_to_exclude = 'CONVOCATORIAS PARA CONCURSOS DE PLAZAS VACANTES DEL SERVICIO PROFESIONAL DE CARRERA EN LA ADMINISTRACION PUBLICA FEDERAL'
    folder_to_save = "spanish_documents/text_files/new/"
    # folder_to_save = "wri.-testing/dof/"

    def __init__(self):
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_ES.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain_ES.json')
        self.from_date, self.today = self.create_date_span(self.start_date)

        # folder = 'C:/Users/jordi/Documents/claus/' # TODO: change to your local path
        # file_name = 'AWS_S3_keys_JordiPlanas_Made_in_game.json' # TODO: Change to your filename
        folder = '/home/propietari/Documents/claus/' # TODO: change to your local path
        file_name = "AWS_S3_keys_wri.json"

        # self.bucket = "wri-testing" # TODO: Change to the final bucket
        # bucket_region = "eu-central-1" # TODO: Change to fit to the final bucket
        self.bucket = "wri-nlp-policy"
        bucket_region = "us-east-1"

        keys_file = folder + file_name
        self.s3 = self.open_S3_session(keys_file, self.bucket, bucket_region)
    
    def start_requests(self):
        for day in self.create_date_list(self.from_date, self.today, 1, "days", self.country_code):
            #self.debug(day)
            day_doc_url = day.strftime('%d/%m/%Y')
            day = day.strftime('%d-%m-%Y')
            #self.debug(day)
            start_url = f'https://sidofqa.segob.gob.mx/dof/sidof/notas/{day}'
            #print(f"\n *************** \n {self.start_url}\n ********************")
            yield scrapy.Request(start_url, dont_filter=True, callback=self.parse, cb_kwargs=dict(day_doc_url = day_doc_url))

    def parse(self, response, day_doc_url):
        # notas = []
        # notas.append(json.loads(response.text)["NotasMatutinas"])
        # notas.append(json.loads(response.text)["NotasVespertinas"])
        # notas.append(json.loads(response.text)["NotasExtraordinarias"])

        for nota in json.loads(response.text)["NotasMatutinas"]:
            if 'titulo' in nota:
                text_to_search = nota["titulo"]
                if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict) and nota['nombreCodOrgaUno'] != self.authorship_to_exclude:
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
                    doc_url = f'https://www.dof.gob.mx/nota_detalle.php?codigo={codigo_nota}&fecha={day_doc_url}&print=true'
                    item['file_urls'] = [doc_url]
                    doc_name = self.HSA1_encoding(doc_url) + ".txt"
                    item['doc_name'] = doc_name
                    #self.debug(f"\n       #################       \n {doc_url} \n   ###############")
                    #self.debug(doc_name)
                    yield item
                    yield scrapy.Request(doc_url, dont_filter=True, callback=self.parse_other, cb_kwargs=dict(document = doc_name, url = doc_url))
            else:
                pass

    def parse_other(self, response, document, url):
        soup = BeautifulSoup(response.css('div#DivDetalleNota').get(), features = "lxml")
        paragraphs = soup.find_all("p")
        text = ""
        if len(paragraphs) == 0:
            text = text + soup.text
        else:
            tables = soup.find_all("td")
            for line in paragraphs[1:]:
                text = text + line.text + "\n"
            text = text + "<table>" + "\n"
            for cell in tables:
                if "En el documento que usted está visualizando" not in cell.text:
                    text = text + cell.text + "\n"
            text = text + "<\\table>" + "\n"
        file = self.folder_to_save + document
        #self.debug(url)
        #self.debug(text)
        #self.debug("\n       ****************       \n")
        #self.debug(file)
        # self.save_to_s3(self.s3, self.bucket, file, text.replace("\t", ""))
