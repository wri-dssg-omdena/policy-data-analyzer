# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import boto3
import json
from dateutil.relativedelta import relativedelta
import datetime
from icecream import ic
import hashlib
import holidays
import logging
import re
from scrapy.spiders import Spider
from scrapy.utils.log import configure_logging


class BaseSpider(Spider):
	logging.getLogger('scrapy.core.scraper').addFilter(lambda x: not x.getMessage().startswith('Scraped from')) #To avoid printing item in the terminal prompt
	configure_logging(install_root_handler=True)
	logging.disable(10)  # DEBUG = 10, INFO = 20, WARNING = 30, ERROR = 40; CRITICAL = 50
	def add_leading_zero_two_digits(self, number):
		if number < 10:
			num = "0" + str(number)
		else:
			num = str(number)
		return (num)
	
	def build_query(self, keyword_dict, start_keyword, end_keyword):
		i = 0
		k = 0
		query = ""
		for item in keyword_dict:
			if start_keyword < k < end_keyword:
				item = item.replace("-" ,"")
				j = 0
				if len(item.split()) > 1:
					combined = "%28"
					for keyword in item.split():
						if j==0 :
							combined = combined + keyword
							j = 1
						else:
							combined = combined + "+" + keyword
					combined = combined + "%29"
					if i == 0:
						query = combined
						i = 1
					else:
						query = query + "+OR+" + combined
				else:
					if i == 0:
						query = item
						i = 1
					else:
						query = query + "+OR+" + item
			k += 1
		return query


	def clean_text(self, string):
		string = string.replace("\n", " ")
		string = string.replace("-", " ")
		return(string)

	def create_date_span(self, fromDate):
		try:
			from_date = datetime.datetime.strptime(fromDate, '%Y-%m-%d').date()
		except:
			from_date = datetime.datetime.strptime(fromDate, '%d-%m-%Y').date()
		from_date = from_date.strftime('%Y-%m-%d')
		date_today = datetime.date.today()
		today = date_today.strftime('%Y-%m-%d')
		return from_date, today

	def create_date_range(self, start_date, to_date, time_span):
		# to_date = datetime.date.today()
		start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
		to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
		dates = []
		while start_date.year < to_date.year:
			from_date = to_date + relativedelta(years = -time_span)
			dates.append([from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d')])
			to_date = from_date
		return dates

	def create_date_list(self, start_date, to_date, time_span, time_unit, country_code):
		dates = []
		start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
		to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
		while start_date < to_date:
			start_date = self.next_business_day(start_date, time_span, time_unit, country_code)
			dates.append(start_date)
		return dates

	def debug(self, to_debug):
		ic(to_debug)

	def findWholeWord(self, word):
		return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search

	def HSA1_encoding(self, string):
		hash_object = hashlib.sha1(string.encode())
		return hash_object.hexdigest()

	def import_json(self, filename):
		with open(filename, 'r') as dict:
			json_dict = json.load(dict)
		return json_dict

	def negative_keyword_filter(self,string, negative_keyword_dict):
		string = string.lower()
		resp = True
		for negative_word in negative_keyword_dict:
			if self.findWholeWord(negative_word.lower())(string) != None:
				resp = False
				break
		return(resp)

	def next_business_day(self, date, time_span, time_unit, country_code):
		ONE_DAY = datetime.timedelta(days=1)
		HOLIDAYS = holidays.CountryHoliday(country_code)
		next_day = date + ONE_DAY
		while next_day.weekday() in holidays.WEEKEND or next_day in HOLIDAYS:
		   next_day += ONE_DAY
		return next_day

	def open_S3_session(self, credentials_file, bucket, bucket_region):
		with open(credentials_file, 'r') as dict:
			credentials = json.load(dict)
										
		KEY = list(credentials)[0]
		SECRET = list(credentials.values())[0]
		s3BucketName = bucket
		region = bucket_region
		s3 = boto3.resource(
			service_name = 's3',
			region_name = region,
			aws_access_key_id = KEY,
			aws_secret_access_key = SECRET
		)
		return s3

	def parse_date(self, raw_date):
		date = re.search(r'(\d+/\d+/\d+)', raw_date)
		date = date.group(0)
		return (self.validate_date(date))

	def remove_html_tags(self, text):
		"""Remove html tags from a string"""
		clean = re.compile('<.*?>')
		return re.sub(clean, '', text)

	def save_dict(file, dictionary):
		with open(file, 'w') as fp:
			json.dump(dictionary, fp)

	def save_to_s3(self, s3, bucket, file_key, text):
		s3.Object(bucket, file_key).put(Body = text)

	def search_keywords(self,string, keyword_dict, negative_keyword_dict):
		string = string.lower()
		for positive_word in keyword_dict:
			if self.findWholeWord(positive_word)(string) != None:
				flag = False
				for negative_word in negative_keyword_dict:
					if self.findWholeWord(negative_word)(string) != None:
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

	def validate_date(self, date_text):
		from dateutil.parser import parse
		try:
			parse(date_text, dayfirst=True)
			return date_text
		except ValueError as err:
			return err


