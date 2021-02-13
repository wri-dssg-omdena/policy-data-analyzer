import scrapy
import json
import datetime
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider


class USFR(BaseSpider):
    name = "USFR"
    country = "USA"
    level = "0"
    source = "Federal Register"
    collector = "Jordi Planas"
    scrapper_name = "Jordi Planas"
    scrapable = "True"
    allowed_domains = ["api.govinfo.gov"]

    def __init__(self, date = "2021-02-11"):
        self.keyword_dict, self.negative_keyword_dict = self.import_filtering_keywords()
        self.from_date, self.today = self.create_date_span(date)
    
    def start_requests(self):
        for day in self.create_date_list(self.from_date, self.today, 1, "days"):
            #print(day)
            start_urls = f'https://api.govinfo.gov/packages/FR-{day}/granules?offset=0&pageSize=300&api_key=pA4uH8buEXSjCdh0LfCj0R2kilPWZPakPzn5JANL'
            #print(start_urls)
            yield scrapy.Request(start_urls, dont_filter=True, callback=self.parse)

    def parse(self, response):
        for granule in json.loads(response.text)["granules"]:
            yield scrapy.Request(granule["granuleLink"]+'?api_key=pA4uH8buEXSjCdh0LfCj0R2kilPWZPakPzn5JANL', dont_filter=True, callback=self.parse_other)

    def parse_other(self, response):
        summary = response.json()
        print(summary, "\n\n")
        #item = ScrapyOfficialNewspapersItem()
    #    for norm in json.loads(response.text)[0]:
    #        text_to_search = self.clean_text(norm['TITULO_NORMA']) + self.clean_text( norm['DESCRIPCION'])
    #        if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
    #            norm_id = norm['IDNORMA']
    #            norm_url = f'https://www.bcn.cl/leychile/navegar?idNorma={norm_id}'
    #            doc_name = f'CHL/policy_{norm_id}'
    #            doc_type = 'txt'
    #            publication_date = norm['FECHA_PUBLICACION']
    #            pub_date_format = parse(publication_date, ['es']).strftime('%Y-%m-%d')
    #            doc_path = str(norm_id) + '.' + str(pub_date_format) + '.0.0%23'
    #            doc_url = f'https://nuevo.leychile.cl/servicios/Consulta/Exportar?radioExportar=Normas&exportar_formato={doc_type}&nombrearchivo={doc_name}&exportar_con_notas_bcn=False&exportar_con_notas_originales=False&exportar_con_notas_al_pie=False&hddResultadoExportar={doc_path}'
    #            item['country'] = self.country
    #            item['level'] = self.level
    #            item['data_source'] = self.source
    #            item['title'] = norm['TITULO_NORMA']
    #            item['reference'] = norm_id
    #            item['authorship'] = norm['ORGANISMO']
    #            item['resume'] = ""
    #            item['publication_date'] = pub_date_format
    #            item['enforcement_date'] = norm['FECHA_PROMULGACION']
    #            item['url'] = norm_url
    #            item['doc_url'] = doc_url
    #            item['doc_name'] = doc_name + '.' + doc_type
    #            item['doc_class'] = norm['DESCRIPCION']
    #            item['file_urls'] = [doc_url]
    #            item['doc_type'] = doc_type
    #            for column in item:
    #                item[column] = item[column] or False
    #            yield item




