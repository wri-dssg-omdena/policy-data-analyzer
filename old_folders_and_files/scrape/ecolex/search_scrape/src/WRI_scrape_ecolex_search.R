
#Load Packages ------------------------------------------------------------------------
#Add all required lists to the list.of.packages object
#missing packages will be automatically installed
list.of.packages <- c("tidyverse", 
                      "here", 
                      "feather",
                      "rvest",
                      "httr")

new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]

if(length(new.packages)) install.packages(new.packages)

#load all required packages
lapply(list.of.packages, require, character.only = TRUE)

#Remove scientific notation
options(scipen=999)

#print working directory
here()
 

# Add search filters -------------------------------------------------------------------------------

search_terms <- NULL #"incentivo OR arboles"

document_type <-"legislation"
#see https://www.ecolex.org/result/?q= for document type values

countries <- c("Chile",
               "El Salvador",
               "Guatemala",
               "Peru",
               "Mexico")
#see https://www.ecolex.org/result/?q= for country values

subjects <- NULL 
#Full list of subjects: 'Agricultural & rural development','Air & atmosphere','Cultivated plants',
#'Energy','Environment gen.','Fisheries','Food & nutrition','Forestry',
#'Land & soil','Legal questions','Livestock','Mineral resources','Sea',
#'Waste & hazardous substances','Water','Wild species & ecosystems' 


keywords <- NULL #c("authorization / permit", "biotechnology")
#list of keywords: http://www.fao.org/faolex/glossary/en/

# Create the base URL ------------------------------------------------------------------------------

add_filter_path <- function(word_vector = NULL, 
                            preface = NULL,
                            use_the_AND_conditional = FALSE) {
  
  first_preface <- preface
  
  if(use_the_AND_conditional == TRUE) {
    first_preface <- str_c(gsub("=", "_and_=on", preface),
                         preface)
 
  }
  
  word_vector <- gsub("\\s{0,}\\/\\s{0,}", "%2F", word_vector)
  word_vector <- gsub("\\s{0,},\\s{0,}", "%2C", word_vector)
  word_vector <- gsub("\\s{0,}&\\s{0,}", "%26", word_vector)
  word_vector <- gsub("\\s{0,}\\+\\s{0,}", "%2B", word_vector)
  word_vector <- gsub(" ", "+", word_vector)
  
  the_path <- str_c(first_preface,
                    str_c(word_vector,
                         collapse = preface))
  
  the_path <- case_when(
    the_path == preface ~ "",
    TRUE ~ the_path
  )
  
}


search_terms_filter <-
  add_filter_path(
    word_vector = search_terms,
    preface = "q=",
    use_the_AND_conditional = FALSE
  )

document_type_filter <-
  add_filter_path(
    word_vector = tolower(document_type),
    preface = "&type=",
    use_the_AND_conditional = FALSE
  )

countries_filter <- add_filter_path(
  word_vector = str_to_title(countries),
  preface = "&xcountry=",
  use_the_AND_conditional = FALSE
) #instead of "OR"

subjects_filter <-
  add_filter_path(
    word_vector = subjects,
    preface = "&xsubjects=",
    use_the_AND_conditional = FALSE
  )

keywords_filter <-
add_filter_path(
  word_vector = keywords,
  preface = "&xkeywords=",
  use_the_AND_conditional = FALSE
)
 

base_url <- str_c(
  "https://www.ecolex.org/result/?",
  search_terms_filter,
  document_type_filter,
  countries_filter,
  subjects_filter,
  keywords_filter,
  "&page=" 
)


#original
# base_url <- str_c(
#   "https://www.ecolex.org/result/?",
#   "type=legislation",
#   "&xcountry=Chile&xcountry=El+Salvador&xcountry=Guatemala&xcountry=Peru&xcountry=Mexico",
#   "&page=" 
# )


# Extract total number of pages to scrape-----------------------------------------------------------

first_page <- str_c(
 base_url,
 1
)

prep_scrape <- NULL
#If there is an http error -- repeat 5 times before skipping
attempt <- 0
while (is.null(prep_scrape) && attempt <= 5) {
      attempt <- attempt + 1
      if(attempt > 1) {Sys.sleep(runif(1, min = 1, max = 5))}
      try(
            prep_scrape <- read_html(first_page)
            )
} 


