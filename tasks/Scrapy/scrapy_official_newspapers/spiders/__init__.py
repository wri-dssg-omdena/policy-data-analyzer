# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import datetime
from dateparser import parse
from dateutil import relativedelta
import json
import locale
import re
from scrapy.spiders import Spider


class BaseSpider(Spider):
	def parse_date(self, raw_date):
		import re
		date = re.search(r'(\d+/\d+/\d+)', raw_date)
		date = date.group(0)
		return (self.validate_date(date))

	def validate_date(self, date_text):
		from dateutil.parser import parse
		try:
			parse(date_text, dayfirst=True)
			return date_text
		except ValueError as err:
			return err

	def transform_spanish_date(self, date):
		return parse(date, ['es']).strftime('%Y-%m-%d')
		
		
	def create_date_span(self, fromDate):
		try:
			from_date = datetime.datetime.strptime(fromDate, '%Y-%m-%d').date()
		except:
			from_date = datetime.datetime.strptime(fromDate, '%d-%m-%Y').date()
		from_date = from_date.strftime('%Y-%m-%d')
		date_today = datetime.date.today()
		today = date_today.strftime('%Y-%m-%d')
		return from_date, today

	def create_date_range(self, stop_date, to_date, time_span):
		# to_date = datetime.date.today()
		stop_date = datetime.datetime.strptime(stop_date, '%Y-%m-%d').date()
		to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
		dates = []
		while stop_date.year < to_date.year:
			from_date = to_date + relativedelta(years = -time_span)
			dates.append([from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d')])
			to_date = from_date
		return dates
	def add_leading_zero_two_digits(self, number):
		if number < 10:
			num = "0" + str(number)
		else:
			num = str(number)
		return (num)

	def import_filtering_keywords(self):
		with open('./keywords_and_dictionaries/keywords_knowledge_domain.json', 'r') as dict:
			keyword_dict = json.load(dict)
		with open('./keywords_and_dictionaries/negative_keywords_knowledge_domain.json', 'r') as dict:
			negative_keyword_dict = json.load(dict)
		return keyword_dict, negative_keyword_dict

	def search_keywords(self,string, keyword_dict, negative_keyword_dict):
		string = string.lower()
		for word in keyword_dict:
			if word.lower() in string:
				flag = False
				for negative in negative_keyword_dict:
					if negative.lower() in string:
						resp = False
						flag = False
						break
					else:
						flag = True
				if flag:
					resp = True
					break
			else:
				resp = False
		return(resp)

	def clean_text(self, string):
		string = string.replace("\n", " ")
		string = string.replace("-", " ")
		return(string)
		
	def remove_html_tags(self, text):
		"""Remove html tags from a string"""
		clean = re.compile('<.*?>')
		return re.sub(clean, '', text)


