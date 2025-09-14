"""
Main entry point for the Excel metadata extraction application.
This module initializes and runs the Excel metadata extraction application,
using the Atlan Apps Framework with correct import paths.
"""
import asyncio
import uvicorn
from pathlib import Path
from app.activities import ExcelMetadataExtractionActivities
from app.clients import ExcelClient
from app.transformer import ExcelAtlasTransformer
from app.workflows import ExcelMetadataExtractionWorkflow
from app.handlers import ExcelMetadataHandler
from application_sdk.application.metadata_extraction.sql import (
    BaseSQLMetadataExtractionApplication,
)
from application_sdk.common.error_codes import ApiError
from application_sdk.constants import APPLICATION_NAME
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse


logger = get_logger(__name__)
metrics = get_metrics()
traces = get_traces()


class ExcelSourceSenseApp:
    """
    Excel SourceSense application using Atlan SDK components
    with a custom web interface for Excel processing.
    """
    
    def __init__(self):
        """Initialize the Excel SourceSense application."""
        self.app = FastAPI(
            title="Excel SourceSense",
            description="Intelligent Excel Metadata Extraction using Atlan Apps Framework",
            version="1.0.0"
        )
        self.handler = ExcelMetadataHandler()
        self.setup_routes()
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        Path("uploads").mkdir(exist_ok=True)
        Path("sample_data").mkdir(exist_ok=True)
        Path("local").mkdir(exist_ok=True)
        Path("frontend/static").mkdir(parents=True, exist_ok=True)
        Path("frontend/templates").mkdir(parents=True, exist_ok=True)
    
    def setup_routes(self):
        """Setup HTTP routes using Atlan SDK patterns."""
        
        # Serve static files
        self.app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
        
        @self.app.get("/")
        async def index():
            """Serve the main application page."""
            try:
                return FileResponse("frontend/templates/index.html")
            except FileNotFoundError:
                return JSONResponse(
                    content={"error": "Frontend not found. Please ensure frontend/templates/index.html exists."},
                    status_code=404
                )
        
        @self.app.post("/api/upload")
        @observability(logger=logger, metrics=metrics, traces=traces)
        async def upload_file(file: UploadFile = File(...)):
            """Handle file upload using SDK handler."""
            return await self.handler.handle_file_upload(file)
        
        @self.app.post("/api/sample/{filename}")
        @observability(logger=logger, metrics=metrics, traces=traces)
        async def load_sample_file(filename: str):
            """Load sample file using SDK handler."""
            return await self.handler.handle_sample_file(filename)
        
        @self.app.get("/api/workflow/{workflow_id}/status")
        @observability(logger=logger, metrics=metrics, traces=traces)
        async def get_workflow_status(workflow_id: str):
            """Get workflow status - real Temporal if available, fallback otherwise."""
            
            # Try to get real status from Temporal
            temporal_client = await self.handler._get_temporal_client() if hasattr(self.handler, '_get_temporal_client') else None
            
            if temporal_client:
                try:
                    handle = temporal_client.get_workflow_handle(workflow_id)
                    result = await handle.describe()
                    
                    return JSONResponse(content={
                        "workflow_id": workflow_id,
                        "status": result.status.name.lower(),
                        "completed": result.status.name in ["COMPLETED", "FAILED", "TERMINATED"],
                        "temporal_url": f"http://localhost:8233/namespaces/default/workflows/{workflow_id}",
                        "temporal_available": True,
                        "error": None
                    })
                except Exception as e:
                    logger.warning(f"Could not get Temporal status for {workflow_id}: {e}")
            
            # Fallback response (existing behavior)
            return JSONResponse(content={
                "workflow_id": workflow_id,
                "status": "completed",
                "completed": True,
                "temporal_url": f"http://localhost:8233/namespaces/default/workflows/{workflow_id}",
                "temporal_available": False,
                "error": None
            })
        
        @self.app.get("/api/result/{filename}")
        @observability(logger=logger, metrics=metrics, traces=traces)
        async def get_result(filename: str):
            """Get processing result for a file."""
            result = self.handler.get_workflow_result(filename)
            if result:
                return JSONResponse(content=result)
            else:
                raise HTTPException(status_code=404, detail="Result not found")
        
        @self.app.post("/api/export")
        @observability(logger=logger, metrics=metrics, traces=traces)
        async def export_metadata(request: dict):
            """Export metadata in various formats."""
            try:
                metadata = request.get("metadata", {})
                export_format = request.get("format", "json")
                
                if export_format == "json":
                    import json
                    content = json.dumps(metadata, indent=2, default=str)
                    
                elif export_format == "csv":
                    import pandas as pd
                    columns_data = metadata.get("columns_info", [])
                    if columns_data:
                        df = pd.DataFrame(columns_data)
                        content = df.to_csv(index=False)
                    else:
                        content = "No column data available"
                else:
                    raise HTTPException(status_code=400, detail="Unsupported format")
                
                return JSONResponse(content={
                    "success": True,
                    "format": export_format,
                    "content": content
                })
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "app": "Excel SourceSense"}


@observability(logger=logger, metrics=metrics, traces=traces)
async def main():
    """Main application entry point."""
    try:
        logger.info("Starting Excel SourceSense application...")
        
        # Create application instance
        excel_app = ExcelSourceSenseApp()
        
        # Start the server
        logger.info("Server starting on http://localhost:8000")
        logger.info("Health check available at http://localhost:8000/health")
        
        config = uvicorn.Config(
            app=excel_app.app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True  # Set to True for development
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
