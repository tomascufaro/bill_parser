import json
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from src.parser import BillParser
from src.extractor import BillExtractor
from src.csv_exporter import export_to_csv

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Bill Parser Pipeline")
    parser.add_argument("--limit", type=int, default=0, help="Limit files to process")
    args = parser.parse_args()

    # Paths
    base_dir = Path(__file__).parent
    raw_dir = base_dir / "data/raw/sample"
    # We still use this to store intermediate MD/JSON for debugging/cache
    # but the pipeline runs start-to-finish.
    docling_output_dir = base_dir / "data/processed/docling_output"
    final_output_dir = base_dir / "data/processed/structured_output"
    database_csv = base_dir / "data/processed/database.csv"
    model_csv = base_dir / "data/raw/data_model.csv"
    
    for d in [docling_output_dir, final_output_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Init
    print("Initializing components...")
    bill_parser = BillParser()
    try:
        extractor = BillExtractor()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    # Select Input Files (Always from Raw)
    input_files = list(raw_dir.glob("*.jpg"))

    if not input_files:
        print("No input files found in data/raw/sample/")
        return

    # Apply Limit
    if args.limit > 0:
        input_files = input_files[:args.limit]
        print(f"Limit applied: Processing first {args.limit} files.")
    else:
        print(f"Found {len(input_files)} files to process.")

    # Process Loop
    for i, file_path in enumerate(input_files, 1):
        print(f"[{i}/{len(input_files)}] Processing {file_path.name}...")
        
        try:
            source_filename = file_path.name
            
            # 1. Docling (Image -> Markdown)
            print(f"  -> Running Docling parser...")
            result = bill_parser.convert_image(file_path)
            markdown_content = bill_parser.export_markdown(result)
            
            # Save intermediate MD (useful for debugging)
            md_path = docling_output_dir / f"{file_path.stem}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            # 2. Extract Data (Markdown -> Structured)
            print(f"  -> Extracting structured data...")
            bill = extractor.extract_data_from_markdown(markdown_content)
            bill.source_filename = source_filename
            
            # 3. Save Final Result
            out_path = final_output_dir / f"{file_path.stem}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(bill.model_dump_json(indent=2))
            
            print(f"  -> Saved to {out_path}")

        except Exception as e:
            print(f"  ERROR processing {file_path.name}: {str(e)}")

    # 4. Export to CSV
    print("\nExporting to CSV database...")
    export_to_csv(final_output_dir, database_csv, model_csv)
    
    print("\nPipeline execution completed.")

if __name__ == "__main__":
    main()
