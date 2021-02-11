
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
 

# import search scrape data ------------------------------------------------------------------------

search_scrape <- as.data.frame(read_feather( 
          here(
                "tasks",
                "scrape",
                "ecolex",
                "search_scrape",
                "output",
                "WRI_Ecolex_Scrape_Search_Results.feather")
))


# Scrape ECOLEX document profiles ------------------------------------------------------- 

scrape_df <- search_scrape
 
#ECOLEX scrape -----
the_output <- vector("character")
all_references_combined <- vector("character")

for(i in 1:nrow(scrape_df)) {
  
eco_url <- str_c("https://www.ecolex.org",scrape_df[i, "TITLE_URL"])

eco_scrape <- NULL
#If there is an http error -- repeat 5 times before skipping
attempt <- 0
while (is.null(eco_scrape) && attempt <= 5) {
      attempt <- attempt + 1
      if(attempt > 1) {Sys.sleep(runif(1, min = 1, max = 5))}
      try(
            eco_scrape <- read_html(eco_url)
            )
} 

#if read_html fails 5 times, skip
if(is.null(eco_scrape)) {next}

#add delay based on GET response time
t0 <- Sys.time()
response <- httr::GET(eco_url)
t1 <- Sys.time()
response_delay <- as.numeric(t1-t0) * 5
Sys.sleep(response_delay)

 
REFERENCE_LINK <- eco_scrape %>%
    html_nodes("p.search-result-source a") %>%
    html_attr("href")


if(length(REFERENCE_LINK) > 0) {
reference_link_type <- str_squish(eco_scrape %>%
    html_nodes("#legislation-references") %>%
    html_text())


oth_reference_link_type <- str_squish(eco_scrape %>%
    html_nodes("#other-references") %>%
    html_text())

if(length(oth_reference_link_type) > 0) {
  
  reference_link_type <-  str_c(reference_link_type, oth_reference_link_type) 
  
}
 

all_references <- unlist(str_extract_all(reference_link_type,
                                         "Implements treaty|Implemented by|Amends|Amended by|Implements|Source"))

all_references <- data.frame(RELATIONSHIP_ORIGINAL = all_references,
                             RELATIONSHIP_FINAL = NA, 
                             stringsAsFactors = F) 

the_final_reference <- all_references[1,"RELATIONSHIP_ORIGINAL"]
for(z in 1:nrow(all_references)) {
  
  the_non_sources <- str_subset(all_references$RELATIONSHIP_ORIGINAL, "Source", negate = T)
  
  the_final_reference <- case_when(
    all_references[z,"RELATIONSHIP_ORIGINAL"] == "Source" ~ the_final_reference,
    TRUE ~ all_references[z,"RELATIONSHIP_ORIGINAL"]
  )
 
  all_references[z,"RELATIONSHIP_FINAL"] <- the_final_reference
  
}

all_references <- all_references %>%
  filter(RELATIONSHIP_ORIGINAL == "Source") %>%
  select(REFERENCE_LINK_RELATIONSHIP = RELATIONSHIP_FINAL) %>%
  bind_cols(data.frame(REFERENCE_LINK, stringsAsFactors = F)) %>%
  mutate(TITLE_URL = scrape_df[i, "TITLE_URL"],
         POLICY_ID = scrape_df[i, "POLICY_ID"]) %>%
  mutate(REFERENCE_POLICY_ID = case_when(
  grepl("LEX-",REFERENCE_LINK) ~ str_extract(REFERENCE_LINK, "[^\\/]+$"),
  TRUE ~ NA_character_)) %>%
  select(TITLE_URL, POLICY_ID, everything())
  
} else {
  
  all_references <- NULL
  
}


get_html_text <- function(the_css,
                          is_link = FALSE) {
  
  if(is_link == FALSE) {
    
    the_html_text <- eco_scrape %>%
    html_nodes(css = the_css) %>%
    html_text()
    
  } else {
    
    the_html_text <- eco_scrape %>%
    html_nodes(css = the_css) %>%
    html_attr("href")
    
  }
  
 
  if(length(the_html_text) == 0) {
    the_html_text <- NA_character_
  }
  
  the_html_text
  
}

temp_df <- data.frame(
  POLICY_ID = scrape_df[i, "POLICY_ID"],
  DOCUMENT_TYPE = get_html_text(
    the_css = "#search-form > main > div > article > header > dl > dd:nth-child(4)"),
  SUBJECT = get_html_text(
    the_css = "#details > dl > dd:nth-child(2)"),
  GEOGRAPHIC_AREA = get_html_text(
    the_css = "#details > dl > dd:nth-child(6)"),
  ABSTRACT = get_html_text(
    the_css = "#text > dl > dd:nth-child(2) > p"),
  FULL_DOC_LINK = get_html_text(
    the_css = "#text > dl > dd:nth-child(4) > a",
    is_link = TRUE),
  RESPONSE_DELAY = response_delay,
  stringsAsFactors = F
)


the_output <- bind_rows(the_output, temp_df)

all_references_combined <- bind_rows(all_references_combined, all_references)

print(str_c("Scraped page ",i, " of ", nrow(scrape_df), " (",
            round((i/nrow(scrape_df)) * 100), "% complete).",
            " Estimated time left is ", 
            round((mean(the_output$RESPONSE_DELAY, na.rm = T) * (nrow(scrape_df) - i)) / 60, 1),
            " minutes"))

}

#Clean --------------------------------------------------------------------------------------------

policy_references <- all_references_combined %>%
  filter(!is.na(POLICY_ID))


policy_profiles <- scrape_df %>%
  left_join(
    the_output %>%
      filter(!is.na(POLICY_ID)) %>%
      select(-RESPONSE_DELAY)
  ) %>%
   select(POLICY_ID, PAGE:TYPE, DOCUMENT_TYPE, DATE,
         GEOGRAPHIC_AREA, JURISDICTION,
         SUBJECT, KEYWORDS,
         ALL_SOURCES, SOURCE_W_URL, SOURCE_URL,
         ABSTRACT, FULL_DOC_LINK
         )


ifelse(sum(!(search_scrape$POLICY_ID %in% the_output$POLICY_ID)) > 0,
       warning("REVIEW RESULTS -- Not all search_srape POLICY_IDs are in policy_profiles", call. = F),
       "SUCCESS -- all POLICY_IDs from search_scrape are in policy_profiles")



# Scrape FAOLEX for complete abstract ------------------
# TO DO



#Export Ecolex Policy Profiles --------------------------------------------------------------------

write.csv(policy_profiles,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "document_scrape",
                "output",
                "WRI_Ecolex_Scrape_Policy_Profiles.csv"),
          row.names = F
)

write_feather(policy_profiles,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "document_scrape",
                "output",
                "WRI_Ecolex_Scrape_Policy_Profiles.feather")
)


write.csv(policy_references,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "document_scrape",
                "output",
                "WRI_Ecolex_Scrape_Policy_References.csv"),
          row.names = F
)

write_feather(policy_references,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "document_scrape",
                "output",
                "WRI_Ecolex_Scrape_Policy_References.feather")
)

