
#Load Packages ------------------------------------------------------------------------
#Add all required lists to the list.of.packages object
#missing packages will be automatically installed
list.of.packages <- c("tidyverse", 
                      "here", 
                      "feather",
                      "readxl")

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


keywords_tagged <- readxl::read_excel(
            here(
                "tasks",
                "scrape",
                "ecolex",
                "relevance_classification",
                "prep",
                "input",
                "WRI_Ecolex_keywords_tagged.xlsx")
) %>%
  as.data.frame() 

subjects_tagged <- readxl::read_excel(
            here(
                "tasks",
                "scrape",
                "ecolex",
                "relevance_classification",
                "prep",
                "input",
                "WRI_Ecolex_subjects_tagged.xlsx")
) %>%
  as.data.frame()  


the_seed <- read_csv(
            here(
                "tasks",
                "scrape",
                "ecolex",
                "relevance_classification",
                "prep",
                "input",
                "the_seed_used.csv")
) %>%
  pull(as.integer(seed_string))


# Subset Profiles by keyword and subjects ----------------------------------------------------------
keywords_include <- keywords_tagged %>%
  filter(use_for_search == 1) %>%
  pull(keywords)

keywords_exclude <- keywords_tagged %>%
  filter(use_for_search != 1) %>%
  pull(keywords)

subjects_include <- subjects_tagged %>%
  filter(use_for_search == 1) %>%
  pull(subjects)

subjects_exclude <- subjects_tagged %>%
  filter(use_for_search != 1) %>%
  pull(subjects)


policy_profiles$n_relevant_keywords <- 
  sapply(policy_profiles[,"KEYWORDS"], function(x) {
  sum(str_detect(x, keywords_include))
  })

policy_profiles$n_irrelevant_keywords <- 
  sapply(policy_profiles[,"KEYWORDS"], function(x) {
  sum(str_detect(x, keywords_exclude))
  })

policy_profiles$n_relevant_subjects <- 
  sapply(policy_profiles[,"SUBJECT"], function(x) {
  sum(str_detect(x, subjects_include))
  })

policy_profiles$n_irrelevant_subjects <- 
  sapply(policy_profiles[,"SUBJECT"], function(x) {
  sum(str_detect(x, subjects_exclude))
  })

policy_profiles <- policy_profiles %>%
  mutate(prop_relevant_keywords = round(n_relevant_keywords / 
                                          (n_relevant_keywords + n_irrelevant_keywords), 5),
         prop_relevant_subjects = round(n_relevant_subjects / 
                                          (n_relevant_subjects + n_irrelevant_subjects), 5))
 

policy_profiles_w_keyword_and_subject <- policy_profiles %>%
  filter(n_relevant_keywords > 0 & n_relevant_subjects > 0)


#NOTE: originally set the seed for 4893 (i.e. set.seed(4893)), but while reviewing this code,
#I was unable to replicate the original sample. To replicate, I needed to run the code twice 
#(the first time setting the seed and the second time not setting the seed). 
#I captured the random seed being used in the second run, which I put into the_seed_used.csv 
#and provides the seed needed to replicate the original sample. 
#More on .Random.seed here: http://www.cookbook-r.com/Numbers/Saving_the_state_of_the_random_number_generator/
.Random.seed <- the_seed

policy_profiles_all_relevant_sample <-
  policy_profiles_w_keyword_and_subject %>%
  sample_n(size = 1000, replace = F) %>%
  select(POLICY_ID,
         FULL_DOC_LINK,
         TITLE,
         DATE,
         SUBJECT,
         KEYWORDS,
         ABSTRACT) %>%
  mutate(
    IS_RESTORATION	 = NA,
    IS_INCENTIVE		 = NA,
    REVIEWED_FULL_DOC	 = NA
  )

policy_profiles <- policy_profiles %>%
  mutate(IN_INITIAL_FILTER = case_when(
    POLICY_ID %in% policy_profiles_w_keyword_and_subject$POLICY_ID ~ 1,
    TRUE ~ 0
  ) )


#Export Ecolex Search Results ---------------------------------------------------------------------

write.csv(policy_profiles,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "relevance_classification",
                "prep",
                "output",
                "WRI_Ecolex_relevance_classification_all.csv"),
          row.names = F
)


write.csv(policy_profiles_all_relevant_sample,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "relevance_classification",
                "prep",
                "output",
                "WRI_Ecolex_relevance_classification_sample.csv"),
          row.names = F
)
 
