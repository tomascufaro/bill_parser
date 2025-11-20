import json
import os
from pathlib import Path
from src.parser import BillParser

def main():
    print("Starting Docling exploration phase...")
    
    # Define paths
    base_dir = Path(__file__).parent
    input_dir = base_dir / "data/raw/sample"
    output_dir = base_dir / "data/processed/docling_output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize parser
    parser = BillParser()
    
    # Get list of jpg files
    image_files = list(input_dir.glob("*.jpg"))
    
    if not image_files:
        print(f"No .jpg files found in {input_dir}")
        return

    print(f"Found {len(image_files)} images to process.")
    
    for i, img_path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Processing {img_path.name}...")
        
        try:
            # Convert
            result = parser.convert_image(img_path)
            
            # Export formats
            md_content = parser.export_markdown(result)
            json_content = parser.export_json(result)
            
            # Save Markdown
            md_path = output_dir / f"{img_path.stem}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            # Save JSON
            json_path = output_dir / f"{img_path.stem}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_content, f, ensure_ascii=False, indent=2)
                
            print(f"  Saved outputs to {output_dir}")
            
        except Exception as e:
            print(f"  Error processing {img_path.name}: {str(e)}")

    print("\nBatch processing completed.")

if __name__ == "__main__":
    main()
