#!/usr/bin/env python3
"""
Zip all JSON/TXT/JSONL files in the treasury_bulletins_parsed directory.

Creates the following structure:
  treasury_bulletins_parsed/
  ├── jsons/
  │   ├── treasury_bulletins_parsed_part001.zip
  │   ├── treasury_bulletins_parsed_part002.zip
  │   └── treasury_bulletins_parsed_part003.zip
  └── transformed/
      └── treasury_bulletins_transformed.zip

Usage:
    python zip.py
    python zip.py --delete-originals  # Delete source files after zipping
"""

import argparse
import os
import zipfile
from pathlib import Path


def get_script_dir() -> Path:
    """Return the directory containing this script."""
    return Path(__file__).parent.resolve()


def collect_files(directory: Path, extensions: tuple[str, ...]) -> list[Path]:
    """Collect all files with given extensions in a directory."""
    files = []
    for ext in extensions:
        files.extend(directory.glob(f"*{ext}"))
    return sorted(files)


def split_into_parts(files: list[Path], num_parts: int) -> list[list[Path]]:
    """Split a list of files into roughly equal parts."""
    if not files:
        return [[] for _ in range(num_parts)]
    
    part_size = len(files) // num_parts
    remainder = len(files) % num_parts
    
    parts = []
    start = 0
    for i in range(num_parts):
        # Distribute remainder across first few parts
        end = start + part_size + (1 if i < remainder else 0)
        parts.append(files[start:end])
        start = end
    
    return parts


def create_zip(zip_path: Path, files: list[Path], delete_originals: bool = False) -> int:
    """Create a zip file containing the given files. Returns number of files added."""
    if not files:
        print(f"  No files to zip for {zip_path.name}")
        return 0
    
    # Remove existing zip if present
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            # Store just the filename in the zip (no directory structure)
            zf.write(file_path, file_path.name)
    
    if delete_originals:
        for file_path in files:
            file_path.unlink()
    
    return len(files)


def zip_jsons(script_dir: Path, delete_originals: bool = False) -> None:
    """Zip JSON files in jsons/ into 3 parts."""
    jsons_dir = script_dir / "jsons"
    
    if not jsons_dir.exists():
        print(f"Directory not found: {jsons_dir}")
        return
    
    # Collect JSON and JSONL files
    json_files = collect_files(jsons_dir, (".json", ".jsonl"))
    
    if not json_files:
        print("No JSON/JSONL files found in jsons/")
        return
    
    print(f"\nFound {len(json_files)} JSON/JSONL files in jsons/")
    
    # Split into 3 parts
    parts = split_into_parts(json_files, 3)
    
    for i, part_files in enumerate(parts, 1):
        zip_name = f"treasury_bulletins_parsed_part{i:03d}.zip"
        zip_path = jsons_dir / zip_name
        
        count = create_zip(zip_path, part_files, delete_originals)
        size_mb = zip_path.stat().st_size / (1024 * 1024) if zip_path.exists() else 0
        print(f"  Created {zip_name}: {count} files ({size_mb:.1f} MB)")


def zip_transformed(script_dir: Path, delete_originals: bool = False) -> None:
    """Zip TXT/JSONL files in transformed/ into a single zip."""
    transformed_dir = script_dir / "transformed"
    
    if not transformed_dir.exists():
        print(f"Directory not found: {transformed_dir}")
        return
    
    # Collect TXT and JSONL files
    txt_files = collect_files(transformed_dir, (".txt", ".jsonl"))
    
    if not txt_files:
        print("No TXT/JSONL files found in transformed/")
        return
    
    print(f"\nFound {len(txt_files)} TXT/JSONL files in transformed/")
    
    zip_name = "treasury_bulletins_transformed.zip"
    zip_path = transformed_dir / zip_name
    
    count = create_zip(zip_path, txt_files, delete_originals)
    size_mb = zip_path.stat().st_size / (1024 * 1024) if zip_path.exists() else 0
    print(f"  Created {zip_name}: {count} files ({size_mb:.1f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Zip JSON and TXT files in treasury_bulletins_parsed directory."
    )
    parser.add_argument(
        "--delete-originals",
        action="store_true",
        help="Delete original files after zipping"
    )
    args = parser.parse_args()
    
    script_dir = get_script_dir()
    print(f"Working directory: {script_dir}")
    
    # Zip JSON files into 3 parts
    zip_jsons(script_dir, args.delete_originals)
    
    # Zip transformed files into 1 zip
    zip_transformed(script_dir, args.delete_originals)
    
    print("\n✓ Done!")
    
    if args.delete_originals:
        print("  Original files have been deleted.")


if __name__ == "__main__":
    main()

