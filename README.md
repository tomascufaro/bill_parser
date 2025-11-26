# bill_parser
MVP for a bill parser application with an enriched layer to add value over the extracted data.

## Phase 3: Semantic Extraction
The pipeline now supports semantic data extraction using Docling (for layout/text) and OpenAI (for structured parsing).

### Setup
1.  **Dependencies**: Ensure all packages are installed.
    ```bash
    uv sync
    ```
2.  **Environment**:
    - Copy `.env.example` to `.env`
    - Add your `OPENAI_API_KEY` to `.env`

### Usage
Run the pipeline with `main.py`.

**Process fresh images (Docling + LLM):**
```bash
python main.py --limit 3
```

### Output
- **Raw Docling**: `data/processed/docling_output/` (*.md, *.json)
- **Final Structured Data**: `data/processed/structured_output/` (*.json)
- **Structured Database**: `data/processed/database.csv`

## Reporter Layer
Generate a Markdown report and monthly spend plot from the consolidated database.

### Usage
After running the main pipeline (to populate `database.csv`), run:

```bash
python -m src.reporter
```

This will:
- Read `data/processed/database.csv`
- Generate a monthly spend line plot at `reports/monthly_spend.png`
- Generate a Markdown report at `reports/spending_report.md`

