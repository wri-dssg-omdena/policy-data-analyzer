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
    start_date = "2020-01-01"
    start_url = f'https://api.govinfo.gov/packages/FR/granules?offset=0&pageSize=300'
    
    def __init__(self):
        # First we import the two dictionaries that we are going to use to filter the policies.
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_EN.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain_ES.json')
        # This is to set the time span variables. 
        self.from_date, self.today = self.create_date_span(self.start_date)
    
    def start_requests(self):
        from_year = datetime.datetime.strptime(self.from_date, '%Y-%m-%d').year
        to_year = datetime.datetime.strptime(self.today, '%Y-%m-%d').year
        i = 0
        k = 0
        for item in self.keyword_dict:
            if k < 30:
                k += 1
                item = item.replace("-" ,"")
                j = 0
                if len(item.split()) > 1:
                    combined = "%28"
                    for keyword in item.split():
                        if j==0 :
                            combined = combined + keyword
                            j = 1
                        else:
                            combined = combined + "+" + keyword
                    combined = combined + "%29"
                    if i == 0:
                        query = combined
                        i = 1
                    else:
                        query = query + "+OR+" + combined
                else:
                    if i == 0:
                        query = item
                        i = 1
                    else:
                        query = query + "+OR+" + item
        self.debug(query)
        start_url = f'https://www.indiacode.nic.in/simple-search?query={query}&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B2000+TO+2021%5D&filtertype=equals'
        yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        table = response.css('table')
        i = 0
        for tr in table.css('tr')[1:]:
            i += 1
            print('*** ', i, ' ***')
            self.publication_date = tr.css('td::text')[0].get()
            self.title = tr.css('td::text')[1].get()
            details_url = response.urljoin(tr.css('td').css('a::attr(href)').get())
            # print("\n", self.publication_date, " ** ", self.title, "\n")
            # print(details_url)
# //*[@id="content"]/div/div/div[1]/div/div[4]/div/table/tbody/tr[2]/td[1]
    #     for granule in json.loads(response.text)["granules"]:
    #         url = granule["granuleLink"] + f'?api_key={self.API_key}'
    #         yield scrapy.Request(url, dont_filter=True, callback=self.parse_other)

    # def parse_other(self, response):
    #     summary_full = response.json()
    #     #self.debug(summary_full)
    #     title = summary_full["title"]
    #     if "summary" in summary_full:
    #         summary = summary_full["summary"]
    #     else:
    #         summary = ""
    #     text_to_search = summary_full["title"] + " " + summary
    #     if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
    #         item = ScrapyOfficialNewspapersItem()
    #         item['country'] = self.country
    #         item['state'] = self.state_name
    #         item['data_source'] = self.source
    #         item['law_class'] = summary_full['category']
    #         item['title'] = summary_full['title']
    #         item['reference'] = summary_full['granuleId']
    #         item['authorship'] = summary_full['agencies'][0]['name']
    #         item['summary'] = summary
    #         item['publication_date'] = summary_full['dateIssued']
    #         item['url'] = summary_full['download']['txtLink'].replace('htm', 'summary?api_key=')
    #         item['doc_url'] = summary_full['download']['txtLink'] + '?api_key='
    #         item['doc_name'] = self.HSA1_encoding(summary_full['download']['txtLink'] + f'?api_key={self.API_key}')

    #         yield item




