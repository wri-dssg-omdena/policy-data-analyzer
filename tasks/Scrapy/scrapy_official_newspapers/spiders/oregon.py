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


class OregonSpider(scrapy.Spider):
    name = 'oregon'
    allowed_domains = ['secure.sos.state.or.us']
    start_urls = ['https://secure.sos.state.or.us/oard/displayBulletins.action']
    country = "Oregon"
    # geo_code = "MEX-000-00000-0000000"
    # level = "0"
    data_source = "The Oregon Bulletin"
    # title = "None"
    # years = [year for year in range(2018, 2020)]
    # collector = "Francisco Canales"
    # scrapper_name = "Francisco Canales"
    # scrapable = "True"
    # allowed_domains = ["dof.gob.mx"]
    # doc_name = None
    # doc_type = 'HTML'
   
    def parse(self, response):        
        # Iterate over URLs
        for href in response.css('div#accordion').css('a::attr(href)'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_month_bulletin)
    
    def parse_month_bulletin(self, response):
        # Get all table headers of the web page
        total_headers = response.css('table').css('thead').css('th::text').extract()
        # item = ScrapyOfficialNewspapersItem()
        item = defaultdict.fromkeys(total_headers)

        # Iterate over tables
        for table in response.css('table'):
            id = table.attrib['id']  # Notices or filings
            table_headers = table.css('thead').css('th::text').extract()
            # Iterate over table rows
            for tr in table.css('tbody').css('tr'):
                # Get all text in a single row of the table
                row_values = tr.css('td::text').getall()
                row_values = list(filter(None, map(lambda x: " ".join(x.split()), row_values)))
                assert len(table_headers) == len(row_values), 'More row values than table headers!'
                # Get the link of a single row of the table
                doc_url = response.urljoin(tr.css('a::attr(href)').extract_first())
                # Populate item dictionary
                item['id'] = id
                item.update(dict(zip(table_headers, row_values)))
                item['country'] = self.country
                # item['geo_code'] = self.geo_code
                # item['level'] = self.level
                item['data_source'] = self.data_source
                # item['title'] = resume
                # item['reference'] = reference
                # item['authorship'] = str(authorship)
                # item['resume'] = resume
                # item['publication_date'] = date
                # item['enforcement_date'] = date
                # item['url'] = response.url
                item['doc_url'] = doc_url
                # item['doc_name'] = reference+'html'
                # item['doc_type'] = self.doc_type
                # item['doc_class'] = ''
                # item['file_urls'] = [doc_url]
                yield item
