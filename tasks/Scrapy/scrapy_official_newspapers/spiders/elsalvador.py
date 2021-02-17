import scrapy
import datetime
import math
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider
from scrapy import Request


class ElSalvador(BaseSpider):
	name = "ElSalvador"
	country = "El Salvador"
	state = "Federal"
	source = "Diario Oficial"
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

	url_dict = {}

	def __init__(self, date="2020-01-01"):
		self.keyword_dict, self.negative_keyword_dict = self.import_filtering_keywords()
		self.from_date, self.today = self.create_date_span(date)

	def start_requests(self):
		for date in self.create_date_range(self.from_date, self.today, 3):
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
		item['state'] = self.state
		item['data_source'] = self.source
		item['url'] = response.url
		
		table = response.xpath('//*[@id="menu1"]/table').get()

		item, good = self.parse_table(item, table)
		
		doc_url = response.xpath('//*[@id="menu2"]/comment()[2]').get().split("\"")[1]
		item['doc_url'] = doc_url
		item['doc_name'] = self.HSA1_encoding(doc_url)
		if good:
			yield item
		else:
			pass

	def parse_table(self, item_object, table):
		cells = table.split("<tr>")
		municipio = ""
		num_documento = "-"
		tipo_documento = ""
		summary = ""
		valid = True
		for cell in cells:
			rows = cell.split("</td>")
			if "Naturaleza [Legislación]" in rows[0]:
				tipo_documento = self.remove_html_tags(rows[1]).strip()
			if "Número de decreto" in rows[0]:
				num_documento = num_documento + self.remove_html_tags(rows[1]).strip()
			if "Tipo de documento" in rows[0]:
				tipo_1_documento = self.remove_html_tags(rows[1]).strip()
			if "Municipio" in rows[0]:
				municipio = self.remove_html_tags(rows[1]).strip()
			if "Nombre" in rows[0]:
				title = self.remove_html_tags(rows[1]).strip().replace("”", "").replace("“","").replace("\"","")
				item_object['title'] = title
			if "Fecha de Publicación en D. O." in rows[0]:
				item_object['publication_date'] = self.remove_html_tags(rows[1]).strip()
			if "Origen" in rows[0]:
				item_object['authorship'] = self.remove_html_tags(rows[1]).strip()
			if "Consideraciones sobre el documento" in rows[0]:
				summary = self.remove_html_tags(rows[1]).strip()
				text_to_search = title + " " + summary
				item_object['summary'] = summary
			if "Vigencia" in rows[0]:
				if self.remove_html_tags(rows[1]).strip() == "Vigente":
					valid = True
				else:
					valid = False
		# print(tipo_documento + "-" + num_documento)
		if tipo_documento == "":
			tipo_documento = tipo_1_documento
		item_object["law_class"] = tipo_documento
		if num_documento == "-":
			num_documento = ""
		if municipio != "":
			item_object['reference'] = tipo_documento + "-" + municipio + num_documento
		else:
			item_object['reference'] = tipo_documento + num_documento
		if self.search_keywords(texttext_to_search, self.keyword_dict, self.negative_keyword_dict) and valid:
			return item_object, True
		else:
			return item_object, False
				
