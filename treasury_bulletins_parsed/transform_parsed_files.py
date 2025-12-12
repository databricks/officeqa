"""
Convert JSON files to Markdown with multi-line tables.

Note that these transformed files are already provided 
in the treasury_bulletins_parsed/transformed directory.
This script is provided for convenience in case you wish to 
modify the ways in which files are transformed for agent 
consumption from the parsed documents.

Input: treasury_bulletins_parsed/*.json
Output: treasury_bulletins_markdown/*.txt

Behavior:
- Non-table elements are written as plain text with original newlines.
- Table elements are converted to standard Markdown tables (separate lines).
- Nested/multi-row headers are flattened with " > " separator.

Usage:
    python transform_parsed_files.py
    python transform_parsed_files.py --file treasury_bulletin_1939_01.json
"""

import argparse
import io
import json
import os
import re
from typing import Any, List
import pandas as pd


# =============================================================================
# Utility functions
# =============================================================================

def get_data_root() -> str:
    """Return the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))


def get_input_output_dirs() -> tuple[str, str]:
    """Return input and output directories."""
    data_root = get_data_root()
    input_dir = os.path.join(data_root, "treasury_bulletins_parsed")
    output_dir = os.path.join(data_root, "treasury_bulletins_markdown")
    return input_dir, output_dir


def load_json_file(src_path: str) -> dict:
    """Load a JSON file and return the parsed object."""
    with open(src_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_elements(obj: dict) -> List[dict]:
    """Extract elements list from a parsed JSON document."""
    doc = obj.get("document") or {}
    elements = doc.get("elements")
    return elements if isinstance(elements, list) else []


def is_table_content(s: str) -> bool:
    """Check if content contains an HTML table."""
    return "<table" in s.lower()


def flatten_columns_to_paths(columns) -> List[str]:
    """Return a list of header names, flattening MultiIndex using ' > ' between levels."""
    if isinstance(columns, pd.MultiIndex):
        names: List[str] = []
        for tup in columns:
            parts = [str(x).strip() for x in tup if x is not None and str(x).strip() != ""]
            names.append(" > ".join(parts) if parts else "")
        return names
    # Simple index
    return [str(c).strip() for c in list(columns)]


def sanitize_md_cell(v: Any) -> str:
    """Clean a cell value for Markdown table output."""
    s = "" if v is None else str(v)
    s = s.replace("\n", " ")
    s = s.replace("|", "\\|")
    return s.strip()


def write_markdown(dst_path: str, lines: List[str]) -> None:
    """Write lines to a Markdown/text file."""
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as w:
        for line in lines:
            w.write(line)
            w.write("\n")


# =============================================================================
# Main conversion logic
# =============================================================================

def dataframe_to_markdown(df) -> str:
    """Convert DataFrame to multi-line Markdown table."""
    headers = flatten_columns_to_paths(df.columns)
    # Ensure unique non-empty headers
    seen = {}
    for i, h in enumerate(headers):
        name = h if h else f"col_{i+1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        headers[i] = name

    # Build rows
    rows: List[List[str]] = []
    for _, row in df.iterrows():
        rows.append([sanitize_md_cell(row.get(col)) for col in df.columns])

    # Markdown table with real newlines
    line_header = "| " + " | ".join(sanitize_md_cell(h) for h in headers) + " |"
    line_sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([line_header, line_sep] + body_lines)


def parse_tables_to_markdown(html_str: str) -> List[str]:
    """Parse HTML tables and convert to Markdown format."""
    try:
        dfs = pd.read_html(io.StringIO(html_str))
    except Exception:
        return ["```html\n" + html_str.strip() + "\n```"]
    
    md_tables: List[str] = []
    for df in dfs:
        md_tables.append(dataframe_to_markdown(df))
    return md_tables


def process_file(src_path: str) -> List[str]:
    """Process a single JSON file and return Markdown lines."""
    out_lines: List[str] = []
    try:
        obj = load_json_file(src_path)
    except Exception as e:
        print(f"Error loading {src_path}: {e}")
        return out_lines
    
    for el in extract_elements(obj):
        content = el.get("content") if isinstance(el, dict) else None
        if not isinstance(content, str) or not content.strip():
            continue
        if is_table_content(content):
            tables_md = parse_tables_to_markdown(content)
            for t in tables_md:
                out_lines.append(t)
                out_lines.append("")
        else:
            text = content.strip()
            text = re.sub(r"\r\n?", "\n", text)
            for line in text.split("\n"):
                out_lines.append(line)
            out_lines.append("")
    return out_lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert JSON files to Markdown (multi-line tables).")
    parser.add_argument("--file", type=str, help="Process a single JSON file")
    args = parser.parse_args()

    input_dir, output_dir = get_input_output_dirs()

    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    if args.file:
        entries = [args.file]
        print(f"Processing single file: {args.file}")
    else:
        entries = [fn for fn in os.listdir(input_dir) if fn.startswith("treasury_bulletin_") and fn.endswith(".json")]
        entries.sort()

    total_files = 0
    for fn in entries:
        src_path = os.path.join(input_dir, fn)
        if not os.path.exists(src_path):
            print(f"Warning: File not found: {src_path}")
            continue
        base, _ = os.path.splitext(fn)
        dst_path = os.path.join(output_dir, base + ".txt")
        lines = process_file(src_path)
        write_markdown(dst_path, lines)
        total_files += 1
        print(f"Wrote {dst_path} ({len(lines)} lines)")

    print(f"\nCompleted: {total_files} files written to {output_dir}")


if __name__ == "__main__":
    main()