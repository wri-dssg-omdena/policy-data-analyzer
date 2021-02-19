# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy




class ScrapyOfficialNewspapersItem(scrapy.Item):
	# define the fields for your item here like:
	country = scrapy.Field()
	state = scrapy.Field()
	data_source = scrapy.Field() # Here we keep the name of the official newspaper
	law_class = scrapy.Field()# Some times the policies are categorized on whether they are laws, decrees, rules etc.
	title = scrapy.Field() # The title of the policy
	reference = scrapy.Field() # The reference of the policy. We need to explain how we determine it in each spider
	authorship = scrapy.Field() # It is important to find which is the admiistrative body, whether a ministry, the office of the president etc.
	summary = scrapy.Field() # If available a summary of the law.
	publication_date = scrapy.Field() # The date of publication should always be accessible because we know what day the official newspaper was published
	url = scrapy.Field() # Here we keep the url of the page where we found all metainformation
	doc_url = scrapy.Field() # Here we keep the url of the page where we can retrieve the actua text of the law.
	doc_name = scrapy.Field() # This is the HSA1 token of the doc_url
	pass