total_number_of_pages <- prep_scrape %>% 
  html_nodes(".btn.btn-sm.btn-default") %>% 
  html_text() 
total_number_of_pages <- str_squish(trimws(total_number_of_pages))
total_number_of_pages <- max(as.numeric(str_extract(total_number_of_pages, "(\\d{1,})")), na.rm = T)


# Scrape ------------------------------------------------------------------------------------------

the_output <- vector("character")

for(the_page in 1:total_number_of_pages) {
  
#Sys.sleep(runif(1, min = 1, max = 3))

the_url <- str_c(
  base_url,
  the_page
)



test_scrape <- NULL
#If there is an http error -- repeat 5 times before skipping
attempt <- 0
while (is.null(test_scrape) && attempt <= 5) {
      attempt <- attempt + 1
      if(attempt > 1) {Sys.sleep(runif(1, min = 1, max = 5))}
      try(
            test_scrape <- read_html(the_url)
            )
} 

#if read_html fails 5 times, skip
if(is.null(test_scrape)) {next}

#add delay based on GET response time
t0 <- Sys.time()
response <- httr::GET(the_url)
t1 <- Sys.time()
response_delay <- as.numeric(t1-t0) * 8
Sys.sleep(response_delay)


the_date <- test_scrape %>% 
  html_nodes(".sr-date") %>% 
  html_text() 

the_date <- str_squish(trimws(the_date))
the_date <- str_subset(the_date,"^\\(" ,negate = T)

SOURCES = test_scrape %>% 
  html_nodes(".search-result-source") %>% 
  html_text() 

ALL_SOURCES <- gsub("Source: ","",str_squish(trimws(SOURCES)))


temp_df <- data.frame(
  PAGE = the_page,
  URL = the_url,
  TITLE = test_scrape %>%
    html_nodes(".search-result-title a") %>%
    html_text(),
  TITLE_URL = test_scrape %>%
    html_nodes(".search-result-title a") %>%
    html_attr("href"),
  TYPE = test_scrape %>%
    html_nodes(".sr-type") %>%
    html_text(),
  JURISDICTION = test_scrape %>%
    html_nodes(".sr-jurisdiction") %>%
    html_text(),
  DATE = the_date,
  KEYWORDS = test_scrape %>%
    html_nodes(".collapse-keywords") %>%
    html_text(),
  ALL_SOURCES,
  SOURCE_W_URL = test_scrape %>%
    html_nodes(".search-result-source a") %>%
    html_text(),
  SOURCE_URL = test_scrape %>%
    html_nodes(".search-result-source a") %>%
    html_attr("href"),
  RESPONSE_DELAY = response_delay,
  stringsAsFactors = F
)

the_output <- bind_rows(the_output, temp_df)

print(str_c("Scraped page ",the_page, " of ", total_number_of_pages, " (",
            round((the_page/total_number_of_pages) * 100), "% complete).",
            " Estimated time left is ", 
            round((mean(the_output$RESPONSE_DELAY, na.rm = T) * (total_number_of_pages - the_page)) / 60, 1),
            " minutes"))

}


#Clean --------------------------------------------------------------------------------------------

final_output <- as.data.frame(the_output %>%
                              filter(rowSums(!is.na(select(., one_of(colnames(the_output))))) >= 1)) %>%
  mutate(POLICY_ID = case_when(
    !is.na(SOURCE_URL) & SOURCE_W_URL == "FAOLEX" ~str_extract(SOURCE_URL, "[^\\/]+$"),
    TRUE ~ NA_character_)) %>%
  select(-RESPONSE_DELAY)


#one hot code the keywords?
#Pull out the date in the parenthesis (ORIGINAL_DATE, UPDATED_DATE)


#Export Ecolex Search Results --------------------------------------------------------------------

write.csv(final_output,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "search_scrape",
                "output",
                "WRI_Ecolex_Scrape_Search_Results.csv"),
          row.names = F
)

write_feather(final_output,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "search_scrape",
                "output",
                "WRI_Ecolex_Scrape_Search_Results.feather")
)

