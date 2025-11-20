# bill_parser
MVP for a bill parser application with an enriched layer to add value over the extracted data.

## Phase 2: Docling Exploration
We are currently in a discovery phase to evaluate the capabilities of [Docling](https://github.com/DS4SD/docling) for parsing bill images.

### Usage
To run the batch processing on the sample dataset:

```bash
python main.py
```

This script will:
1.  Look for `.jpg` files in `data/raw/sample/`
2.  Convert each image using Docling
3.  Save the results in `data/processed/docling_output/`:
    - `*.md`: Markdown representation of the document layout and text
    - `*.json`: Full structured JSON output

The output of this phase will inform the strategy for structured data extraction (Phase 3).
