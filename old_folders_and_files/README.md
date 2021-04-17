Old READMEs
------------------------------------------
Previous Roadmap
==============================
### Resources

- [Data](https://drive.google.com/drive/folders/1tFn-6cKpIFZgGr7qELXAGXpjUU97k3NZ)
- [Trello](https://trello.com/b/0eZuJyZL/wrilatam)

### Phase 1: Augmenting training data

1. [X] Fine-tune S-BERT on existing labeled data from 5 countries (`WRI_Policy_Tags.xlsx` file)
2. [X] Find methods to improve performance of S-BERT for data augmentation purposes
3. [X] Build pipeline for further fine tuning as we get more data
4. [X] Classify the policy instrument of new sentences from El Salvador and Chile policy documents 
5. [X] Manually review the model tags and tag more examples (2 reviewers)
6. [X] Build pipeline to create excel documents for manual reviewing/tagging
7. [X] Explore other models if needed

### Phase 2: Modeling

1. [X] Develop a model to first identify whether a sentence contains an incentive instrument, or is an icentive at all
2. [X] Develop a model that classifies incentive instruments (direct payment, tax deduction, etc.)
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
