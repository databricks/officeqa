<div align="center">
  <h1>OfficeQA</h1>
  <p>A Grounded Reasoning Benchmark by Databricks</p>
</div>
<p align="center"><img width="300" src="logo.png"/></p>

**OfficeQA** is a benchmark by Databricks, built for evaluating model / agent performance on end to end **Grounded Reasoning** tasks.

Additional details:
* Questions require the **[U.S Treasury Bulletin](https://fraser.stlouisfed.org/title/treasury-bulletin-407?browse=1930s)** documents to answer
* OfficeQA contains 246 questions & corresponding ground truth answers.
* Datasets released under **CC-BY-SA 4.0** and code and scripts under **Apache 2.0 License**.

## Overview

OfficeQA evaluates how well AI systems can reason over real-world documents to answer complex questions. The benchmark uses historical U.S. Treasury Bulletin PDFs (1939-2025), which contain dense financial tables, charts, and text data.

**Repository Contents:**
- `officeqa.csv` - The benchmark dataset with 246 questions
- `treasury_bulletin_pdfs/` - Source PDF documents (696 files)
- `treasury_bulletins_parsed/` - Parsed version of the treasury bulletin PDFs.
- `treasury_bulletins_parsed_transformed/` - Transformed version of the parsed treasury bulletins. Transformations made, like stripping bounding box information and changing html tables to markdown, were in order to make docs more 'legible' by agents.
- `reward.py` - Evaluation script for scoring model outputs

**Dataset Schema (`officeqa.csv`):**
| Column | Description |
|--------|-------------|
| `uid` | Unique question identifier |
| `question` | The question to answer |
| `answer` | Ground truth answer |
| `source_docs` | Document(s) required to answer the question |
| `difficulty` | `easy` or `hard` |

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/databricks/officeqa.git
cd officeqa
```
NOTE: This may take a long time due to the large amount of PDF documents in `treasury_bulletin_pdfs`.

### 2. Load the dataset
```python
import pandas as pd

df = pd.read_csv('officeqa.csv')
print(f"Total questions: {len(df)}")
print(f"Easy: {len(df[df['difficulty'] == 'easy'])}")
print(f"Hard: {len(df[df['difficulty'] == 'hard'])}")
```

### 3. Choose your corpus
There are a few different forms of the Treasury Bulletin corpus that are available for you to use:
1. 
We've provided both the original PDFs, a parsed version of the treasury bulletins, and a 

# TODO: flesh out

### 4. Evaluate your model outputs
```python
from reward import officeqa_reward

# Score a single prediction
score = officeqa_reward(
    ground_truth="123.45",
    prediction="123.45",
    tolerance=0.01  # 1% tolerance for numerical answers
)
print(f"Score: {score}")  # 1.0 for correct, 0.0 for incorrect
```

## Evaluation

The `reward.py` script provides fuzzy matching for numerical answers with configurable tolerance levels:
- `0.0%` - Exact match
- `0.1%` - Within 0.1% relative error
- `1.0%` - Within 1% relative error
- `5.0%` - Within 5% relative error
etc.