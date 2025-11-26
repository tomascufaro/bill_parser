import csv
import json
from pathlib import Path
from typing import List, Set
from src.models import Bill

def get_column_order(model_csv_path: Path) -> List[str]:
    """
    Reads the data model CSV and extracts the column order from the 'Field' column.
    
    Args:
        model_csv_path: Path to the data model CSV file
        
    Returns:
        List of field names in the order they appear in the model
    """
    with open(model_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row["Field"] for row in reader if row["Field"].strip()]

def get_existing_filenames(csv_path: Path) -> Set[str]:
    """
    Reads existing CSV and returns a set of source_filename values.
    
    Args:
        csv_path: Path to the existing CSV file
        
    Returns:
        Set of source_filename values already in the CSV
    """
    if not csv_path.exists():
        return set()
    
    existing = set()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "source_filename" in row and row["source_filename"]:
                existing.add(row["source_filename"])
    
    return existing

def bill_to_row(bill: Bill, columns: List[str]) -> dict:
    """
    Converts a Bill model to a CSV row dictionary.
    
    Args:
        bill: The Bill model instance
        columns: List of column names in order
        
    Returns:
        Dictionary with column names as keys
    """
    bill_dict = bill.model_dump()
    row = {}
    for col in columns:
        value = bill_dict.get(col, "")
        # Convert None to empty string, dates are already ISO strings
        if value is None:
            row[col] = ""
        else:
            row[col] = str(value)
    return row

def export_to_csv(json_dir: Path, output_csv: Path, model_csv: Path) -> None:
    """
    Reads JSON files from json_dir, converts to CSV rows, and writes/appends to output_csv.
    
    Args:
        json_dir: Directory containing JSON files
        output_csv: Path to the output CSV file
        model_csv: Path to the data model CSV (for column order)
    """
    # Get column order from model
    columns = get_column_order(model_csv)
    
    # Get existing filenames if CSV exists
    existing_filenames = get_existing_filenames(output_csv)
    
    # Find all JSON files
    json_files = list(json_dir.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {json_dir}")
        return
    
    # Process JSON files
    new_rows = []
    skipped = 0
    
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate as Bill model
            bill = Bill(**data)
            
            # Skip if already exists
            if bill.source_filename and bill.source_filename in existing_filenames:
                skipped += 1
                continue
            
            # Convert to row
            row = bill_to_row(bill, columns)
            new_rows.append(row)
            
            # Track this filename
            if bill.source_filename:
                existing_filenames.add(bill.source_filename)
                
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
            continue
    
    if not new_rows:
        print(f"No new rows to add. {skipped} file(s) skipped (already in CSV).")
        return
    
    # Write or append to CSV
    file_exists = output_csv.exists()
    mode = "a" if file_exists else "w"
    
    with open(output_csv, mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        
        # Write header if new file
        if not file_exists:
            writer.writeheader()
        
        # Write rows
        writer.writerows(new_rows)
    
    print(f"Exported {len(new_rows)} row(s) to {output_csv}")
    if skipped > 0:
        print(f"Skipped {skipped} duplicate file(s)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export structured JSON data to CSV")
    parser.add_argument("--json-dir", type=Path, default=Path("data/processed/structured_output"), 
                       help="Directory containing JSON files")
    parser.add_argument("--output", type=Path, default=Path("data/processed/database.csv"),
                       help="Output CSV file path")
    parser.add_argument("--model", type=Path, default=Path("data/raw/data_model.csv"),
                       help="Data model CSV file path")
    args = parser.parse_args()
    
    export_to_csv(args.json_dir, args.output, args.model)

