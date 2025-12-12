#!/usr/bin/env python3
"""
Unzip all zip files in the treasury_bulletins_parsed directory.

Creates the following structure:
  treasury_bulletins_parsed/
  ├── jsons/           <- files from treasury_bulletins_parsed_part*.zip
  └── transformed/     <- files from treasury_bulletins_transformed.zip
"""

import os
import zipfile
from pathlib import Path


def unzip_all():
    # Get the directory where this script lives
    script_dir = Path(__file__).parent.resolve()
    
    # Define output directories
    jsons_dir = script_dir / "jsons"
    transformed_dir = script_dir / "transformed"
    
    # Create output directories
    jsons_dir.mkdir(exist_ok=True)
    transformed_dir.mkdir(exist_ok=True)
    
    # Find all zip files (in root and subdirectories)
    zip_files = sorted(script_dir.glob("**/*.zip"))
    
    if not zip_files:
        print("No zip files found in", script_dir)
        return
    
    print(f"Found {len(zip_files)} zip file(s)")
    
    for zip_path in zip_files:
        zip_name = zip_path.name
        
        # Extract to same directory as the zip file
        output_dir = zip_path.parent
        
        print(f"\nExtracting: {zip_name} -> {output_dir.name}/")
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                # Skip directories
                if member.endswith('/'):
                    continue
                
                # Get just the filename (ignore any path in the zip)
                filename = os.path.basename(member)
                if not filename:
                    continue
                
                # Skip macOS metadata files
                if filename.startswith('._') or filename == '.DS_Store':
                    continue
                
                target_path = output_dir / filename
                
                # Extract file
                with zf.open(member) as src:
                    target_path.write_bytes(src.read())
                
                print(f"  {filename}")
    
    # Count extracted files (excluding zip files)
    jsons_count = len([f for f in jsons_dir.glob("*") if f.suffix != ".zip"]) if jsons_dir.exists() else 0
    transformed_count = len([f for f in transformed_dir.glob("*") if f.suffix != ".zip"]) if transformed_dir.exists() else 0
    
    print(f"\n✓ Done!")
    print(f"  jsons/: {jsons_count} files")
    print(f"  transformed/: {transformed_count} files")


if __name__ == "__main__":
    unzip_all()

