# The Policy Accelerator

This project contains the code for the paper *Accelerating Incentives: Identifying economic and financial incentives for forest and landscape restoration in Latin American policy using Machine Learning*, accepted at [ICCP5](https://www.ippapublicpolicy.org/conference/icpp5/13). 

In the long term, we are building a tool that can be extended to any use case related to policy analysis. More information on the architecture and implementation below.

# Table of contents
- [About](#about)
- [Architecture](#architecture)
  - [General Pipeline](#general-pipeline)
  - [Human-in-the-loop Annotation Pipeline](#human-in-the-loop-annotation-pipeline)
  - [Classifier Pipeline](#classifier-pipeline)
- [Results](#results)
  - [Incentive Detection](#incentive-detection)
  - [Incentive Instrument Classification](#incentive-instrument-classification)
- [Development](#development)
  - [Getting Started](#getting-started)
  - [Main Components](#main-components)
  - [Contribution Guidelines](#contribution-guidelines)
  - [Project Organization](#project-organization)
- [Background, Motivation and Impact](#background-motivation-and-impact)

## About
[DSSG Solve](https://github.com/wri-dssg/policy-data-analyzer/blob/i77_edit_readme/images/MulticlassClassificationResults.png) and [Omdena](https://omdena.com/) are collaborating with the [World Resources Institute](https://www.wri.org/) to create a tool that can assist policy analysts in understanding regulations and incentives relating to forest and landscape restoration, how these policies are applied in practice, and the degree of alignment across ministries and levels of government.

So far, we have successfully built an end-to-end pipeline containing a model that can identify financial and economic incentives in policy documents from 5 Latin American countries: Chile, El Salvador, Guatemala, Mexico, and Peru. We presented our project to government officials from these countries and have received support and input from stakeholders in El Salvador and Chile. Going forward, we will receive additional input from stakeholders in other countries, including Mexico and India.  

The modeling side has yielded promising results, and we will be presenting this progress at the [5th Conference on International Public Policy](https://www.ippapublicpolicy.org/conference/icpp5/13). The potential impact of this framework is quite large, as it can be extended to multiple countries and to different types of policy analysis. Very little has been done to apply ML to restoration, so this project is a great opportunity to pioneer a new application of data science to environmental efforts. More information in the [Background, Motivation and Impact section](#background-motivation-and-impact).

## Architecture

### General Pipeline 
<img src="https://github.com/wri-dssg/policy-data-analyzer/blob/master/images/GeneralPipeline.png" width="80%">

### Human-in-the-loop Annotation Pipeline
<img src="https://github.com/wri-dssg/policy-data-analyzer/blob/master/images/HITLPipeline.png" width="40%">

### Classifier Pipeline
<img src="https://github.com/wri-dssg/policy-data-analyzer/blob/master/images/ClassifierPipeline.png" width="50%">

## Results
### Incentive Detection
<img src="https://github.com/wri-dssg/policy-data-analyzer/blob/master/images/BinaryClassificationResults.png" width="60%">

### Incentive Instrument Classification
<img src="https://github.com/wri-dssg/policy-data-analyzer/blob/master/images/MulticlassClassificationResults.png" width="55%">

## Development

### Getting Started

**Requirements**

- Python >= 3.6
- Miniconda or `virtualenv` (or any type of virtual environment tool)
- pip

### Contribution Guidelines

#### Steps to contribute to the master branch

*On Github*

1. Create an issue for each new bug/feature/update that you want to contribute. In the issue description, be as detailed as possible with what the expected inputs and outputs should be, and if possible what the process to solve the issue will be. 
2. Assign someone, as well as apply the respective tags (documentation, enhacement, etc.)

*On your local machine*

3. If you haven't already, accept the invite to be a member of wri-dssg! Then clone the repository using `git clone https://github.com/wri-dssg/policy-data-collector.git`
4. If you're going to work on issue #69 which is about extracting text, then create a branch for that issue: 
  ```
  git checkout -b i69_text_extraction
  ``` 
5. Once work is done, commit and push:
  ```
  git push --set-upstream origin i69_text_extraction
  ```

*Back on Github*

6. Once issue is solved, make a Pull Request (PR) on Github to merge to the master branch, and link the issue in the PR description and assign people to review. If possible, do one PR once a week to avoid merge conflicts. 
7. If the PR gets approved and merged, you can close the issue and delete the branch! 

#### Docker, reproducibility and development

 - The project's Dockerfile can be used to set up a development environment which encapsulates all dependencies necessary to run each project component. The purpose of this environment is to facilitate collaboration and reproducibility, while being able to develop and work on the project locally.
 - Future dependencies should be added either to the Dockerfile or the requirements.txt with a comment on the purpose of the specific package.

*Build the Docker image:*

    $ docker build -f Dockerfile -t policy_container . 
    
*Create a Docker container by running the image:*

    $ docker run -ti --rm -p 8888:8888 --mount source=$(pwd),target=/app,type=bind policy_container:latest  
    # $(pwd) should give you the absolute path to the project directory
    
*Launch a jupyter notebook from within the container*

    $ jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root

#### FAQs

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
    
## Project Organization

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


Project structure based on the [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/) and the [task as a quantum of workflow project template](https://hrdag.org/2016/06/14/the-task-is-a-quantum-of-workflow/). 


-------------------------------------
## Background, Motivation and Impact

We are on the verge of the United Nations Decade for Ecosystem Restoration. The Decade starts in 2021 and ushers in a global effort to drive ecosystem restoration to support climate mitigation and adaptation, water and food security, biodiversity conservation and livelihood development. In order to prepare for the decade, we must understand the enabling environment. However, to understand policies involves reading and analyzing thousands of pages of documentation across multiple sectors. Using NLP to mine policy documents, would promote knowledge sharing between stakeholders and enable rapid identification of incentives, disincentives, perverse incentives and misalignment between policies. If a lack of incentives or disincentives were discovered, this would provide an opportunity to advocate for positive change. Creating a systematic analysis tool using NLP would enable a standardized approach to generate data that can support evidence-based change.

The viability of Nature Based Solutions projects is often impeded by the lack of positive incentives to adopt practices that conserve or restore land. Perverse incentives also encourage business-as-usual practices that have a heavy carbon footprint, degrade ecosystems, exploit workers or fail to generate decent livelihoods for rural communities.

Shifting incentives in a specific jurisdiction begins with a diagnosis of the country’s existing regulations, incentives and mandates across agencies. The aim is to gain a thorough understanding of current regulations and incentives that are relevant to forest and landscape restoration, the reality of how they are applied in practice and the degree of alignment or conflict across ministries and different levels of government. Shifting incentives at international level, may require such diagnostics across multiple countries, or voluntary standards and business practices. For this purpose, natural language processing technologies are needed to expedite systematic review of the legal and policy context in the relevant jurisdictions, as well as examples of innovative incentives from other contexts.

Success will be achieved as governments or market platforms create aligned incentives across sectoral silos, remove administrative bottlenecks, or reorient incentives in line with recommendations. To advocate for change, a systematic process of analyzing incentives is needed beyond manual policy analysis. Currently manual policy analysis is the only method utilized to understand incentives. This is inadequate when considering the scale of the task.

_Description taken from: [DSSG Solve Project Description](https://www.solveforgood.org/proj/46/)_



