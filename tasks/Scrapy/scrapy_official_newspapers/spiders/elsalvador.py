import scrapy
import json
import datetime
import math
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider
from scrapy import Request


class ElSalvador(BaseSpider):
	name = "ElSalvador"
	country = "El Salvador"
	geo_code = "SLV-000-00000-0000000"
	level = "0"
	source = "https://www.jurisprudencia.gob.sv/busqueda/busquedaLeg.php?id=2"
	collector = "Jordi Planas"
	scrapper_name = "Jordi Planas"
	scrapable = "True"
	allowed_domains = ["jurisprudencia.gob.sv"]
	keywords = ["agropecuario", "ganadero", "ganadería", "energía", "energético", "energética", "agrícola"]#["forestal", "agrícola", "restauración", "uso del suelo", "minería", "medio ambiente"]
	info_url = ""
	counter = 0
	start_date = datetime.datetime.strptime("2015-01-01", '%Y-%m-%d').date()
	end_date = datetime.date.today().strftime('%Y-%m-%d')
	serch_results = 0
	# with open('./keywords_and_dictionaries/keywords_knowledge_domain.json', 'r') as dict:
		# keyword_dict = json.load(dict)
	# with open('./keywords_and_dictionaries/negative_keywords_knowledge_domain.json', 'r') as dict
		# negative_keyword_dict = json.load(dict)
		
	url_dict = {}

	def __init__(self, date="2020-01-01"):
		keyword_dict, negative_keyword_dict = self.import_filtering_keywords()
		try:
			self.from_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
		except:
			self.from_date = datetime.datetime.strptime(date, '%d-%m-%Y').date()
		self.from_date = self.from_date.strftime('%Y-%m-%d')
		date_today = datetime.date.today()
		self.today = date_today.strftime('%Y-%m-%d')

	def start_requests(self):
		for date in self.create_date_range(1990):
			for keyword in self.keywords:
				request = f"curl 'https://www.jurisprudencia.gob.sv/busqueda/result.php' -H 'Connection: keep-alive' -H 'Accept: */*' -H 'X-Requested-With: XMLHttpRequest' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Origin: https://www.jurisprudencia.gob.sv' -H 'Sec-Fetch-Site: same-origin' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Dest: empty' -H 'Referer: https://www.jurisprudencia.gob.sv/busqueda/busquedaLeg.php?id=2' -H 'Accept-Language: ca,en;q=0.9' -H 'Cookie: _ga=GA1.3.499250194.1605023569; _gid=GA1.3.1562076103.1605176978; wplc_chat_status=5; _icl_current_language=es; nc_status=browsing; PHPSESSID=emkambpjvphadn3r7lracuqvg6' --data-raw 'libre=true&txtBusquedaLibre={keyword}&baseDatos=2&nivel1=0&nivel2=0&nivel3=0&nivel4=0&maximo=300&inicio={date[0]}&fin={date[1]}&tipoBusquedaFrasePalabra=1' --compressed"
				yield Request.from_curl(request, callback = self.parse)

			
	def parse(self, response):
		
		for i in range(0, len(response.xpath('//*[@id="files"]/tbody/tr/td/h4/a'))):
			url = response.xpath('//*[@id="files"]/tbody/tr/td/a/@href')[i].get().replace("\'", "")
			self.info_url = url.replace("http", "https")
			if self.info_url in self.url_dict:
				pass
			else:
				self.url_dict[self.info_url] = 0
				try:
					yield Request(self.info_url, dont_filter = True, callback = self.parse_other)
				except Exception as e:
					print("\n---- There was an exception", e)
					pass
	
	def parse_other(self, response):
		self.counter += 1
		# print("\n----- Reccord processed succesfully\n\n", response.xpath('//*[@id="menu1"]/table').get(), "\n")
		item = ScrapyOfficialNewspapersItem()
		item['country'] = self.country
		item['geo_code'] = self.geo_code
		item['level'] = self.level
		item['data_source'] = self.source
		item['url'] = response.url
		# print("\n--- ", response.url)
		item['doc_type'] = 'pdf'
		item['doc_class'] = ""
		
		table = response.xpath('//*[@id="menu1"]/table').get()
		
		# print(response)
		item, good = self.parse_table(item, table)
		
		doc_url = response.xpath('//*[@id="menu2"]/comment()[2]').get().split("\"")[1]
		# print("\n+++++ ", doc_url, " +++++\n")
		item['file_urls'] = [doc_url]
		item['doc_url'] = doc_url
		if good:
			return item
		else:
			pass

	def parse_table(self, item_object, table):
		cells = table.split("<tr>")
		municipio = ""
		num_documento = "-"
		tipo_documento = ""
		resume = ""
		valid = True
		for cell in cells:
			# print("\n----- Reccord processed succesfully\n\n", cell, "\n")
			items = cell.split("</td>")
			if "Naturaleza [Legislación]" in items[0]:
				# print(self.remove_html_tags(items[1]).strip())
				tipo_documento = self.remove_html_tags(items[1]).strip()
			if "Número de decreto" in items[0]:
				# print(self.remove_html_tags(items[1]).strip())
				num_documento = num_documento + self.remove_html_tags(items[1]).strip()
			if "Tipo de documento" in items[0]:
				# print(self.remove_html_tags(items[1]).strip())
				tipo_1_documento = self.remove_html_tags(items[1]).strip()
			if "Municipio" in items[0]:
				# print(self.remove_html_tags(items[1]).strip())
				municipio = self.remove_html_tags(items[1]).strip()
			if "Nombre" in items[0]:
				# print(self.remove_html_tags(items[1]).strip())
				item_object['title'] = self.remove_html_tags(items[1]).strip().replace("”", "").replace("“","").replace("\"","")
			if "Fecha de Publicación en D. O." in items[0]:
				# print(self.remove_html_tags(items[1]).strip())
				item_object['publication_date'] = self.remove_html_tags(items[1]).strip()
				item_object['enforcement_date'] = self.remove_html_tags(items[1]).strip()
			if "Origen" in items[0]:
				# print(self.remove_html_tags(items[1]).strip())
				item_object['authorship'] = self.remove_html_tags(items[1]).strip()
			if "Consideraciones sobre el documento" in items[0]:
				resume = self.remove_html_tags(items[1]).strip()
				item_object['resume'] = self.remove_html_tags(items[1]).strip()
			if "Vigencia" in items[0]:
				if self.remove_html_tags(items[1]).strip() == "Vigente":
					item_object['enforcement_check'] = datetime.date.today().strftime('%d-%m-%y')
				else:
					valid = False
		# print(tipo_documento + "-" + num_documento)
		if tipo_documento == "":
			tipo_documento = tipo_1_documento
		if num_documento == "-":
			num_documento = ""
		if municipio != "":
			item_object['reference'] = tipo_documento + "-" + municipio + num_documento
			item_object['doc_name'] = "slv-" + tipo_documento + "-" + municipio + num_documento
		else:
			item_object['reference'] = tipo_documento + num_documento
			item_object['doc_name'] = "slv-" + tipo_documento + num_documento
		if self.search_keywords(resume, self.keyword_dict, self.negative_keyword_dict) and valid:
			return item_object, True
		else:
			return item_object, False
				
