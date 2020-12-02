# Scrapy Tool for Omdena Latam LFR Challenge 
Web Crawling application running *Scrapy* Tool, extracting official policies from the following sources:

### Characteristics of the information sources

### Chile (LeyChile)

**Search type:** Exhaustive, through API , limited by the pages_num

**Speed:** Fast

**Amount of avaliable documents:** 10-100k

**Document Type:** HTML


### Mexico Distrito oficial de la Federación 
**Search type:** Exhaustive, through scrapping (Xpath) , limited by years range.

**Speed:**  Terrible slow and buggy when you change pipelines order

**Amount of avaliable documents:** 10-100k

**Document Type:** HTML

### El Peruano
**Search type:**

**Speed:**

**Amount of avaliable documents:**

**Document Type:**





# Setup Steps:
## Recommendations:
Use a virtual environment not your python system to run and also to install the dependencies.

## Install dependencies

```
pip install -r requirements.txt
```



## Scrapy settings.py
https://drive.google.com/file/d/1bjbjYSXQqZQpJdwATRCLZFSRQciiULy-/view?usp=sharing
### Warning!
S3 upload pipeline and MySQL insert pipeline doesn't work together.
Use:
```
ITEM_PIPELINES = {
    # 'scrapy.pipelines.files.FilesPipeline': 100,
    'scrapy_official_newspapers.pipelines.ScrapyOfficialNewspapersMySQLPipeline': 200,
        }
```

and 

```
ITEM_PIPELINES = {
     'scrapy.pipelines.files.FilesPipeline': 100,
    #'scrapy_official_newspapers.pipelines.ScrapyOfficialNewspapersMySQLPipeline': 200,
        }
```
The order doesn't mind.

## Database access
Setup the DB access inserting settings.json into *scrappy_official_newspapers*.

```
{
  "username": "username",
  "password": "password",
  "db_name": "db_name",
  "aws_endpoint": "your_db_instance_access"
}
```


## S3 Access
Setup scrapy *settings.py* located at *scrappy_official_newspapers*
```
AWS_ACCESS_KEY_ID = "XXXXXXXXXXXXXXXXXXXX"
AWS_SECRET_ACCESS_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
FILES_STORE = 's3://wri-latin-test/'
```


## Run
from repository root:
* cd scrapy_official_newspapers
* scrapy crawl leychile
* scrapy crawl MexicoDOF

## Monitorization/Debug/Test
Through mysql table inspection, you can check how the information is being inserted.

Through https://console.aws.amazon.com/console/home after authenticating you can navigate to S3 Service, you can check the files uploaded and their properties.

## Goal
Provide a structured information system, from multiple variated sources formats containing raw official policy documents, keeping the reference to their attributes.

## Attributes
country

geo_code

level

source

title

reference

authorship

resume

publication_date

enforcement_date
url

doc_url

doc_name

doc_type

file_urls (Needed for Scrappy S3FilesPipeline, Not in DB Schema)

Not implemented like that, but the idea is to also keep track of:
* file_raw_S3_url
* file_proccesed_task_1_S3_url 

So we are able to keep track of the policies with their attributes and also have the capability of maintaining the relationships and results of different processes.

## What is this information system:
Policies Documents Stored and indexed through the integration of a relational MySQL database and AWS S3 media database service (FTP would work too), with most attributes such as the title of the act, a resume of the document, the date of publication... 


## Documentation:
https://docs.scrapy.org/en/2.2/

https://docs.scrapy.org/en/2.2/topics/media-pipeline.html#enabling-your-media-pipeline

## Recomendations:
Do not make an extensive use of the tool, probably information will be thrown because it is still in development, you can collapse the target's resources and engraving amazon's bill through this.


