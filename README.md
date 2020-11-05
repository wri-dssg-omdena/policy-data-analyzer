Current Roadmap
==============================
### Phase 1: Classifying documents as relevant/non-relevant

**Current Data**
- PDF Docs (NOT from Ecolex) in [OneDrive link](https://onedrive.live.com/?authkey=%21APg%5FS4HvxM%5FJBBw&id=C675544AC4321F5C%21125&cid=C675544AC4321F5C) 
- Policy document information (around 12k+) from Ecolex, including `Title, Subjects, Keywords, Abstract` (NOT the actual documents, also in OneDrive link)

**Tasks** 
1. [X] Scraping of policy documents information (NOT the actual documents).
2. [X] Extract keywords and keyphrases from PDF Docs and any type of meaningful information that differentiates these documents.
3. [ ] (_In progress_) Apply keywords and keyphrases to the policy document information dataset, to cut down from 12k+ to around 1k-2k.
4. [ ] (_In progress_) At the same time, tag a random subset of documents as relevant/non-relevant based on policy information. 
5. [ ] Scraping of full policy documents from the narrowed down filter in steps 3. and 4. (_or more?_ - second scraping phase)
6. [ ] Second round of relevant/non-relevant tagging process for the full policy documents.
7. [ ] Create a model for classifying relevant/non-relevant documents using abstracts from documents only
8. [ ] Create a model for classifying relevant/non-relevant documents using the full text of documents

### Phase 2: Classifying relevant documents using multiple tags
1. [ ] Scraping full policy documents from list of relevant policy information 
2. [ ] Tagging the scraped full documents according to the different types of incentives/disincentives/etc. 
3. [ ] Create a multi-class classification model for the labeled data above

-------------------------------------

World Resource Institute
==============================
# Background and Motivation

We are on the verge of the United Nations Decade for Ecosystem Restoration. The Decade starts in 2021 and ushers in a global effort to drive ecosystem restoration to support climate mitigation and adaptation, water and food security, biodiversity conservation and livelihood development. In order to prepare for the decade, we must understand the enabling environment. However, to understand policies involves reading and analyzing thousands of pages of documentation across multiple sectors. Using NLP to mine policy documents, would promote knowledge sharing between stakeholders and enable rapid identification of incentives, disincentives, perverse incentives and misalignment between policies. If a lack of incentives or disincentives were discovered, this would provide an opportunity to advocate for positive change. Creating a systematic analysis tool using NLP would enable a standardized approach to generate data that can support evidence-based change.

# Project Description

The viability of Nature Based Solutions projects is often impeded by the lack of positive incentives to adopt practices that conserve or restore land. Perverse incentives also encourage business-as-usual practices that have a heavy carbon footprint, degrade ecosystems, exploit workers or fail to generate decent livelihoods for rural communities.

Shifting incentives in a specific jurisdiction begins with a diagnosis of the country’s existing regulations, incentives and mandates across agencies. The aim is to gain a thorough understanding of current regulations and incentives that are relevant to forest and landscape restoration, the reality of how they are applied in practice and the degree of alignment or conflict across ministries and different levels of government. Shifting incentives at international level, may require such diagnostics across multiple countries, or voluntary standards and business practices. For this purpose, natural language processing technologies are needed to expedite systematic review of the legal and policy context in the relevant jurisdictions, as well as examples of innovative incentives from other contexts.

The initial focus is in Latin America, therefore native or fluent Spanish speakers are required to lead the project. If volunteers are interested in other country contexts, please contact us and we will assess data availability, but Latin America is a priority focus in the first instance.

# Intended Impact

Success will be achieved as governments or market platforms create aligned incentives across sectoral silos, remove administrative bottlenecks, or reorient incentives in line with recommendations. To advocate for change, a systematic process of analyzing incentives is needed beyond manual policy analysis. Currently manual policy analysis is the only method utilized to understand incentives. This is inadequate when considering the scale of the task.

# Internal Stakeholders

Global Restoration Initiative and Forest teams. Supporting the work of the Policy Accelerator

# Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── tasks              <- Top level folder for all tasks and code
    │   ├── task_name        <- Folder to contain materials for one single task
    │       ├── src              <- Source code for use in this task.
    │       ├── input            <- Input files for this task ONLY (otherwise use the data/ folder by default)
    │       ├── output           <- Output files from the task
    │       ├── notebooks        <- Place to store jupyter notebooks/R markdowns or any prototyping files (the drafts)
    │       ├── README.md        <- Basic instructions on how to replicate the results from the output/run the code in src
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt` (we will probably need to change this to include R information in the future)
--------

Project structure based on the [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/) and the [task as a quantum of workflow project template](https://hrdag.org/2016/06/14/the-task-is-a-quantum-of-workflow/). 

