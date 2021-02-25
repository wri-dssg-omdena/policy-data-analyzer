import scrapy
import json
import datetime
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
from scrapy_official_newspapers.spiders import BaseSpider

class IndiaCodeActs(BaseSpider):
    name = "IndiaCodeActs"
    country = "India"
    country_code = "IN" # You can find the ISO3166 country code here: https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
    state_name = "Federal&State"
    satate_code = "" # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "India Code"
    spider_builder = "Jordi Planas"
    scrapable = "True"
    allowed_domains = ["indiacode.nic.in/"]
    start_date = "2000-01-01"
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
        start_url = f'https://www.indiacode.nic.in/simple-search?query=forestry&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B{from_year}+TO+{to_year}%5D&filtertype=equals'
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
            self.title = tr.css('td::text')[1].get()
            if self.title in self.done_dictionary:
                pass
            else:
                self.done_dictionary[self.title] = 0
                i += 1
                #print('*** ', i, ' ***')
                self.publication_date = tr.css('td::text')[0].get()
                self.title = tr.css('td::text')[1].get()
                details_url = response.urljoin(tr.css('td').css('a::attr(href)').get())
                yield scrapy.Request(details_url, dont_filter=True, callback=self.parse_other)
                # print("\n", self.publication_date, " ** ", self.title, "\n")
                # print(details_url)
# //*[@id="content"]/div/div/div[1]/div/div[4]/div/table/tbody/tr[2]/td[1]
    #     for granule in json.loads(response.text)["granules"]:
    #         url = granule["granuleLink"] + f'?api_key={self.API_key}'
    #         yield scrapy.Request(url, dont_filter=True, callback=self.parse_other)

    def parse_other(self, response):
        doc_url =  response.urljoin(response.css('#short_title').css('a::attr(href)').get())
        doc_name = self.HSA1_encoding(doc_url) + doc_url.split('#')[0][-4:]
        self.debug(doc_name)
        for tr in response.css('#tb2 table tr'):
            if "Act ID" in tr.css('td')[0].get():
                reference = tr.css('td')[1].get()
            if "Ministry" in tr.css('td')[0].get():
                ministry = tr.css('td')[1].get()
            if "Department" in tr.css('td')[0].get():
                department = tr.css('td')[1].get()
            if "Location" in tr.css('td')[0].get():
                state_name = tr.css('td')[1].get()
            if "Long Title" in tr.css('td')[0].get():
                summary = tr.css('td')[1].get()
            else:
                summary = ""

            elif 


        #print(response.css("div#tb2 table tr").get())
        summary = response.xpath('//*[@id="tb2"]/div/div/table/tr[6]/td[2]/text()').get()
        self.debug(summary)
        text_to_search = self.title + " " + summary
        if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
            item = ScrapyOfficialNewspapersItem()

            item['country'] = self.country
            item['state'] = self.state_name
            item['data_source'] = self.source
            item['law_class'] = summary_full['category']
            item['title'] = summary_full['title']
            item['reference'] = summary_full['granuleId']
            item['authorship'] = summary_full['agencies'][0]['name']
            item['summary'] = summary
            item['publication_date'] = summary_full['dateIssued']
            item['url'] = summary_full['download']['txtLink'].replace('htm', 'summary?api_key=')
            item['doc_url'] = summary_full['download']['txtLink'] + '?api_key='
            item['doc_name'] = self.HSA1_encoding(summary_full['download']['txtLink'] + f'?api_key={self.API_key}')

    #         yield item




