


# Scrapy settings for scrapy_official_newspapers project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapy_official_newspapers'

SPIDER_MODULES = ['scrapy_official_newspapers.spiders']
# NEWSPIDER_MODULE = 'scrapy_official_newspapers.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Omdena - WRI'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 10
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
	'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
	'scrapy_official_newspapers.middlewares.ScrapyOfficialNewspapersSpiderMiddleware': 543,
	'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 600,
 }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# set the Splash URL to run the Slpash Middleware to access javascript rendered content
#Splash render service
# SPLASH_URL = 'http://localhost:8050'
#DEduplication filter
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
#Use Splash's Http cache
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
# DOWNLOADER_MIDDLEWARES = {
#    'scrapy_official_newspapers.middlewares.ScrapyOfficialNewspapersDownloaderMiddleware': 543,
    # 'scrapy_splash.SplashCookiesMiddleware': 723,
    # 'scrapy_splash.SplashMiddleware': 725,
    # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
 # }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html


ITEM_PIPELINES = {
    'scrapy.pipelines.files.FilesPipeline': 100,
    # 'scrapy_official_newspapers.pipelines.ScrapyOfficialNewspapersPipeline': 200,
    # 'scrapy_official_newspapers.pipelines.ScrapyOfficialNewspapersMySQLPipeline': 200,
}



# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 10
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 20
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


DB_USER = "Francisco Pérez"

#MySQL
CONNECTION_STRING = "{drivername}://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8".format(
    drivername="mysql+pymysql",
    user="JordiPlanas",
    passwd="1-gfJkw_",
    host="omdena-db-yaml.c9ozq65pvktb.us-west-1.rds.amazonaws.com",
    port="3306",
    db_name="wriLatin",
)

#S3
AWS_ACCESS_KEY_ID = "AKIA4TYLWXVC35TDDU6V"
AWS_SECRET_ACCESS_KEY = "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"
FILES_STORE = 's3://wri-latin-talent/'
