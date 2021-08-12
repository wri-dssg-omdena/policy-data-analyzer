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
    state_code = "" # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "India Code"
    spider_builder = "Jordi Planas"
    scrapable = "True"
    allowed_domains = ["indiacode.nic.in/"]
    start_date = "2011-01-01"
    done_dictionary = {}
    
    def __init__(self):
        # First we import the two dictionaries that we are going to use to filter the policies.
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_EN.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain_EN.json')
        # This is to set the time span variables. 
        self.from_date, self.today = self.create_date_span(self.start_date)
        self.code_type = {1 : "Rules", 2 : "Regulation", 3 : "Notification", 4 : "Orders", 5 : "Circular", 6 : "Ordinances", 7 : "Statutes"}
        self.code_type_url = {1 : "Rule", 2 : "Regulation", 3 : "Notification", 4 : "Order", 5 : "Circular", 6 : "Ordinance", 7 : "Statute"}

    def start_requests(self):
        from_year = datetime.datetime.strptime(self.from_date, '%Y-%m-%d').year
        to_year = datetime.datetime.strptime(self.today, '%Y-%m-%d').year
        start = 0
        # start_url = f'https://www.indiacode.nic.in/simple-search?query=forestry&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B{from_year}+TO+{to_year}%5D&filtertype=equals'
        # yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)
        for i in range(0, len(self.keyword_dict)):
        #    self.debug(i)
           if i % 5 == 0:
               end = i
               query = self.build_query(self.keyword_dict, start, end)
               self.debug(query)
               start_url = f'https://www.indiacode.nic.in/simple-search?query={query}&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B{from_year}+TO+{to_year}%5D&filtertype=equals'
               self.debug(start_url)
               yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)
               start = i
           elif i == len(self.keyword_dict) - 1:
               end = i
               query = self. build_query(self.keyword_dict, start, end)
               self.debug(query)
               start_url = f'https://www.indiacode.nic.in/simple-search?query={query}&sort_by=score&order=desc&rpp=1000&etal=0&filtername=actyear&filterquery=%5B{from_year}+TO+{to_year}%5D&filtertype=equals'
               self.debug(start_url)
               yield scrapy.Request(start_url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        table = response.css('table')
        i = 0
        for tr in table.css('tr')[1:]:
            title = self.remove_html_tags(tr.css('td')[2].get()).replace("  ", " ")
            if title not in self.done_dictionary:
                self.done_dictionary[title] = 0
                details_url = response.urljoin(tr.css('td').css('a::attr(href)').get())
                yield scrapy.Request(details_url, dont_filter=True, callback=self.parse_other, cb_kwargs=dict(title_first = title, details_url = details_url))

    def parse_other(self, response, title_first, details_url):
        flag = True
        flag_1 = True
        flag_2 = True
        self.state_name = "Federal"
        ministry = ""
        department = ""
        for tr in response.css('#tb2 table tr'):
            if "Location" in tr.css('td')[0].get():
                self.state_name = tr.css('td::text')[1].get()
            if "Act ID" in tr.css('td')[0].get():
                reference = tr.css('td::text')[1].get()
                flag_1 = False
            if "Enactment" in tr.css('td::text')[0].get():
                publication_date = tr.css('td::text')[1].get()
            if "Short Title" in tr.css('td::text')[0].get():
                title = self.remove_html_tags(tr.css('td')[1].get()).replace("  ", " ").lstrip().rstrip()
                flag_2 = False
            if "Long Title" in tr.css('td::text')[0].get():
                summary = self.remove_html_tags(tr.css('td')[1].get()).lstrip().rstrip()
                flag = False
            if "Ministry" in tr.css('td')[0].get():
                ministry = tr.css('td::text')[1].get()
            if "Department" in tr.css('td')[0].get():
                department = tr.css('td::text')[1].get()
        if flag:
            summary = ''
        if flag_1:
            reference = "NA"
        if flag_2:
            title = title_first
            # print("\n*** No Act ID***\n")
        # if title_first == title or title_first == summary:
        #     print("\nTitle OK\n")

        text_to_search = title + " " + summary

        # if self.negative_keyword_filter(text_to_search, self.negative_keyword_dict):
        if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict):
            self.debug(title)
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
            item['url'] = details_url
            doc_url = response.urljoin(response.css('p#short_title').css('a::attr(href)').get())
            item['file_urls'] = [doc_url]
            item['doc_name'] = self.HSA1_encoding(doc_url) + doc_url.split('#')[0][-4:]
            yield item

            for type in self.code_type:
                id = "myModal" + str(type)
                for tr in response.css(f'div#{id}').css(f'table#myTable{self.code_type[type]} tr'):
                    check_title = tr.css('td::text')[1].get()
                    if check_title not in self.done_dictionary:
                        self.done_dictionary[check_title] = 0

                        item = ScrapyOfficialNewspapersItem()

                        item['country'] = self.country
                        item['state'] = self.state_name
                        item['data_source'] = self.source
                        item['law_class'] = self.code_type_url[type]
                        item['title'] = tr.css('td::text')[1].get()
                        item['reference'] = ""
                        item['authorship'] = ""
                        item['summary'] = ""
                        item['publication_date'] = tr.css('td::text')[0].get()
                        item['url'] = details_url
                        doc_id = tr.css('td')[2].css('a::attr(href)').get().split("=")[1]
                        doc_id = doc_id.split("/")[0]
                        doc_file = tr.css('td')[2].css('a::attr(href)').get().split("=")[2].lstrip().rstrip()
                        doc_url = "https://upload.indiacode.nic.in/showfile?actid=" + doc_id + "&type=" + self.code_type_url[type].lower() + "&filename=" + doc_file
                        item['file_urls'] = [doc_url]
                        item['doc_name'] = self.HSA1_encoding(doc_url) + doc_url.split('#')[0][-4:]
                        yield item


