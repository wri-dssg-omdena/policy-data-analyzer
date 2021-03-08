import scrapy
import json
import datetime
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider

class IndiaCodeActs(BaseSpider):
    name = "India"
    country = "India"
    country_code = "IN" # You can find the ISO3166 country code here: https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
    state_name = "Federal"
    satate_code = "" # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "India Code"
    spider_builder = "Jordi Planas"
    scrapable = "True"
    allowed_domains = ["indiacode.nic.in/"]
    start_date = "1950-01-01"
    done_dictionary = {}
    
    def __init__(self):
        # First we import the two dictionaries that we are going to use to filter the policies.
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_EN.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain_ES.json')
        # This is to set the time span variables. 
        self.from_date, self.today = self.create_date_span(self.start_date)

    def start_requests(self):
        from_year = datetime.datetime.strptime(self.from_date, '%Y-%m-%d').year
        to_year = datetime.datetime.strptime(self.today, '%Y-%m-%d').year
        start = 0
        start_url = f'https://www.indiacode.nic.in/handle/123456789/1362/simple-search?page-token=20535654ba20&page-token-value=376eba4759ae6cdc1a288873fa82b701&nccharset=6FB91D47&location=123456789%2F1362&query=The+University+Grants+Commission+Act&rpp=10&sort_by=score&order=desc&filter_field_1=title&filter_type_1=contains&filter_value_1=The+University+Grants+Commission+Act'
        #f'https://www.indiacode.nic.in/handle/123456789/1362/simple-search?page-token=c2035d749fe0&page-token-value=e8416433108e80650fe97479b9d11464&nccharset=5CA7ECED&location=%2F&query=forestry&rpp=10&sort_by=score&order=desc&filter_field_1=actyear&filter_type_1=equals&filter_value_1=%5B2000+TO+2020%5D'
        # f'https://www.indiacode.nic.in/simple-search?query=forestry&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B{from_year}+TO+{to_year}%5D&filtertype=equals'
        yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)
        #for i in range(0, len(self.keyword_dict)):
        #    self.debug(i)
        #    if i % 20 == 0:
        #        end = i
        #        query = self. build_query(self.keyword_dict, start, end)
        #        self.debug(query)
        #        start_url = f'https://www.indiacode.nic.in/simple-search?query={query}&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B{from_year}+TO+{to_year}%5D&filtertype=equals'
        #        yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)
        #        start = i
        #    elif i == len(self.keyword_dict) - 1:
        #        end = i
        #        query = self. build_query(self.keyword_dict, start, end)
        #        self.debug(query)
        #        start_url = f'https://www.indiacode.nic.in/simple-search?query={query}&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B{from_year}+TO+{to_year}%5D&filtertype=equals'
        #        yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        table = response.css('table')
        i = 0
        for tr in table.css('tr')[1:]:
            self.title = self.remove_html_tags(tr.css('td')[2].get()).replace("  ", " ")
            if self.title in self.done_dictionary:
                pass
            else:
                self.done_dictionary[self.title] = 0
                self.details_url = response.urljoin(tr.css('td').css('a::attr(href)').get())
                yield scrapy.Request(self.details_url, dont_filter=True, callback=self.parse_other)

    def parse_other(self, response):
        flag = True
        for tr in response.css('#tb2 table tr'):
            if "Location" in tr.css('td')[0].get():
                self.state_name = tr.css('td::text')[1].get()
            if "Act ID" in tr.css('td')[0].get():
                reference = tr.css('td::text')[1].get()
                self.debug(reference)
            if "Enactment" in tr.css('td::text')[0].get():
                publication_date = tr.css('td::text')[1].get()
            if "Short Title" in tr.css('td::text')[0].get():
                title = self.remove_html_tags(tr.css('td')[1].get()).replace("  ", " ").lstrip().rstrip()
            if "Long Title" in tr.css('td::text')[0].get():
                summary = self.remove_html_tags(tr.css('td')[1].get()).lstrip().rstrip()
                self.debug(summary)
                flag = False
            if "Ministry" in tr.css('td')[0].get():
                ministry = tr.css('td::text')[1].get()
            if "Department" in tr.css('td')[0].get():
                department = tr.css('td::text')[1].get()
        if flag:
            summary = ''

        item = ScrapyOfficialNewspapersItem()

        item['country'] = self.country
        item['state'] = self.state_name
        item['data_source'] = self.source
        item['law_class'] = "Act"
        item['title'] = title
        item['reference'] = reference
        item['authorship'] = ministry + "/" + department
        item['summary'] = summary
        item['publication_date'] = publication_date
        item['url'] = self.details_url
        doc_url = response.urljoin(response.css('#short_title').css('a::attr(href)').get())
        item['file_urls'] = [doc_url]
        item['doc_name'] = self.HSA1_encoding(doc_url) + doc_url.split('#')[0][-4:]
        yield item

        code_type = {1 : "Rules", 2 : "Regulation", 3 : "Notification", 4 : "Orders", 5 : "Circular", 6 : "Ordinances", 7 : "Statutes"}
        for type in code_type:
            id = "myModal" + str(type)
            print("\n %%% ", id, " %%%\n")
            for tr in response.css(f'div#{id}').css(f'table#myTable{code_type[type]} tr'):
                print("\n   -- HELLO -- ", id, " -- ", tr.css('td::text').get())



