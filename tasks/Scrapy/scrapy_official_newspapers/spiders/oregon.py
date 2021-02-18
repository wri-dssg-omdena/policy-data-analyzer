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
    allowed_domains = ['secure.sos.state.or.us']
    start_urls = ['https://secure.sos.state.or.us/oard/displayBulletins.action']
    country = "USA"
    state = "Oregon"
    data_source = "The Oregon Bulletin"
    scrapable = "True"
    # years = [year for year in range(2018, 2020)]
    spider_builder = "David Silva"

    def __init__(self, date = "2020-12-11"):
        self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain.json')
        self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain.json')
        self.from_date, self.today = self.create_date_span(date)


    def parse(self, response):        
        # Iterate over URLs
        i = 0
        for bulletin in response.css('div#accordion').css('a'):
            # Get the url and the text of the element, the textbeing the publication date
            self.url = response.urljoin(bulletin.css('::attr(href)').get())
            publication_date = bulletin.css('::text').get().replace("\xa0\xa0", "-")
            # Filter by date and request
            if parse(self.from_date) <= parse(publication_date) <= parse(self.today):
                #self.debug(publication_date)
                yield scrapy.Request(self.url, callback=self.parse_month_bulletin)
    
    def parse_month_bulletin(self, response):
        # Get all table headers of the web page
        #total_headers = response.css('table').css('thead').css('th::text').extract_first()
        item = ScrapyOfficialNewspapersItem()
        #item = defaultdict.fromkeys(total_headers)

        # We take only the first table and we could loop through the two tables if there is a need to get the information of the second table
        table = response.css('table')[0]
        #id = table.attrib['id']  # Notices or filings
        #table_headers = table.css('thead').css('th::text').extract()
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
                item['state'] = self.state
                item['data_source'] = self.data_source
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
                                                   