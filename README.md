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
- `reward.py` - Evaluation script for scoring model outputs
- `treasury_bulletin_pdfs/` - Original source PDF documents (696 files, ~20GB)
- `treasury_bulletins_parsed/` - Parsed and transformed versions (see more details below)

**Dataset Schema (`officeqa.csv`):**
| Column | Description |
|--------|-------------|
| `uid` | Unique question identifier |
| `question` | The question to answer |
| `answer` | Ground truth answer |
| `source_docs` | Original URL(s) from the Federal Reserve Archive |
| `source_files` | Corresponding parsed filename(s) (e.g., `treasury_bulletin_1941_01.txt`) |
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

We provide the Treasury Bulletin corpus in multiple formats:

#### Option A: Original PDFs (`treasury_bulletin_pdfs/`)
The raw PDF documents as downloaded from the Federal Reserve Archive. Use these if your system can process PDFs directly.
- **696 PDF files** covering 1939-2025
- Total size: ~20GB

#### Option B: Parsed Documents (`treasury_bulletins_parsed/`)
Pre-parsed versions of the PDFs. The files are distributed as zip archives to stay within Git file size limits.

**Structure:**
```
treasury_bulletins_parsed/
├── jsons/                    # Parsed JSON files with full structure
│   ├── treasury_bulletins_parsed_part001.zip
│   ├── treasury_bulletins_parsed_part002.zip
│   └── treasury_bulletins_parsed_part003.zip
├── transformed/              # Agent-friendly text format
│   └── treasury_bulletins_transformed.zip
├── unzip.py                  # Script to extract all files
└── transform_parsed_files.py # Script to transform JSON → text
```

**To extract the files:**
```bash
cd treasury_bulletins_parsed
python unzip.py
```

This will extract:
- `jsons/*.json` - Full parsed documents with bounding boxes, tables as HTML, and element metadata
- `transformed/*.txt` - Simplified text format with tables converted to Markdown (more readable for LLMs)

**Altenative data representations:**

The representation of the parsed documents can impact model performance. For reproducibility, we include the transformed data we used in our original experiments here, as well as the script to produce these files from the parsed files in `jsons/`, which can be found in `treasury_bulletins_parsed/transform_scripts/transform_parsed_files.py`.

New transformation scripts to adapt the raw parsed data can also be found and added to `treasury_bulletins_parsed/transform_scripts/`.

For example, a new file (`transform_files_page_level.py`) was recently added to add page level markers in the transformed parsed documents.
Data transformations can be run using:
```
cd treasury_bulletins_parsed/transform_scripts
python transform_parsed_files.py
```

#### Which format should I use?
| Format | Best for | Size |
|--------|----------|------|
| PDFs | Systems with native PDF support, or you want to parse from scratch | ~20GB |
| Parsed JSON | Full structural information, coordinates | ~600MB |
| Transformed TXT | LLM/agent consumption, cleaner text | ~200MB |

#### Mapping source URLs to parsed files

The `source_files` column in `officeqa.csv` provides the direct filenames (e.g., `treasury_bulletin_1941_01.txt`) for easy reference. If you need to understand the URL-to-filename conversion logic, here's how it works:

**URL format:** `https://fraser.stlouisfed.org/title/treasury-bulletin-407/{MONTH}-{YEAR}-{ID}?page={PAGE}`

**Filename format:** `treasury_bulletin_{YEAR}_{MONTH_NUM}.{ext}`

**Month name to number mapping:**
```
january   → 01    july      → 07
february  → 02    august    → 08
march     → 03    september → 09
april     → 04    october   → 10
may       → 05    november  → 11
june      → 06    december  → 12
```

**Example:**
- URL: `https://fraser.stlouisfed.org/title/treasury-bulletin-407/january-1941-6529`
- JSON file: `treasury_bulletins_parsed/jsons/treasury_bulletin_1941_01.json`
- Text file: `treasury_bulletins_parsed/transformed/treasury_bulletin_1941_01.txt`
- PDF file: `treasury_bulletin_pdfs/treasury_bulletin_1941_01.pdf`

### 4. Evaluate your model outputs
```python
from reward import score_answer

# Score a single prediction
score = score_answer(
    ground_truth="123.45",
    predicted="123.45",
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
