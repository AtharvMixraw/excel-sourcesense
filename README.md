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

## Setup & Installation

### Prerequisites
- Python 3.11+
- uv (Python package manager)

### Installation

```bash
# Clone the repository
git clone [your-repo-url]
cd excel-sourcesense

# Install dependencies
uv sync

# Start the application
uv run main.py
```

### Access
- **Web Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Usage

1. **Upload Excel File**: Drag & drop or browse to select
2. **View Metadata**: Comprehensive schema and column information
3. **Quality Analysis**: Data quality metrics and scoring
4. **Visualizations**: Interactive charts and graphs
5. **Export**: JSON/CSV export functionality

## Testing

Sample files are automatically generated:
- `company_employees.xlsx`: Multi-sheet workbook
- `sales_analytics.xlsx`: Large dataset
- `customer_survey.xlsx`: Data quality issues
- `financial_report.xlsx`: Complex data types

## Project Structure

```
excel-sourcesense/
├── app/                    # Core application
│   ├── activities.py       # Metadata extraction activities
│   ├── clients.py          # Excel file client
│   ├── handlers.py         # HTTP request handlers
│   ├── transformer.py      # Atlan entity transformation
│   └── workflows.py        # Workflow orchestration
├── frontend/               # Web interface
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, assets
├── uploads/                # File upload directory
├── sample_data/            # Sample Excel files
└── main.py                 # Application entry point
```

## Atlan Assessment Compliance

- **Framework Integration**: Full Atlan SDK usage
- **Data Source**: Excel/CSV file processing
- **Metadata Extraction**: Schema, columns, data types
- **Quality Metrics**: Comprehensive data analysis
- **Visualizations**: Interactive charts and graphs
- **Professional UI**: Production-ready interface

## Demo Video

[Link to 5-7 minute demo video showcasing features]

## License

Built for Atlan SourceSense Assessment
