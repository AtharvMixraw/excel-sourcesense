# Excel SourceSense

**Intelligent Excel Metadata Extraction using Atlan Apps Framework**

Built for the Atlan SourceSense Assessment - A comprehensive Excel file analyzer that extracts metadata, performs data quality analysis, and generates interactive visualizations.

## Features

- **Multi-format Support**: Excel (.xlsx, .xls) and CSV files
- **Comprehensive Metadata**: Schema information, column analysis, data types
- **Data Quality Metrics**: Null counts, uniqueness, quality scoring
- **Interactive Visualizations**: Charts powered by Plotly.js
- **Atlan SDK Integration**: Full framework compliance with observability
- **Professional UI**: Modern web interface with drag-and-drop upload

## Architecture

Built using Atlan Apps Framework with:
- **FastAPI**: Modern web framework for API endpoints
- **Temporal**: Workflow orchestration (simulated)
- **Pandas**: Excel data processing and analysis
- **Plotly.js**: Interactive data visualizations
- **Atlan SDK**: Observability, logging, metrics, tracing

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [Temporal CLI](https://docs.temporal.io/cli)

### Installation Guides
- [macOS Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/MAC.md)
- [Linux Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/LINUX.md)
- [Windows Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/WINDOWS.md)

## Quick Start

1. **Download required components:**
   ```bash
   uv run poe download-components
   ```

2. **Set up environment variables (see .env in the doc)**

3. **Start dependencies (in separate terminal):**
   ```bash
   uv run poe start-deps
   ```

4. **Run the application:**
   ```bash
   uv run main.py
   ```

### Access
- **Web Interface**: http://localhost:8000
- **Temporal UI**: http://localhost:8233

## Usage

1. **Upload Excel File**: Drag & drop or browse to select
2. **View Metadata**: Comprehensive schema and column information
3. **Quality Analysis**: Data quality metrics and scoring
4. **Visualizations**: Interactive charts and graphs
5. **Export**: JSON/CSV export functionality

## Testing
You can generate fresh sample Excel and CSV files for testing:

```
uv run poe create-sample-data
```
This will create files under the sample_data/ directory:

- company_data.xlsx → Contains multiple sheets (Employees, Sales)
- sales_data.csv → Standalone CSV version of the sales dataset

Additionally, the repository includes pre-defined test files (uploads folder):-
- `company_employees.xlsx`: Multi-sheet workbook
- `sales_analytics.xlsx`: Large dataset
- `customer_survey.xlsx`: Data quality issues
- `financial_report.xlsx`: Complex data types

## Project Structure

```
excel-sourcesense/
├── app/                    # Core application logic
│   ├── activities.py       # Metadata extraction activities
│   ├── clients.py          # Excel file client
│   ├── handlers.py         # HTTP request handlers
│   ├── transformer.py      # Atlan entity transformation
│   └── workflows.py        # Workflow orchestration
├── components/             # Dapr components (auto-downloaded)
├── frontend/               # Web interface
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, assets
├── deploy/                 # Installation and deployment files
├── local/                  # Local data storage
├── uploads/                # File upload directory
├── sample_data/            # Sample Excel files
├── main.py                 # Application entry point
├── pyproject.toml          # Dependencies and config
└── README.md               # This file
```

## Atlan Assessment Compliance

- **Framework Integration**: Full Atlan SDK usage
- **Data Source**: Excel/CSV file processing
- **Metadata Extraction**: Schema, columns, data types
- **Quality Metrics**: Comprehensive data analysis
- **Visualizations**: Interactive charts and graphs
- **Professional UI**: Production-ready interface

## Development

### Stop Dependencies
```bash
uv run poe stop-deps
```

> **Note**: Make sure you have a `.env` file (ATTACHED IN THE SUBMISSION DOC)

## Learning Resources

- [Atlan Application SDK Documentation](https://github.com/atlanhq/application-sdk/tree/main/docs)
- [Excel Processing with Pandas Documentation](https://pandas.pydata.org/docs/user_guide/io.html#excel-files)
- [Python FastAPI Documentation](https://fastapi.tiangolo.com/)


## License

Built for Atlan SourceSense Assessment
