
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

policy_profiles_w_keyword_and_subject <- read.csv(
  here(
    "tasks",
    "scrape",
    "ecolex",
    "relevance_classification",
    "prep",
    "output",
    "WRI_Ecolex_relevance_classification_all.csv"
  ),
  stringsAsFactors = F
) %>%
  as.data.frame()

#SOURCE: https://onedrive.live.com/view.aspx?cid=c675544ac4321f5c&page=view&resid=C675544AC4321F5C!1256&parId=C675544AC4321F5C!125&authkey=!APg_S4HvxM_JBBw&app=Excel

policy_tags <- read_excel(
  here(
    "tasks",
    "scrape",
    "ecolex",
    "relevance_classification",
    "join_tags",
    "input",
    "WRI_Ecolex_relevance_classification_sample_complete.xlsx"
  )
  
) %>%
  as.data.frame()


# Join -------------------------------------------------------------------------------------------

policy_profiles_w_tags_subset <- policy_profiles_w_keyword_and_subject %>%
  left_join(policy_tags %>%
              select(POLICY_ID, 
                     IS_RESTORATION,
                     IS_INCENTIVE, 
                     REVIEWED_FULL_DOC)) %>%
  rename(n_WRI_keywords = n_relevant_keywords,
         n_WRI_subjects = n_relevant_subjects) %>%
  select(-starts_with("n_irrelevant"),
         -starts_with("prop"))



#Export Ecolex Search Results ---------------------------------------------------------------------

write.csv(policy_profiles_w_tags_subset,
          here(
                "tasks",
                "scrape",
                "ecolex",
                "relevance_classification",
                "join_tags",
                "output",
                "WRI_Ecolex_policy_profiles_w_labeled_sample.csv"),
          row.names = F
)

write_feather(policy_profiles_w_tags_subset, 
            here(
                "tasks",
                "scrape",
                "ecolex",
                "relevance_classification",
                "join_tags",
                "output",
                "WRI_Ecolex_policy_profiles_w_labeled_sample.feather") 
)


 
