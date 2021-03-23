
#Load Packages ------------------------------------------------------------------------
#Add all required lists to the list.of.packages object
#missing packages will be automatically installed
list.of.packages <- c("tidyverse", 
                      "here", 
                      "feather")

new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]

if(length(new.packages)) install.packages(new.packages)

#load all required packages
lapply(list.of.packages, require, character.only = TRUE)

#Remove scientific notation
options(scipen=999)

#print working directory
here()
 

# Import ------------------------------------------------------------------------------------------

policy_profiles <- read_feather( 
          here(
                "tasks",
                "scrape",
                "ecolex",
                "document_scrape",
                "output",
                "WRI_Ecolex_Scrape_Policy_Profiles.feather")
) %>%
  as.data.frame()


# Extract keywords --------------------------------------------------------------------------------

keywords <- policy_profiles %>%
  pull(KEYWORDS)

keywords <- sort(unique(unlist(str_split(string = keywords, pattern = ", "))))

keywords_df <- data.frame(keywords,
                          use_for_search = NA,
                          stringsAsFactors = F)


# Extract subjects --------------------------------------------------------------------------------

subjects <- policy_profiles %>%
  pull(SUBJECT)

subjects <- sort(unique(unlist(str_split(string = subjects, pattern = ", "))))

subjects_df <- data.frame(subjects,
                          use_for_search = NA,
                          stringsAsFactors = F)


#Export Ecolex Search Results ---------------------------------------------------------------------

write.csv(keywords_df,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "extract_keywords",
                "output",
                "WRI_Ecolex_keywords.csv"),
          row.names = F
)

write.csv(subjects_df,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "extract_keywords",
                "output",
                "WRI_Ecolex_subjects.csv"),
          row.names = F
)

