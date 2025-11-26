import os
import argparse
from pathlib import Path
from openai import OpenAI
from src.models import Bill

class BillExtractor:
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)

    def extract_data_from_markdown(self, markdown_text: str) -> Bill:
        """
        Extract structured data from markdown text using OpenAI's Structured Outputs.
        
        Args:
            markdown_text: The markdown content of the bill.
            
        Returns:
            Bill: A populated Pydantic model.
        """
        prompt = (
            "You are an expert data extraction assistant. "
            "Extract the following information from the provided bill/invoice markdown text. "
            "Ensure all required fields are populated accurately based on the document content."
        )

        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",  # Use a model that supports Structured Outputs
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": markdown_text},
                ],
                response_format=Bill,
            )
            
            # The parsed response is already a Bill instance
            bill_data = completion.choices[0].message.parsed
            return bill_data

        except Exception as e:
            print(f"Error during LLM extraction: {e}")
            raise

if __name__ == "__main__":
    # Load env vars for standalone run
    from dotenv import load_dotenv
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Test BillExtractor independently")
    parser.add_argument("md_path", type=Path, help="Path to markdown file")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/structured_output"),
                       help="Directory to save JSON output")
    args = parser.parse_args()
    
    if not args.md_path.exists():
        print(f"File not found: {args.md_path}")
        exit(1)
    
    # Create output directory if needed
    args.output_dir.mkdir(parents=True, exist_ok=True)
        
    try:
        extractor = BillExtractor()
        
        with open(args.md_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"Extracting data from {args.md_path}...")
        bill = extractor.extract_data_from_markdown(content)
        
        # Set source filename from markdown file name
        bill.source_filename = f"{args.md_path.stem}.jpg"
        
        # Save JSON output
        output_path = args.output_dir / f"{args.md_path.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(bill.model_dump_json(indent=2))
        
        print(f"\nSaved JSON output to {output_path}")
        print("\n--- JSON Output ---\n")
        print(bill.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
