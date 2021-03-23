#import requests
#from bs4 import BeautifulSoup
#from scrapy_official_newspapers.items import ScrapyOfficialNewspapersItem
#from scrapy_official_newspapers.spiders import BaseSpider
#import scrapy
#from scrapy import Request
#from dateutil.parser import parse

#class MississippiSpider(BaseSpider):
#    name = 'Mississippi'
#    country = "USA"
#    country_code = "US" # You can find the ISO3166 country code here: https://gist.github.com/ssskip/5a94bfcd2835bf1dea52
#    state_name = "Mississippi"
#    state_code = 'MS' # As per the Holidays package, you can find the code here https://pypi.org/project/holidays/ if avaiable.
#    source = "The Mississippi Administrative Code"
#    spider_builder = "David Silva"
#    scrapable = "True"
#    allowed_domains = ['sos.ms.gov']
#    start_date = "2020-12-11"
#    start_urls = ['https://www.sos.ms.gov/adminsearch/default.aspx']
#    # years = [year for year in range(2018, 2020)]

#    def __init__(self):
#        # First we import the two dictionaries that we are going to use to filter the policies.
#        # self.keyword_dict = self.import_json('./keywords_and_dictionaries/keywords_knowledge_domain_EN.json')
#        # self.negative_keyword_dict = self.import_json('./keywords_and_dictionaries/negative_keywords_knowledge_domain.json')
#        # This is to set the time span variables. 
#        self.from_date, self.today = self.create_date_span(self.start_date)

#    def start_requests(self):
#        # Get the query keys i.e. the value of each option element in the form field
#        agencies = BeautifulSoup(requests.get(self.start_urls).content).find(id="agenciesDelim").get('value').split('^')[1:]
#        def to_dict(x):
#            x = x.split('~')
#            return x[0], f'Title {x[1]} - {x[2]}'
#        query_dict = {k: v for k, v in map(to_dict, agencies)}
#        # Iterate over desired dates
#        for date in self.create_date_range(self.from_date, self.today, 3):
#            for query_key, query_value in query_dict.items():
#                request = f"curl 'https://www.sos.ms.gov/adminsearch/AdminSearchService.asmx/CodeSearch' -H 'Connection: keep-alive' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36' -H 'X-Requested-With: XMLHttpRequest' -H 'Content-Type: application/json; charset=UTF-8' -H 'Accept: */*' -H 'Origin: https://www.sos.ms.gov' -H 'Sec-Fetch-Site: same-origin' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Dest: empty' -H 'Referer: https://www.sos.ms.gov/adminsearch/default.aspx' -H 'Accept-Language: pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6' -H 'Cookie: f5avraaaaaaaaaaaaaaaa_session_=BIKOAAKMGLBNCIHPKALHDJHJLGCOOLOGLJMFKNEGCOPKALBDLLLLCCDDNABNHMCEEEMDABIGIOOPOEEMIHEAKALFEOHCCMICFKBPHGGJEFDEAFFIOHAAKDEHEGFLDHMA; f5_cspm=1234; BIGipServerpl_sos_web_server_ext_https=rd1o00000000000000000000ffff0a0d3b0bo443; f5avr0011788986aaaaaaaaaaaaaaaa_cspm_=JGCGLMKNJPBOKODPKMFEGCHJHEBFCKPGABMJLOFGDOPKALBDLLLLCKDDNAHMHMCEEEMCABIGHAEPBLOMIHEAKALFACEEJCLEJMKMFIAJEFDEAFHJCMLNKLKHEGFLDHHA; BIGipServerpl_msi_prod_https=rd1o00000000000000000000ffff0a0df71fo443; f5avraaaaaaaaaaaaaaaa_session_=KNDODJGKCICNEHFDGLAEMLLKGHEBBHNJLGHPEGCEEFOJFGOAEHKCCDKABOOMHGHBPLLDAKPCKOFHJLADKHAAIDNOEOMKFDGILCCPIFDMKBFPIDJLEABGDLHEJGBAMJDM' --data-raw '{{'tmpSubject':'','tmpAgency':'{query_key}','tmpPartRange1':'','tmpPartRange2':'','tmpRuleSum':'','tmpOrder':'PartNo','tmpOrderDirec':'Ascending','tmpSearchDate1':'{date[0]}','tmpSearchDate2':'{date[1]}','tmpDateType':'0'}}' --compressed'"
#                yield Request.from_curl(request, callback = self.parse)

