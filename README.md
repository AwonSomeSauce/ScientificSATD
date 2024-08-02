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

After filtering potential SATD comments, manually review the dataset to eliminate non-SATD comments. This step ensures the accuracy of the SATD identification process.

### Step 5: Analysis

Analyze the refined dataset using the `analysis.ipynb` Jupyter Notebook. This notebook contains all the analysis steps and visualizations used in the study.

```bash
jupyter notebook analysis.ipynb
```

### Step 6: Extract Closed Issues

For LLM predictions, extract closed issues from the `ESCOMP/CTSM` repository using the `extract_closed_issues.py` script.

```bash
python extract_closed_issues.py
```

### Step 7: Send Batch Requests to GPT-4

Send a batch request to GPT-4 using the `send_gpt_request.py` script. This script processes the issues and sends them to the GPT-4 API for predictions.

```bash
python send_gpt_request.py
```

### Step 8: Analyze GPT-4 Predictions

After the batch process is completed, analyze the results using the `analyze_gpt_predictions.py` script.

```bash
python analyze_gpt_predictions.py
```

## Zenodo DOI

The labelled dataset associated with this study can be accessed at [Zenodo](https://doi.org/10.5281/zenodo.13174322).

## Contact

For any questions or issues, please contact Ahmed Musa Awon at ahmedmusa@uvic.ca.

---

This README provides a comprehensive guide to replicating our study on SATD in scientific software. Follow the steps carefully to ensure accurate replication of our methodology and results.
