"""
This file contains the client for the Excel metadata extraction application.
Handles Excel file connections and data reading operations.
"""
import os
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
from application_sdk.clients.sql import AsyncBaseSQLClient
from application_sdk.observability.logger_adaptor import get_logger

logger = get_logger(__name__)

class ExcelClient(AsyncBaseSQLClient):
    """
    Client for handling Excel file operations and metadata extraction.
    Supports .xlsx, .xls, and .csv files.
    """
    
    SUPPORTED_EXTENSIONS = ['.xlsx', '.xls', '.csv']
    
    # Override the DB_CONFIG to disable SQL-specific validation
    DB_CONFIG = {
        "template": "file://{file_path}",
        "required": ["file_path"],
    }
    
    def __init__(self, connection_config: Dict[str, Any] = None):
        """
        Initialize Excel client with file path configuration.
        
        Args:
            connection_config: Dictionary containing file path and options (can be None for SDK compatibility)
        """
        # Handle SDK instantiation without parameters
        if connection_config is None:
            connection_config = {"file_path": ""}
        
        # Initialize the parent class but we won't use SQL functionality
        super().__init__(connection_config)
        
        self.file_path = connection_config.get('file_path', '')
        self.workbook_data = {}
        self.file_metadata = {}
        self._connected = False
        
    def set_file_path(self, file_path: str):
        """Set the file path for the Excel client."""
        self.file_path = file_path
        self.connection_config = {"file_path": file_path}
        
    async def connect(self) -> bool:
        """
        Establish connection to Excel file(s).
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self.file_path or self.file_path == "":
                logger.warning("No file path provided, client ready but not connected")
                return True  # Return True for SDK compatibility
                
            file_path = Path(self.file_path)
            
            if not file_path.exists():
                logger.error(f"File does not exist: {self.file_path}")
                return False
                
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                logger.error(f"Unsupported file type: {file_path.suffix}")
                return False
                
            # Store file metadata
            self.file_metadata = {
                'file_name': file_path.name,
                'file_path': str(file_path.absolute()),
                'file_size': file_path.stat().st_size,
                'file_extension': file_path.suffix.lower(),
                'modified_time': file_path.stat().st_mtime
            }
            
            # Load Excel data
            await self._load_workbook_data()
            self._connected = True
            logger.info(f"Successfully connected to Excel file: {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Excel file: {str(e)}")
            return False
    
    async def _load_workbook_data(self):
        """Load all sheets from the Excel workbook."""
        try:
            file_path = Path(self.file_path)
            
            if file_path.suffix.lower() == '.csv':
                # Handle CSV files
                df = pd.read_csv(self.file_path)
                self.workbook_data = {'Sheet1': df}
            else:
                # Handle Excel files
                excel_file = pd.ExcelFile(self.file_path)
                self.workbook_data = {}
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                        self.workbook_data[sheet_name] = df
                        logger.info(f"Loaded sheet: {sheet_name} with {len(df)} rows")
                    except Exception as e:
                        logger.warning(f"Failed to load sheet {sheet_name}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Failed to load workbook data: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from Excel file."""
        self.workbook_data.clear()
        self.file_metadata.clear()
        self._connected = False
        logger.info("Disconnected from Excel file")
    
    def get_sheet_names(self) -> List[str]:
        """Get list of all sheet names."""
        return list(self.workbook_data.keys())
    
    def get_sheet_data(self, sheet_name: str) -> Optional[pd.DataFrame]:
        """Get DataFrame for specific sheet."""
        return self.workbook_data.get(sheet_name)
    
    def get_file_metadata(self) -> Dict[str, Any]:
        """Get file metadata information."""
        return self.file_metadata.copy()
    
    def is_connected(self) -> bool:
        """Check if client is connected to a file."""
        return self._connected
    
    # Override parent methods to prevent SQL operations
    async def get_connection_string(self) -> str:
        """Return a dummy connection string for compatibility."""
        return f"file://{self.file_path}"
    
    async def test_connection(self) -> bool:
        """Test connection to Excel file."""
        return await self.connect()
