"""
This file contains the activities for the Excel metadata extraction application.
Handles Excel file analysis and metadata extraction.
"""

from typing import Any, Dict, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from application_sdk.activities.common.models import ActivityStatistics
from application_sdk.activities.common.utils import auto_heartbeater
from application_sdk.activities.metadata_extraction.sql import (
    BaseSQLMetadataExtractionActivities,
    BaseSQLMetadataExtractionActivitiesState,
)
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.services.secretstore import SecretStore
from temporalio import activity

logger = get_logger(__name__)
activity.logger = logger
metrics = get_metrics()
traces = get_traces()

class ExcelMetadataExtractionActivities(BaseSQLMetadataExtractionActivities):
    
    def _convert_to_json_serializable(self, obj):
        """Convert numpy/pandas types to JSON serializable types."""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (pd.Series, pd.Index)):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif pd.isna(obj) or obj is None or obj == np.nan:
            return None
        elif hasattr(obj, 'dtype'):
            return str(obj)
        else:
            return obj

    @observability(logger=logger, metrics=metrics, traces=traces)
    
    @activity.defn
    async def get_workflow_args(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow arguments from config."""
        from datetime import datetime

        workflow_args = workflow_config.copy()
        workflow_args['processing_start_time'] = datetime.now().isoformat()

        return workflow_args


    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    async def preflight_check(self, workflow_args: Dict[str, Any]) -> bool:
        """Perform preflight checks."""
        file_path = workflow_args.get('file_path')
        if not file_path or not Path(file_path).exists():
            raise Exception(f"File not found: {file_path}")
        return True

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_databases(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Extract database metadata (Excel workbook information)."""
        try:
            file_path = workflow_args.get('file_path') or workflow_args.get('credential_guid')
            if not file_path:
                logger.error("No file path provided in workflow args")
                return ActivityStatistics(processed_count=0, error_count=1)

            from app.clients import ExcelClient
            excel_client = ExcelClient({'file_path': file_path})
            if not await excel_client.connect():
                logger.error("Failed to connect to Excel file")
                return ActivityStatistics(processed_count=0, error_count=1)

            file_metadata = excel_client.get_file_metadata()
            database_info = {
                'database_name': file_metadata.get('file_name', '').replace('.xlsx', '').replace('.xls', '').replace('.csv', ''),
                'file_path': file_metadata.get('file_path'),
                'file_size': int(file_metadata.get('file_size', 0)),
                'file_type': file_metadata.get('file_extension'),
                'modified_date': datetime.fromtimestamp(file_metadata.get('modified_time', 0)),
                'sheet_count': len(excel_client.get_sheet_names())
            }

            database_info = self._convert_to_json_serializable(database_info)
            workflow_args['excel_client'] = excel_client
            workflow_args['database_info'] = database_info

            logger.info(f"Extracted database metadata for: {database_info['database_name']}")
            return ActivityStatistics(processed_count=1, error_count=0)

        except Exception as e:
            logger.error(f"Failed to fetch database metadata: {str(e)}")
            return ActivityStatistics(processed_count=0, error_count=1)

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_schemas(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Extract schema metadata (Excel workbook schema)."""
        try:
            database_info = workflow_args.get('database_info', {})
            schema_info = {
                'schema_name': database_info.get('database_name', 'default_schema'),
                'database_name': database_info.get('database_name'),
                'table_count': database_info.get('sheet_count', 0),
                'file_path': database_info.get('file_path')
            }

            schema_info = self._convert_to_json_serializable(schema_info)
            workflow_args['schema_info'] = schema_info

            logger.info(f"Extracted schema metadata: {schema_info['schema_name']}")
            return ActivityStatistics(processed_count=1, error_count=0)

        except Exception as e:
            logger.error(f"Failed to fetch schema metadata: {str(e)}")
            return ActivityStatistics(processed_count=0, error_count=1)

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_tables(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Extract table metadata (Excel sheets information)."""
        try:
            excel_client = workflow_args.get('excel_client')
            if not excel_client:
                logger.error("Excel client not found")
                return ActivityStatistics(processed_count=0, error_count=1)

            sheet_names = excel_client.get_sheet_names()
            tables_info = []

            for sheet_name in sheet_names:
                df = excel_client.get_sheet_data(sheet_name)
                if df is not None:
                    data_types = {}
                    for col, dtype in df.dtypes.items():
                        data_types[str(col)] = str(dtype)

                    table_info = {
                        'table_name': str(sheet_name),
                        'schema_name': str(workflow_args.get('schema_info', {}).get('schema_name', 'default')),
                        'row_count': int(len(df)),
                        'column_count': int(len(df.columns)),
                        'has_header': True,
                        'data_types': data_types,
                        'memory_usage': int(df.memory_usage(deep=True).sum())
                    }

                    table_info = self._convert_to_json_serializable(table_info)
                    tables_info.append(table_info)

            workflow_args['tables_info'] = tables_info
            logger.info(f"Extracted {len(tables_info)} table metadata records")
            return ActivityStatistics(processed_count=len(tables_info), error_count=0)

        except Exception as e:
            logger.error(f"Failed to fetch table metadata: {str(e)}")
            return ActivityStatistics(processed_count=0, error_count=1)

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_columns(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Extract column metadata from Excel sheets."""
        try:
            excel_client = workflow_args.get('excel_client')
            tables_info = workflow_args.get('tables_info', [])

            if not excel_client or not tables_info:
                logger.error("Required data not found in workflow args")
                return ActivityStatistics(processed_count=0, error_count=1)

            columns_info = []
            total_columns = 0

            for table_info in tables_info:
                sheet_name = table_info['table_name']
                df = excel_client.get_sheet_data(sheet_name)

                if df is not None:
                    for idx, column_name in enumerate(df.columns):
                        column_data = df[column_name]
                        column_metadata = self._analyze_column(
                            column_data, str(column_name), idx + 1,
                            sheet_name, table_info['schema_name']
                        )

                        column_metadata = self._convert_to_json_serializable(column_metadata)
                        columns_info.append(column_metadata)
                        total_columns += 1

            workflow_args['columns_info'] = columns_info
            logger.info(f"Extracted {total_columns} column metadata records")
            return ActivityStatistics(processed_count=total_columns, error_count=0)

        except Exception as e:
            logger.error(f"Failed to fetch column metadata: {str(e)}")
            return ActivityStatistics(processed_count=0, error_count=1)

    def _analyze_column(self, column_data: pd.Series, column_name: str, position: int,
                       table_name: str, schema_name: str) -> Dict[str, Any]:
        """Analyze individual column and extract metadata."""
        dtype_mapping = {
            'int64': 'INTEGER',
            'float64': 'DECIMAL',
            'object': 'VARCHAR',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'DATETIME',
            'category': 'VARCHAR'
        }

        column_info = {
            'table_name': str(table_name),
            'schema_name': str(schema_name),
            'column_name': str(column_name),
            'ordinal_position': int(position),
            'data_type': dtype_mapping.get(str(column_data.dtype), 'VARCHAR'),
            'is_nullable': 'YES' if column_data.isnull().any() else 'NO',
        }

        # Quality metrics
        total_count = int(len(column_data))
        null_count = int(column_data.isnull().sum())
        unique_count = int(column_data.nunique())

        column_info.update({
            'total_count': total_count,
            'null_count': null_count,
            'null_percentage': round(float((null_count / total_count) * 100), 2) if total_count > 0 else 0.0,
            'unique_count': unique_count,
            'unique_percentage': round(float((unique_count / total_count) * 100), 2) if total_count > 0 else 0.0,
        })

        # Quality level
        null_pct = column_info['null_percentage']
        if null_pct <= 10:
            column_info['quality_level'] = 'HIGH'
        elif null_pct <= 30:
            column_info['quality_level'] = 'MEDIUM'
        else:
            column_info['quality_level'] = 'LOW'

        # Numeric analysis
        if pd.api.types.is_numeric_dtype(column_data):
            non_null_data = column_data.dropna()
            if not non_null_data.empty:
                try:
                    column_info.update({
                        'min_value': float(non_null_data.min()),
                        'max_value': float(non_null_data.max()),
                        'mean_value': float(non_null_data.mean()),
                    })
                except (ValueError, TypeError):
                    pass

        # String analysis
        elif pd.api.types.is_string_dtype(column_data) or column_data.dtype == 'object':
            non_null_data = column_data.dropna()
            if not non_null_data.empty:
                try:
                    str_lengths = non_null_data.astype(str).str.len()
                    column_info.update({
                        'avg_length': round(float(str_lengths.mean()), 2),
                        'max_length': int(str_lengths.max()),
                        'min_length': int(str_lengths.min()),
                    })
                except (ValueError, TypeError):
                    pass

        return column_info

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def generate_visualizations(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Generate visualizations from Excel data."""
        try:
            excel_client = workflow_args.get('excel_client')
            if not excel_client:
                logger.error("Excel client not found")
                return ActivityStatistics(processed_count=0, error_count=1)

            visualizations = []
            sheet_names = excel_client.get_sheet_names()

            for sheet_name in sheet_names:
                df = excel_client.get_sheet_data(sheet_name)
                if df is not None and not df.empty:
                    viz_data = self._generate_sheet_visualizations(df, sheet_name)
                    visualizations.extend(viz_data)

            visualizations = self._convert_to_json_serializable(visualizations)
            workflow_args['visualizations'] = visualizations

            logger.info(f"Generated {len(visualizations)} visualizations")
            return ActivityStatistics(processed_count=len(visualizations), error_count=0)

        except Exception as e:
            logger.error(f"Failed to generate visualizations: {str(e)}")
            return ActivityStatistics(processed_count=0, error_count=1)

    def _generate_sheet_visualizations(self, df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Generate visualization data for a specific sheet."""
        visualizations = []

        try:
            # Data quality overview
            quality_viz = {
                'type': 'bar_chart',
                'title': f'Data Quality Overview - {sheet_name}',
                'data': {
                    'columns': [str(col) for col in df.columns.tolist()],
                    'null_counts': [int(count) for count in df.isnull().sum().tolist()],
                    'total_rows': int(len(df))
                }
            }
            visualizations.append(quality_viz)

            # Data type distribution
            dtype_counts = df.dtypes.value_counts()
            dtype_viz = {
                'type': 'pie_chart',
                'title': f'Data Type Distribution - {sheet_name}',
                'data': {
                    'labels': [str(dtype) for dtype in dtype_counts.index],
                    'values': [int(count) for count in dtype_counts.tolist()]
                }
            }
            visualizations.append(dtype_viz)

            # Numeric column statistics
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                numeric_stats = df[numeric_columns].describe()
                stats_dict = {}
                
                for col in numeric_columns:
                    if col in numeric_stats.columns:
                        col_stats = {}
                        for stat_name in numeric_stats.index:
                            try:
                                value = numeric_stats.loc[stat_name, col]
                                if pd.notna(value):
                                    col_stats[str(stat_name)] = float(value)
                            except (ValueError, TypeError):
                                col_stats[str(stat_name)] = 0.0
                        stats_dict[str(col)] = col_stats

                stats_viz = {
                    'type': 'heatmap',
                    'title': f'Numeric Column Statistics - {sheet_name}',
                    'data': {
                        'columns': [str(col) for col in numeric_columns.tolist()],
                        'statistics': stats_dict
                    }
                }
                visualizations.append(stats_viz)

        except Exception as e:
            logger.error(f"Error generating visualizations for {sheet_name}: {str(e)}")

        return visualizations

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    async def transform_data(self, workflow_args: Dict[str, Any]) -> bool:
        """Transform extracted data to Atlan format."""
        try:
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
            workflow_args['transformed_entities'] = transformed_entities
            
            logger.info("Successfully transformed metadata to Atlan format")
            return True
            
        except Exception as e:
            logger.error(f"Failed to transform data: {str(e)}")
            return False
