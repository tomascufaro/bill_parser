from pathlib import Path
from typing import Dict, Any
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
