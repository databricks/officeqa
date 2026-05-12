# Corpus Scripts

Scripts and notebooks for working with the Treasury Bulletin corpus.

The corpus (PDFs, parsed JSONs, and transformed text files) lives on
[Hugging Face](https://huggingface.co/datasets/databricks/officeqa) — you must download it
before running any of these scripts. The dataset is gated; request access on Hugging Face first.

## Step 1: Download the corpus

```python
from huggingface_hub import snapshot_download

# Download everything (~5GB total)
local_dir = snapshot_download(
    repo_id="databricks/officeqa",
    repo_type="dataset",
    local_dir="~/officeqa-corpus",
)

# Or download only what you need:

# Transformed text — recommended for LLM/RAG workflows (~460MB)
local_dir = snapshot_download(
    repo_id="databricks/officeqa",
    repo_type="dataset",
    allow_patterns="treasury_bulletins_parsed/transformed/*.txt",
    local_dir="~/officeqa-corpus",
)

# Parsed JSONs — full structure with bounding boxes, tables, metadata (~730MB)
local_dir = snapshot_download(
    repo_id="databricks/officeqa",
    repo_type="dataset",
    allow_patterns="treasury_bulletins_parsed/jsons/*.json",
    local_dir="~/officeqa-corpus",
)

# Original PDFs (~4GB)
local_dir = snapshot_download(
    repo_id="databricks/officeqa",
    repo_type="dataset",
    allow_patterns="treasury_bulletin_pdfs/*",
    local_dir="~/officeqa-corpus",
)
```

## Scripts

### `transform_scripts/transform_parsed_files.py`

Converts parsed JSON files to agent-friendly Markdown text (tables converted to Markdown format).
Requires the parsed JSONs to be downloaded first.

```bash
python transform_scripts/transform_parsed_files.py --data-dir ~/officeqa-corpus

# Process a single file
python transform_scripts/transform_parsed_files.py --data-dir ~/officeqa-corpus --file treasury_bulletin_1939_01.json
```

Output: `<data-dir>/treasury_bulletins_parsed/transformed/*.txt`

### `transform_scripts/transform_files_page_level.py`

Same as above but adds `--- PAGE N ---` markers between pages. Also supports splitting output
into one file per page with `--split-files`.

```bash
python transform_scripts/transform_files_page_level.py --data-dir ~/officeqa-corpus

# Split into one file per page
python transform_scripts/transform_files_page_level.py --data-dir ~/officeqa-corpus --split-files
```

Output: `<data-dir>/treasury_bulletins_parsed/transformed_page_level/*.txt`

### `render-officeqa-json.ipynb`

Visualizes a parsed JSON document alongside the original PDF, with bounding boxes overlaid.
Requires both the parsed JSONs and original PDFs to be downloaded.

Update the paths in the notebook before running:
```python
path_to_json = "~/officeqa-corpus/treasury_bulletins_parsed/jsons/treasury_bulletin_1980_01.json"
path_to_pdf  = "~/officeqa-corpus/treasury_bulletin_pdfs/treasury_bulletin_1980_01.pdf"
```

### `ocr_removal.ipynb`

Converts OCR PDFs to image-only (no-OCR) PDFs by rendering each page as a JPEG.
Requires the original PDFs to be downloaded.

```
Input:  <data-dir>/treasury_bulletin_pdfs/
Output: <data-dir>/treasury_bulletin_pdfs_no_ocr/
```
