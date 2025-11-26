from pathlib import Path
from typing import Dict, Any
import argparse
from docling.document_converter import DocumentConverter

class BillParser:
    def __init__(self):
        """Initialize the Docling DocumentConverter."""
        self.converter = DocumentConverter()

    def convert_image(self, file_path: str | Path):
        """
        Convert a single image file using Docling.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            ConversionResult: The raw result from Docling
        """
        return self.converter.convert(file_path)

    def export_markdown(self, conversion_result) -> str:
        """
        Export the conversion result to Markdown.
        
        Args:
            conversion_result: The result object from convert_image
            
        Returns:
            str: Markdown representation of the document
        """
        return conversion_result.document.export_to_markdown()

    def export_json(self, conversion_result) -> Dict[str, Any]:
        """
        Export the conversion result to a dictionary (JSON structure).
        
        Args:
            conversion_result: The result object from convert_image
            
        Returns:
            dict: Dictionary representation of the document
        """
        return conversion_result.document.export_to_dict()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test BillParser independently")
    parser.add_argument("image_path", type=Path, help="Path to image file")
    args = parser.parse_args()
    
    if not args.image_path.exists():
        print(f"File not found: {args.image_path}")
        exit(1)
        
    bill_parser = BillParser()
    print(f"Processing {args.image_path}...")
    result = bill_parser.convert_image(args.image_path)
    md = bill_parser.export_markdown(result)
    
    print("\n--- Markdown Output ---\n")
    print(md)
