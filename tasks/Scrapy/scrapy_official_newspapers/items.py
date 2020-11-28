# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy




class ScrapyOfficialNewspapersItem(scrapy.Item):
    # define the fields for your item here like:
    country = scrapy.Field()
    geo_code = scrapy.Field()
    level = scrapy.Field()
    data_source = scrapy.Field()
    title = scrapy.Field()
    reference = scrapy.Field()
    authorship = scrapy.Field()
    resume = scrapy.Field()
    publication_date = scrapy.Field()
    enforcement_date = scrapy.Field()
    url = scrapy.Field()
    doc_url = scrapy.Field()
    doc_name = scrapy.Field()
    doc_class = scrapy.Field()
    doc_type = scrapy.Field()
    file_urls = scrapy.Field()
    pass