#    # WE NEED TO USE SCRAPY-SPLASH AS THE PAGE USES JAVASCRIPT. THE ACTUAL HTML OF THE PAGE CAN BE SEEN IN "View Page Source".
#    # TO GO OVER THE MULTIPLE SEARCH ARGUMENTS USE THE cURL(bash) together with the search term (the value from the options in the search bar) - curl 'https://www.sos.ms.gov/adminsearch/AdminSearchService.asmx/CodeSearch' -H 'Connection: keep-alive' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36' -H 'X-Requested-With: XMLHttpRequest' -H 'Content-Type: application/json; charset=UTF-8' -H 'Accept: */*' -H 'Origin: https://www.sos.ms.gov' -H 'Sec-Fetch-Site: same-origin' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Dest: empty' -H 'Referer: https://www.sos.ms.gov/adminsearch/default.aspx' -H 'Accept-Language: pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6' -H 'Cookie: f5avraaaaaaaaaaaaaaaa_session_=BIKOAAKMGLBNCIHPKALHDJHJLGCOOLOGLJMFKNEGCOPKALBDLLLLCCDDNABNHMCEEEMDABIGIOOPOEEMIHEAKALFEOHCCMICFKBPHGGJEFDEAFFIOHAAKDEHEGFLDHMA; f5_cspm=1234; BIGipServerpl_sos_web_server_ext_https=rd1o00000000000000000000ffff0a0d3b0bo443; f5avr0011788986aaaaaaaaaaaaaaaa_cspm_=JGCGLMKNJPBOKODPKMFEGCHJHEBFCKPGABMJLOFGDOPKALBDLLLLCKDDNAHMHMCEEEMCABIGHAEPBLOMIHEAKALFACEEJCLEJMKMFIAJEFDEAFHJCMLNKLKHEGFLDHHA; BIGipServerpl_msi_prod_https=rd1o00000000000000000000ffff0a0df71fo443; f5avraaaaaaaaaaaaaaaa_session_=KNDODJGKCICNEHFDGLAEMLLKGHEBBHNJLGHPEGCEEFOJFGOAEHKCCDKABOOMHGHBPLLDAKPCKOFHJLADKHAAIDNOEOMKFDGILCCPIFDMKBFPIDJLEABGDLHEJGBAMJDM' --data-raw '{"tmpSubject":"","tmpAgency":"54 ","tmpPartRange1":"","tmpPartRange2":"","tmpRuleSum":"","tmpOrder":"PartNo","tmpOrderDirec":"Ascending","tmpSearchDate1":"","tmpSearchDate2":"","tmpDateType":"0"}' --compressed
#    # FOR QUERY_DICT PAIR ("Title 7 - DEPARTMENT OF EDUCATION", 64) THERE'S MULTIPLE PAGES, HOWEVER IF WE USE THE CURL REQUEST WE GET ALL THE DOCUMENTS ACROSS PAGES
#    def parse(self, response):   
#        # Example of result of curl requests for first query: {"d":"SECRETARY OF STATE~1~5/31/2016~11/30/2011~Administrative Law~~169~00000169c.pdf^SECRETARY OF STATE~2~4/24/2018~11/30/2011~Organization and Executive Policies and Procedures~~170~00000170c.pdf^SECRETARY OF STATE~4~7/17/2017~11/30/2011~Business Services - Uniform Commercial Code Filings~~171~00000171c.pdf^SECRETARY OF STATE~5~12/27/2017~11/30/2011~Business Services - Notaries Public~~172~00000172c.pdf^SECRETARY OF STATE~7~8/19/2019~11/30/2011~Business Services - Miscellaneous~~173~00000173c.pdf^SECRETARY OF STATE~9~6/17/2015~11/30/2011~Elections - Campaign Finance and Lobbying~~174~00000174c.pdf^SECRETARY OF STATE~10~6/18/2019~11/30/2011~Elections - Voting and HAVA Compliance~~175~00000175c.pdf^SECRETARY OF STATE~11~12/4/2014~11/30/2011~Public Lands~~176~00000176c.pdf^SECRETARY OF STATE~12~8/11/2014~11/30/2011~Regulation and Enforcement - Preneed Funeral Service and Mdse. and Perpetual Care Cemeteries Regulation~~177~00000177c.pdf^SECRETARY OF STATE~13~4/4/2016~11/30/2011~Regulation and Enforcement - Scrap Metal Dealer Regulation~~178~00000178c.pdf^SECRETARY OF STATE~14~8/2/2019~11/30/2011~Securities Regulation~~179~00000179c.pdf^SECRETARY OF STATE~15~11/20/2017~11/30/2011~Charities Regulation~~180~00000180c.pdf^SECRETARY OF STATE~16~11/27/2013~12/27/2013~Elections- Voter Photo Identification~~534~00000534c.pdf^SECRETARY OF STATE~17~10/5/2020~11/3/2020~Part 17: Absentee Voting~~731~00000731c.pdf|14"}     
#        # We need to access element "d", split by "^" to get each element of the result, split each element by "~" to get each metadata field
#        # The one thing I cannot understand is how to get the pdf link. We only get access to the pdf name and the HTML code of the button to get the pdf is (I think it call a JS function): <input type="button" onclick="window.open('ACCode/00000169c.pdf');" style="border-style:solid; border-width:2px; border-radius:4px; font-weight:bold; color:#003F59; border-color:#94C0D2; background-color:transparent; cursor:pointer; padding:3px;" value="Part">
#        print("LOGGING ----- ", response)
#        elements = response['d'].split('^')
#        elements = map(lambda x: x.split('~'), elements)
        
#        item = ScrapyOfficialNewspapersItem()
#        # Iterate over elements
#        for elem in elements:
#            # Get the pdf document url
#            # doc_url = response.urljoin()
#            # Populate item dictionary
#            item['country'] = self.country
#            item['state'] = self.state_name
#            item['data_source'] = self.source
#            item['law_class'] = ''
#            item['agency'] = elem[0]
#            item['part_number'] = elem[1]
#            item['last_amended'] = elem[2]
#            item['effective_date'] = elem[3]
#            item['rule'] = elem[4]
#            item['summary'] = elem[5]
#            item['system_number'] = elem[6]
#            item['doc_url'] = elem[7]
#            # item['doc_name'] = self.HSA1_encoding(doc_url)
#            # item['doc_url'] = doc_url
#            item['title'] = ''
#            item['reference'] = ''
#            item['authorship'] = ''
#            item['summary'] = ''
#            item['publication_date'] = item['effective_date']
#            item['url'] = response.url
#            yield item