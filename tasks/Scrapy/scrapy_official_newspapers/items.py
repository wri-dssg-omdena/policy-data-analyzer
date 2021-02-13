# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy




class ScrapyOfficialNewspapersItem(scrapy.Item):
	# define the fields for your item here like:
	country = scrapy.Field()
	data_source = scrapy.Field() # Here we keep the name of the official newspaper. url of the page where we found all metainformation
	title = scrapy.Field() # The title of the policy
	reference = scrapy.Field() # The reference of the policy. We need to explain how we determine it in each spider
	authorship = scrapy.Field() # It is important to find which is the admiistrative body, whether a ministry, the office of the president etc.
	summary = scrapy.Field() # If available a summary of the law.
	publication_date = scrapy.Field() # The date of publication should always be accessible because we know what day the official newspaper was published
	enforcement_date = scrapy.Field() # Often the enforcement date is related with the publication date. In the US it is around 60 days from publication.
									  #If there is no specific info we put the same as the publication date.
	enforcement_check = scrapy.Field() # Some laws may become abrogate or may become without effect after a time if we can retrieve this info it is very
										# important. Here we should introduce the date of the last check
	url = scrapy.Field() # Here we keep the url of the page where we found all metainformation
	doc_url = scrapy.Field() # Here we keep the url of the page where we can retrieve the actua text of the law.
	doc_name = scrapy.Field()
	doc_class = scrapy.Field()
	doc_type = scrapy.Field()
	file_urls = scrapy.Field()
	pass