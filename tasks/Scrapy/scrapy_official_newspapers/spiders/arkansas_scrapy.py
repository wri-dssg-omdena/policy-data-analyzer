# -*- coding: utf-8 -*-
import scrapy
from arkanasa_policy_scrapy.items import ArkanasaPolicyScrapyItem
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.http import Request
import re
import request

class ArkansasScrapySpider(scrapy.Spider):
    name = 'arkansas_scrapy'
       
    
    country = "USA"
    state = "Arkansas"
    #need to specify the geo_code for USA_AR
    geo_code = "USA-000-00000-0000000"
    # does level 0 refer to country level, then state level is 1?
    level = "1"
    #The following criteria define the endpoint of url
    collector = "Rong Fang"
    scrapper_name = "Rong Fang"
    scrapable = "True"
    source = "https://www.arkleg.state.ar.us"
    #search_type = "/Acts/Search?start=0&bienniumAll=on&hdnSessions=on"
    #sessions = "%2Cb2021%2Cz2021R%2Cb2019%2Cz2019R%2Cz2020F%2Cz2020S1%2Cb2017%2Cz2017R%2Cz2017S1%2Cz2018F%2Cz2018S2%2Cb2015%2Cz2015R%2Cz2015S1%2Cz2016F%2Cz2016S2%2Cz2016S3%2Cb2013%2Cz2013R%2Cz2013S1%2Cz2014F%2Cz2014S2%2Cb2011%2Cz2011R%2Cz2012F%2Cb2009%2Cz2009R%2Cz2010F%2Cb2007%2Cz2007R%2Cz2008S1%2Cb2005%2Cz2005R%2Cz2006S1%2Cb2003%2Cz2003R%2Cz2003S1%2Cz2003S2%2Cb2001%2Cz2001R%2Cz2002S1%2Cb1999%2Cz1999R%2Cz1999S1%2Cz2000S2%2Cb1997%2Cz1997R%2Cb1995%2Cz1995R%2Cz1995S1%2Cb1993%2Cz1993R%2Cz1993S1%2Cz1994S2%2Cb1991%2Cz1991R%2Cz1991S1%2Cz1991S2%2Cb1989%2Cz1989R%2Cz1989S1%2Cz1989S2%2Cz1989S3%2Cb1987%2Cz1987R%2Cz1987S1%2Cz1987S2%2Cz1987S3%2Cz1987S4%2C&ddChamber=A&ddExclusivity=Only&ddBienniumSession=2021%2F2021R"
   
    #searching_end = "#SearchResults"
    keywords = ['Agroforestry', 'Forests', 'Forestry', 'Forester','Plantation','land ownership','Conservation',
                'Preservation','Restoration','Natural Resources','Incentive','Wildlife','Logging','Timber',
                'Forest Fire','Forest Protection']
    start_urls = []
    
    for keyword in keywords:
        start_urls.append(f"https://www.arkleg.state.ar.us/Acts/Search?tbType=&ddBienniumSession=2021%2F2021R&bienniumAll=on&hdnSessions=on%2Cb2021%2Cz2021R%2Cb2019%2Cz2019R%2Cz2020F%2Cz2020S1%2Cb2017%2Cz2017R%2Cz2017S1%2Cz2018F%2Cz2018S2%2Cb2015%2Cz2015R%2Cz2015S1%2Cz2016F%2Cz2016S2%2Cz2016S3%2Cb2013%2Cz2013R%2Cz2013S1%2Cz2014F%2Cz2014S2%2Cb2011%2Cz2011R%2Cz2012F%2Cb2009%2Cz2009R%2Cz2010F%2Cb2007%2Cz2007R%2Cz2008S1%2Cb2005%2Cz2005R%2Cz2006S1%2Cb2003%2Cz2003R%2Cz2003S1%2Cz2003S2%2Cb2001%2Cz2001R%2Cz2002S1%2Cb1999%2Cz1999R%2Cz1999S1%2Cz2000S2%2Cb1997%2Cz1997R%2Cb1995%2Cz1995R%2Cz1995S1%2Cb1993%2Cz1993R%2Cz1993S1%2Cz1994S2%2Cb1991%2Cz1991R%2Cz1991S1%2Cz1991S2%2Cb1989%2Cz1989R%2Cz1989S1%2Cz1989S2%2Cz1989S3%2Cb1987%2Cz1987R%2Cz1987S1%2Cz1987S2%2Cz1987S3%2Cz1987S4%2C&ddChamber=A&tbActNumber=&tbBillNumber=&ddSponsor=&tbAllWords={keyword}&tbExactPhrase=&tbOneWord=&tbWithoutWords=&ddExclusivity=Only")
  
    
    
    def start_request(self):
        #set multiple start url for the searching results of different keywords
        return [Request(url) for url in self.start_urls]
	     
    def parse(self, response):
        #Find the total number of pages of searching results
        total_pages=int(response.xpath('//div[@class="row tableSectionFooter"]\
                 /div[@class="col-sm-12 col-md-12 col-lg-12"]\
                 /text()').extract_first().split(' ')[3][:-1])+1
        keyword=re.findall("tbAllWords=(.*?)&", response.url)[0]
        for i in range(0, total_pages):
            num = i*20
            url = f"https://www.arkleg.state.ar.us/Acts/Search?start={num}?tbType=&ddBienniumSession=2021%2F2021R&bienniumAll=on&hdnSessions=on%2Cb2021%2Cz2021R%2Cb2019%2Cz2019R%2Cz2020F%2Cz2020S1%2Cb2017%2Cz2017R%2Cz2017S1%2Cz2018F%2Cz2018S2%2Cb2015%2Cz2015R%2Cz2015S1%2Cz2016F%2Cz2016S2%2Cz2016S3%2Cb2013%2Cz2013R%2Cz2013S1%2Cz2014F%2Cz2014S2%2Cb2011%2Cz2011R%2Cz2012F%2Cb2009%2Cz2009R%2Cz2010F%2Cb2007%2Cz2007R%2Cz2008S1%2Cb2005%2Cz2005R%2Cz2006S1%2Cb2003%2Cz2003R%2Cz2003S1%2Cz2003S2%2Cb2001%2Cz2001R%2Cz2002S1%2Cb1999%2Cz1999R%2Cz1999S1%2Cz2000S2%2Cb1997%2Cz1997R%2Cb1995%2Cz1995R%2Cz1995S1%2Cb1993%2Cz1993R%2Cz1993S1%2Cz1994S2%2Cb1991%2Cz1991R%2Cz1991S1%2Cz1991S2%2Cb1989%2Cz1989R%2Cz1989S1%2Cz1989S2%2Cz1989S3%2Cb1987%2Cz1987R%2Cz1987S1%2Cz1987S2%2Cz1987S3%2Cz1987S4%2C&ddChamber=A&tbActNumber=&tbBillNumber=&ddSponsor=&tbAllWords={keyword}&tbExactPhrase=&tbOneWord=&tbWithoutWords=&ddExclusivity=Only"

            yield scrapy.Request(url, dont_filter=True, callback=self.parse_page)
        

    def parse_page(self, response):
        if response.css('p.errormessage::text').extract_first() == 'No results found!':
            pass
        else:
            keyword=re.findall("tbAllWords=(.*?)&", response.url)[0]
            """Extract all items in a page"""
            for res in response.xpath('//div[@aria-hidden="true"]/div'):
                section_class=res.xpath("@class").extract()[0]
                if section_class=='row tableHeader':
                   continue
                if section_class=='row tableSectionHeader':
                   """Extract the session name and year"""
                   session_list = res.css('div').extract_first().split('\r\n')
                   session_name_year=session_list[2].replace('                                            ','').split(',')
                   session_name=session_name_year[0]
                   session_year=session_name_year[1].replace(' ',"")
                   continue
                if section_class=='row tableRow':
                   act_code=res.css('a::text').extract()[1]
                   act_title=res.css('div::text').extract()[5].replace("\r\n                                       ","").replace("\r\n","")
                   act_pdf_href=res.css('a::attr(href)').extract()[1]
                   act_sponsor=res.css('a::text').extract()[2]
                if section_class=='row tableRowAlt':
                   act_code=res.css('a::text').extract()[1]
                   act_title=res.css('div::text').extract()[5].replace("\r\n                                       ","").replace("\r\n","")
                   act_pdf_href=res.css('a::attr(href)').extract()[1]
                   act_sponsor=res.css('a::text').extract()[2]
                item = ArkanasaPolicyScrapyItem()
                item['country'] = 'USA'
                item['state'] = 'Arkansas'
                item['geo_code'] = "USA-000-00000-0000000"
                item['level'] = "1"
                item['data_source'] = "https://www.arkleg.state.ar.us"
                item['sponsorship'] = act_sponsor
                item['title'] = act_title
                item['publication_date'] = session_year
                #item['enforcement_date'] = item['publication_date']
                item['url'] = response.request.url
                item['session_name']=session_name
                item['doc_name'] = ('USA/AR/policy_' + act_code)
                item['doc_type'] = 'pdf'
                item['doc_class'] = keyword
                item['file_urls'] = "https://www.arkleg.state.ar.us" + act_pdf_href
                yield item

