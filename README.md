Current Roadmap
==============================
### Resources

- [Data](https://drive.google.com/drive/folders/1tFn-6cKpIFZgGr7qELXAGXpjUU97k3NZ)
- [Trello](https://trello.com/b/0eZuJyZL/wrilatam)

### Phase 1: Augmenting training data

1. [ ] Fine-tune S-BERT on existing labeled data from 5 countries (`WRI_Policy_Tags.xlsx` file)
2. [ ] Find methods to improve performance of S-BERT for data augmentation purposes
3. [ ] Build pipeline for further fine tuning as we get more data
4. [ ] Classify the policy instrument of new sentences from El Salvador and Chile policy documents 
5. [ ] Manually review the model tags and tag more examples (2 reviewers)
6. [ ] Build pipeline to create excel documents for manual reviewing/tagging
7. [ ] Explore other models if needed

==============================
### Phase 2: Modeling

1. [ ] Develop a model to first identify whether a sentence contains an incentive instrument, or is an icentive at all
2. [ ] Develop a model that classifies incentive instruments (direct payment, tax deduction, etc.)



Contribution Guidelines
==============================
### Steps to contribute to the master branch

**On Github**
1. Let's say you want to work on extracting text! In the `Projects` tab on github, add a card in the TODO column and then click on the dropdown menu for the card and "Convert to issue"
2. In the issue description, be as detailed as possible with what the expected inputs and outputs should be, and if possible what the process to solve the issue will be. 
3. Assign someone! 

**On your local machine**
1. If you haven't already, accept the invite to be a member of wri-dssg! Then clone the repository using `git clone https://github.com/wri-dssg/policy-data-collector.git`
2. If you're going to work on issue #69 which is about extracting text, then create a branch for that issue (`git checkout -b issue_69_text_extraction` if the branch doesn't exist, else remove the `-b` flag). Let's see if that naming convention works but if not we can try something different!
3. Once work is done, commit and push

**Back on Github**

4. Once issue is solved, make a Pull Request (PR) on Github to merge to the master branch, and link the issue in the PR description and assign people to review. If possible, do one PR once a week to avoid merge conflicts. 
5. If the PR gets approved and merged, you can close the issue and delete the branch! The Github Projects page will be automatically updated

**To work on tasks**
1. So far the tasks will be defined by the Roadmap and you can follow the structure described in [Project Organization](#project-organization) or see existing structure of current tasks.

### Docker, reproducibility and development

 - The project's Dockerfile can be used to set up a development environment which encapsulates all dependencies necessary to run each project component. The purpose of this environment is to facilitate collaboration and reproducibility, while being able to develop and work on the project locally.
 - Future dependencies should be added either to the Dockerfile or the requirements.txt with a comment on the purpose of the specific package.

**Build the Docker image:**

    $ docker build -f Dockerfile -t policy_container . 
**Create a Docker container by running the image:**

    $ docker run -ti --rm -p 8888:8888 --mount source=$(pwd),target=/app,type=bind policy_container:latest  
    # $(pwd) should give you the absolute path to the project directory
**Launch a jupyter notebook from within the container**

    $ jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root

### FAQs
- _I want to create a new branch starting from an old branch, how do I do that?_
    - Say you want to create `branch_2` based on `branch_1` (in other words, with `branch_1` as a starting point), then you would:
    ```
    $ git checkout -b branch_2 branch_1    
    ```
- _I want to bring the changes from one branch into mine, to keep mine updated, how do I do that?_
    - Say you want to merge `branch_1` INTO `branch_2`, then you would:
    ```
    $ git checkout branch_2   # if you aren't in branch 2 already
    $ git merge branch_1
    ```
- _If I'm working with someone in the same issue, can I contribute/push to their branch?_
    - Technically yes, but it would be safer if you would work on yours first (maybe divide the issue in smaller issues) and then open a PR to theirs once you feel ready to merge code. Alternatively you could pair program and not worry about overwritting someone else's code :)
- _Can I push directly to master?_
    - Please don't :( 
    
# Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    |
    ├── src                <- Source code for use in this project. Code used across tasks.
    │
    ├── tasks              <- Top level folder for all tasks and code
    │   └── <task_name>        <- Folder to contain materials for one single task
    │       ├── src              <- Source code for use in this task.
    │       ├── input            <- Input files for this task
    │       ├── output           <- Output files from the task
    │       ├── notebooks        <- Place to store jupyter notebooks/R markdowns or any prototyping files (the drafts)
    │       └── README.md        <- Basic instructions on how to replicate the results from the output/run the code in src
    │
    └── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
                             generated with `pip freeze > requirements.txt` (we will probably need to change this to include R information in the future)
--------

Project structure based on the [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/) and the [task as a quantum of workflow project template](https://hrdag.org/2016/06/14/the-task-is-a-quantum-of-workflow/). 


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


------------------------------------------
Old Roadmap
==============================
### Phase 1: Classifying documents as relevant/non-relevant

**Current Data**
- PDF Docs (NOT from Ecolex) in [OneDrive link](https://onedrive.live.com/?authkey=%21APg%5FS4HvxM%5FJBBw&id=C675544AC4321F5C%21125&cid=C675544AC4321F5C) 
- Policy document information (around 12k+) from Ecolex, including `Title, Subjects, Keywords, Abstract` (NOT the actual documents, also in OneDrive link)
- 1000 abstracts from policy documents (plus other info such as subject, keywords, etc,) **labeled as relevant/non-relevant (column IS_INSTANCE in the document)** in [this table](https://onedrive.live.com/edit.aspx?resid=C675544AC4321F5C!1256&ithint=file%2cxlsx&authkey=!AE1-WJImJJpVyVs)

**Tasks** 
1. [X] Scraping of policy documents information (NOT the actual documents).
2. [X] Extract keywords and keyphrases from PDF Docs and any type of meaningful information that differentiates these documents.
3. [ ] (_On hold_) Apply keywords and keyphrases to the policy document information dataset, to cut down from 12k+ to around 1k-2k.
4. [X] At the same time, tag a random subset of documents as relevant/non-relevant based on policy information. 
5. [ ] Scraping of full policy documents from the narrowed down filter in steps 3. and 4. (_or more?_ - second scraping phase)
6. [ ] Second round of relevant/non-relevant tagging process for the full policy documents.
7. [ ] (_In progress_) Create a model for classifying relevant/non-relevant documents using abstracts from documents only
8. [ ] Create a model for classifying relevant/non-relevant documents using the full text of documents

### Phase 2: Classifying relevant documents using multiple tags
1. [ ] Scraping full policy documents from list of relevant policy information 
2. [ ] Tagging a sample of the scraped full documents according to the different types of incentives/disincentives/etc. 
3. [ ] Create a multi-class classification model for the labeled data above

