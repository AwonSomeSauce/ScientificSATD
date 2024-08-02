# Replication Package for SATD Analysis in Scientific Software

This replication package contains all the necessary scripts, data, and instructions to replicate the study on Self-Admitted Technical Debt (SATD) in scientific software. The study analyzes SATD across various scientific domains and utilizes Large Language Models (LLMs) to identify cross-domain knowledge for Scientific Debt management.

## Overview

This repository includes:

1. Scripts to clone target repositories and extract code comments.
2. Tools to identify potential SATD comments.
3. Analysis scripts and Jupyter Notebooks.
4. Scripts for LLM predictions on closed issues.

## Requirements

-   Python 3.x
-   Git
-   Required Python libraries: `pandas`, `numpy`, `openai`, `tqdm`, `scipy`

## Steps to Replicate the Study

### Step 1: Clone Target Repositories

First, clone all the target repositories to your local machine. You can use the following command:

```bash
git clone <repository-url>
```

Ensure that you clone all the required repositories for the study.

### Step 2: Extract Comments

Run the `extract_git_log.py` script to extract comments from `.py`, `.cpp`, and `.F90` files. This script will save the extracted comments into a CSV file named `all_projects_comments.csv` in the root directory of this repository.

```bash
python extract_git_log.py
```

### Step 3: Identify Potential SATD Comments

Run the `identify_satd.py` script to filter potential SATD comments based on keywords provided by Potdar et al. \cite{Potdar2014} and Sridharan et al. \cite{Sridharan2023PENTACETD}. The keywords are listed in the `satd_features.txt` file.

```bash
python identify_satd.py
```

### Step 4: Manual Elimination of Non-SATD Comments

Manually eliminate non-SATD comments from the filtered dataset.

### Step 5: Manual Categorization and Labeling

Manually categorize all comments, assign them appropriate categories, and identify indicators for all Scientific Debt categories. Store these labeled comments in `ssw_satd.csv`.

### Step 6: Analysis

Perform the analysis using `analysis.ipynb`, which utilizes the data stored in `ssw_satd.csv`.

```bash
jupyter notebook analysis.ipynb
```

### Step 7: Extract Closed Issues

Extract closed issues from `ESCOMP/CTSM` using `extract_closed_issues.py`.

```bash
python extract_closed_issues.py
```

### Step 8: Send Batch Requests to GPT-4

Send a batch request to GPT-4 using `send_gpt_request.py`.

```bash
python send_gpt_request.py
```

### Step 9: Collect and Check Results

After the batch process is completed, collect and check the results using `analyze_gpt_predictions.py`.

```bash
python analyze_gpt_predictions.py
```

## Data Description

-   **ssw_satd.csv**: Contains all labelled SATD comments from the target repositories.
-   **satd_features.txt**: List of keywords used to identify potential SATD comments.

## Contact

For any questions or issues, please contact Ahmed Musa Awon at ahmedmusa@uvic.ca.

---

This README provides a comprehensive guide to replicating our study on SATD in scientific software. Follow the steps carefully to ensure accurate replication of our methodology and results.
