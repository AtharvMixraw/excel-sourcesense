"""
Handler for Excel metadata extraction requests.
Uses correct Atlan SDK imports and patterns.
"""
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path
import asyncio
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from app.clients import ExcelClient

logger = get_logger(__name__)
metrics = get_metrics()
traces = get_traces()

class ExcelMetadataHandler:
    """
    Handler for Excel metadata extraction operations.
    Integrates with Atlan SDK's observability and patterns.
    """
    
    def __init__(self):
        """Initialize Excel metadata handler."""
        self.upload_dir = Path("./uploads")
        self.sample_dir = Path("./sample_data")
        
        # Ensure directories exist
        self.upload_dir.mkdir(exist_ok=True)
        self.sample_dir.mkdir(exist_ok=True)
        
        # Storage for results (in production, this would use a database)
        self._workflow_results = {}
    
    @observability(logger=logger, metrics=metrics, traces=traces)
    async def handle_file_upload(self, file: UploadFile) -> Dict[str, Any]:
        """Handle Excel file upload with SDK observability."""
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file selected")
            
            # Check file extension
            allowed_extensions = ['.xlsx', '.xls', '.csv']
            file_ext = '.' + file.filename.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type. Supported: {', '.join(allowed_extensions)}"
                )
            
            # Save uploaded file
            file_path = self.upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"File uploaded successfully: {file_path}")
            
            # Process the file
            result = await self.process_excel_file(str(file_path), file.filename)
            
            return {
                "success": True,
                "filename": file.filename,
                "file_path": str(file_path),
                "workflow_id": f"excel_{file.filename}_{hash(str(file_path)) % 10000}",
                "result": result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @observability(logger=logger, metrics=metrics, traces=traces)
    async def handle_sample_file(self, filename: str) -> Dict[str, Any]:
        """Handle sample file processing with SDK observability."""
        try:
            sample_file = self.sample_dir / filename
            if not sample_file.exists():
                # Create sample file if it doesn't exist
                await self.create_sample_file(filename)
            
            # Process the sample file
            result = await self.process_excel_file(str(sample_file), filename)
            
            return {
                "success": True,
                "filename": filename,
                "file_path": str(sample_file),
                "workflow_id": f"sample_{filename}_{hash(str(sample_file)) % 10000}",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Sample file processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_sample_file(self, filename: str):
        """Create sample file if it doesn't exist."""
        import pandas as pd
        import random
        from datetime import datetime, timedelta
        
        try:
            if filename == "company_data.xlsx":
                # Create company data sample
                employees = pd.DataFrame({
                    'employee_id': range(1, 51),
                    'name': [f'Employee {i}' for i in range(1, 51)],
                    'department': random.choices(['Engineering', 'Sales', 'Marketing', 'HR'], k=50),
                    'salary': [random.randint(40000, 100000) for _ in range(50)],
                    'hire_date': [datetime.now() - timedelta(days=random.randint(30, 1825)) for _ in range(50)],
                    'is_active': random.choices([True, False], weights=[85, 15], k=50)
                })
                
                sales = pd.DataFrame({
                    'order_id': range(1, 101),
                    'customer_name': [f'Customer {i}' for i in range(1, 101)],
                    'product': random.choices(['Product A', 'Product B', 'Product C'], k=100),
                    'quantity': [random.randint(1, 5) for _ in range(100)],
                    'price': [round(random.uniform(10.0, 500.0), 2) for _ in range(100)],
                    'order_date': [datetime.now() - timedelta(days=random.randint(1, 365)) for _ in range(100)]
                })
                
                # Save with multiple sheets
                with pd.ExcelWriter(self.sample_dir / filename, engine='openpyxl') as writer:
                    employees.to_excel(writer, sheet_name='Employees', index=False)
                    sales.to_excel(writer, sheet_name='Sales', index=False)
                    
            elif filename == "sales_data.csv":
                # Create CSV sample
                sales_data = pd.DataFrame({
                    'date': [datetime.now() - timedelta(days=i) for i in range(30)],
                    'product': random.choices(['Widget A', 'Widget B', 'Widget C'], k=30),
                    'sales_amount': [round(random.uniform(100, 1000), 2) for _ in range(30)],
                    'units_sold': [random.randint(1, 20) for _ in range(30)],
                    'region': random.choices(['North', 'South', 'East', 'West'], k=30)
                })
                sales_data.to_csv(self.sample_dir / filename, index=False)
                
            logger.info(f"Created sample file: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to create sample file {filename}: {str(e)}")
            raise
    
    @observability(logger=logger, metrics=metrics, traces=traces)
    async def process_excel_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process Excel file using SDK activities."""
        try:
            # Initialize Excel client
            client = ExcelClient({'file_path': file_path})
            
            # Connect and validate
            if not await client.connect():
                raise Exception("Failed to connect to Excel file")
            
            # Initialize activities
            from app.activities import ExcelMetadataExtractionActivities
            activities = ExcelMetadataExtractionActivities()
            
            # Create workflow args
            workflow_args = {
                'file_path': file_path,
                'excel_client': client,
                'filename': filename
            }
            
            # Execute activities in sequence (simulating workflow)
            logger.info("Starting metadata extraction activities...")
            
            await activities.fetch_databases(workflow_args)
            await activities.fetch_schemas(workflow_args)
            await activities.fetch_tables(workflow_args)
            await activities.fetch_columns(workflow_args)
            await activities.generate_visualizations(workflow_args)
            
            # Transform data
            from app.transformer import ExcelAtlasTransformer
            transformer = ExcelAtlasTransformer(
                connector_name="excel-sourcesense", 
                tenant_id="default"
            )
            
            metadata_for_transform = {
                'database_info': workflow_args.get('database_info', {}),
                'schema_info': workflow_args.get('schema_info', {}),
                'tables_info': workflow_args.get('tables_info', []),
                'columns_info': workflow_args.get('columns_info', []),
                'visualizations': workflow_args.get('visualizations', [])
            }
            
            transformed_entities = transformer.transform(metadata_for_transform)
            
            # Get database info safely
            database_info = workflow_args.get('database_info', {})
            
            # Prepare final result
            result = {
                'database_info': database_info,
                'schema_info': workflow_args.get('schema_info', {}),
                'tables_info': workflow_args.get('tables_info', []),
                'columns_info': workflow_args.get('columns_info', []),
                'visualizations': workflow_args.get('visualizations', []),
                'transformed_entities': transformed_entities,
                'processing_summary': {
                    'total_sheets': len(workflow_args.get('tables_info', [])),
                    'total_columns': len(workflow_args.get('columns_info', [])),
                    'file_size': database_info.get('file_size', 0),
                    'processing_time': '< 1 second'
                }
            }
            
            # Store result
            self._workflow_results[filename] = result
            
            # Cleanup
            await client.disconnect()
            
            logger.info(f"Successfully processed Excel file: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"File processing failed: {str(e)}")
            raise
    
    def get_workflow_result(self, filename: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored workflow result."""
        return self._workflow_results.get(filename)
