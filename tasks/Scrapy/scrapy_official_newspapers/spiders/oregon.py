# The Oregon Bulletin is a monthly online publication containing Notices of Proposed Rulemaking, 
# Permanent and Temporary Administrative Rule filings, along with rule text; as well as Minor 
# Correction filings. The Bulletin also includes non-OAR (Oregon Administrative Rules) items when
# they are submitted, such as Executive Orders of the Governor and Opinions of the Attorney General
# About the OARs
# ​​Administrative Rules are created by most agencies and some boards and commissions to implement and
# interpret their statutory authority (ORS 183.310(9)). Agencies may adopt, amend, repeal or renumber
# rules, permanently or temporarily (for up to 180 days).
# Every OAR uses the same numbering sequence of a three-digit chapter number followed by a three-digit 
# division number and a four-digit rule number. For example, Oregon Administrative Rules, chapter 166,
# division 500, rule 0020 is cited as OAR 166-500-0020.
# Changes to existing Rules are listed chronologically in abbreviated form, with the most recent 
# change last. For example, "OSA 4-1993, f. & cert. ef. 11-10-93," means this was the 4th administrative 
# rule filing by the Oregon State Archives in 1993; and "f. & cert. ef. 11-10-93" means the rule was 
# filed and certified effective on Nov. 10, 1993.
# The official copy of an Oregon Administrative Rule is the Administrative Order filed at the Archives
# Division. Any discrepancies with the published version are satisfied in favor of the Administrative Order
from collections import defaultdict
from scrapy_official_newspapers.spiders import BaseSpider
from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
import scrapy
from dateutil.parser import parse


class OregonSpider(BaseSpider):
    name = 'Oregon'
    country = "USA"
    country_code = "US" # You can find the ISO3166 country code here: https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
    state_name = "Oregon"
    state_code = 'OR' # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
    source = "The Oregon Bulletin"
    spider_builder = "David Silva"
    scrapable = "True"
    allowed_domains = ['secure.sos.state.or.us']
    start_date = "2020-12-11"
    start_urls = ['https://secure.sos.state.or.us/oard/displayBulletins.action']
    # years = [year for year in range(2018, 2020)]

    def __init__(self):
        # First we import the two dictionaries that we are going to use to filter the policies.
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_EN.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain.json')
        # This is to set the time span variables. 
        self.from_date, self.today = self.create_date_span(self.start_date)


    def parse(self, response):        
        # Iterate over URLs
        i = 0
        for bulletin in response.css('div#accordion').css('a'):
            # Get the url and the text of the element, the text being the publication date
            self.url = response.urljoin(bulletin.css('::attr(href)').get())
            publication_date = bulletin.css('::text').get().replace("\xa0\xa0", "-")
            # Filter by date and request
            if parse(self.from_date) <= parse(publication_date) <= parse(self.today):
                #self.debug(publication_date)
                yield scrapy.Request(self.url, callback=self.parse_month_bulletin)
    
    def parse_month_bulletin(self, response):
        # Get all table headers of the web page
        #total_headers = response.css('table').css('thead').css('th::text').extract_first()
        #item = defaultdict.fromkeys(total_headers)
        item = ScrapyOfficialNewspapersItem()

        # We take only the first table, we could loop through the two tables if there is a need to get the information of the second table
        #id = table.attrib['id']  # Notices or filings
        #table_headers = table.css('thead').css('th::text').extract()
        table = response.css('table')[0]
        ## Iterate over table rows
        for tr in table.css('tbody').css('tr'):
            # Get all text in a single row of the table
            row_values = tr.css('td::text').getall()
            row_values = list(filter(None, map(lambda x: " ".join(x.split()), row_values)))
            #assert len(table_headers) == len(row_values), 'More row values than table headers!'
            # Get the link of a single row of the table
            doc_url = response.urljoin(tr.css('a::attr(href)').extract_first())
            # Populate item dictionary
            #item.update(dict(zip(table_headers, row_values)))
            #self.debug(row_values)
            text_to_search = row_values[3]
            if self.search_keywords(text_to_search, self.keyword_dict, self.negative_keyword_dict) or self.scrapable == "True":
                item['country'] = self.country
                item['state'] = self.state_name
                item['data_source'] = self.source
                item['law_class'] = ''
                item['title'] = row_values[3]
                item['reference'] = ''
                item['authorship'] = row_values[1]
                item['summary'] = ''
                item['publication_date'] = parse(row_values[2].split(' ')[0]).strftime('%Y-%m-%d')
                item['url'] = response.url
                item['doc_url'] = doc_url
                item['doc_name'] = self.HSA1_encoding(doc_url)
                yield item
                                                   