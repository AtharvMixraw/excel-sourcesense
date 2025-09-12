"""
This file contains the transformer for the Excel metadata extraction application.
The transformer is responsible for transforming the raw Excel metadata into Atlan Type.
"""
from typing import Any, Dict, Optional, Type, List
from datetime import datetime
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.transformers.atlas import AtlasTransformer
from application_sdk.transformers.common.utils import build_atlas_qualified_name

logger = get_logger(__name__)

class ExcelDatabase:
    """Represents an Excel workbook as a database entity in Atlan."""
    
    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Excel workbook metadata into Atlan database entity attributes.
        
        Args:
            obj: Dictionary containing the raw Excel database metadata.
            
        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes.
        """
        attributes = {
            "name": obj.get("database_name", ""),
            "qualifiedName": build_atlas_qualified_name([obj.get("database_name", "")]),
            "displayName": obj.get("database_name", "").replace("_", " ").title(),
        }
        
        custom_attributes = {
            "filePath": obj.get("file_path", ""),
            "fileSize": obj.get("file_size", 0),
            "fileType": obj.get("file_type", ""),
            "modifiedDate": str(obj.get("modified_date", "")),
            "sheetCount": obj.get("sheet_count", 0),
            "sourceType": "Excel Workbook"
        }
        
        return {"attributes": attributes, "custom_attributes": custom_attributes}

class ExcelSchema:
    """Represents an Excel workbook schema entity in Atlan."""
    
    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Excel schema metadata into Atlan schema entity attributes.
        
        Args:
            obj: Dictionary containing the raw Excel schema metadata.
            
        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes.
        """
        qualified_name = build_atlas_qualified_name([
            obj.get("database_name", ""),
            obj.get("schema_name", "")
        ])
        
        attributes = {
            "name": obj.get("schema_name", ""),
            "qualifiedName": qualified_name,
            "displayName": obj.get("schema_name", "").replace("_", " ").title(),
        }
        
        custom_attributes = {
            "databaseName": obj.get("database_name", ""),
            "tableCount": obj.get("table_count", 0),
            "filePath": obj.get("file_path", ""),
            "sourceType": "Excel Schema"
        }
        
        return {"attributes": attributes, "custom_attributes": custom_attributes}

class ExcelTable:
    """Represents an Excel sheet as a table entity in Atlan."""
    
    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Excel sheet metadata into Atlan table entity attributes.
        
        Args:
            obj: Dictionary containing the raw Excel table metadata.
            
        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes.
        """
        qualified_name = build_atlas_qualified_name([
            obj.get("schema_name", ""),
            obj.get("table_name", "")
        ])
        
        attributes = {
            "name": obj.get("table_name", ""),
            "qualifiedName": qualified_name,
            "displayName": obj.get("table_name", "").replace("_", " ").title(),
        }
        
        # Calculate data quality score
        row_count = obj.get("row_count", 0)
        column_count = obj.get("column_count", 0)
        data_quality_score = min(100, (row_count * column_count) / 1000 * 10) if row_count and column_count else 0
        
        custom_attributes = {
            "schemaName": obj.get("schema_name", ""),
            "rowCount": row_count,
            "columnCount": column_count,
            "hasHeader": obj.get("has_header", True),
            "memoryUsage": obj.get("memory_usage", 0),
            "dataQualityScore": round(data_quality_score, 2),
            "sourceType": "Excel Sheet"
        }
        
        return {"attributes": attributes, "custom_attributes": custom_attributes}

class ExcelColumn:
    """Represents an Excel column entity in Atlan."""
    
    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform Excel column metadata into Atlan column entity attributes.
        
        Args:
            obj: Dictionary containing the raw Excel column metadata.
            
        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes.
        """
        qualified_name = build_atlas_qualified_name([
            obj.get("schema_name", ""),
            obj.get("table_name", ""),
            obj.get("column_name", "")
        ])
        
        attributes = {
            "name": obj.get("column_name", ""),
            "qualifiedName": qualified_name,
            "displayName": obj.get("column_name", "").replace("_", " ").title(),
            "dataType": obj.get("data_type", "VARCHAR"),
            "isNullable": obj.get("is_nullable", "YES") == "YES",
            "position": obj.get("ordinal_position", 0),
        }
        
        # Data quality assessment
        null_percentage = obj.get("null_percentage", 0)
        unique_percentage = obj.get("unique_percentage", 0)
        
        quality_level = "HIGH"
        if null_percentage > 50:
            quality_level = "LOW"
        elif null_percentage > 20:
            quality_level = "MEDIUM"
        
        custom_attributes = {
            "tableName": obj.get("table_name", ""),
            "schemaName": obj.get("schema_name", ""),
            "totalCount": obj.get("total_count", 0),
            "nullCount": obj.get("null_count", 0),
            "nullPercentage": null_percentage,
            "uniqueCount": obj.get("unique_count", 0),
            "uniquePercentage": unique_percentage,
            "qualityLevel": quality_level,
            "sourceType": "Excel Column"
        }
        
        # Add numeric-specific attributes
        if obj.get("min_value") is not None:
            custom_attributes.update({
                "minValue": obj.get("min_value"),
                "maxValue": obj.get("max_value"),
                "meanValue": obj.get("mean_value"),
            })
        
        # Add string-specific attributes
        if obj.get("avg_length") is not None:
            custom_attributes.update({
                "averageLength": obj.get("avg_length"),
                "maxLength": obj.get("max_length"),
                "minLength": obj.get("min_length"),
            })
        
        return {"attributes": attributes, "custom_attributes": custom_attributes}

class ExcelVisualization:
    """Represents Excel data visualizations in Atlan."""
    
    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform visualization metadata into Atlan entity attributes.
        
        Args:
            obj: Dictionary containing the visualization metadata.
            
        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes.
        """
        qualified_name = build_atlas_qualified_name([
            "visualizations",
            obj.get("title", "").replace(" ", "_").lower()
        ])
        
        attributes = {
            "name": obj.get("title", ""),
            "qualifiedName": qualified_name,
            "displayName": obj.get("title", ""),
        }
        
        custom_attributes = {
            "visualizationType": obj.get("type", ""),
            "dataSource": str(obj.get("data", {})),  # Convert to string for storage
            "createdDate": datetime.now().isoformat(),
            "sourceType": "Excel Visualization"
        }
        
        return {"attributes": attributes, "custom_attributes": custom_attributes}

class ExcelAtlasTransformer(AtlasTransformer):
    """
    Transformer class for converting Excel metadata to Atlan entities.
    Fixed to properly initialize with required parameters.
    """
    
    # Mapping of data types to Atlan entity classes
    ENTITY_TYPE_MAPPING = {
        "database": ExcelDatabase,
        "schema": ExcelSchema,
        "table": ExcelTable,
        "column": ExcelColumn,
        "visualization": ExcelVisualization,
    }
    
    def __init__(self, connector_name: str = "excel-sourcesense", tenant_id: str = "default"):
        """
        Initialize the Excel Atlas Transformer with required parameters.
        
        Args:
            connector_name: Name of the connector (default: "excel-sourcesense")
            tenant_id: Tenant ID for Atlan (default: "default")
        """
        super().__init__(connector_name=connector_name, tenant_id=tenant_id)
        logger.info(f"ExcelAtlasTransformer initialized with connector: {connector_name}, tenant: {tenant_id}")
    
    def transform(self, raw_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform raw Excel metadata into Atlan entities.
        
        Args:
            raw_metadata: Dictionary containing all extracted Excel metadata
            
        Returns:
            List[Dict[str, Any]]: List of transformed Atlan entities
        """
        transformed_entities = []
        
        try:
            # Transform database metadata
            if "database_info" in raw_metadata and raw_metadata["database_info"]:
                database_entity = self._transform_entity(
                    raw_metadata["database_info"], "database"
                )
                transformed_entities.append(database_entity)
            
            # Transform schema metadata
            if "schema_info" in raw_metadata and raw_metadata["schema_info"]:
                schema_entity = self._transform_entity(
                    raw_metadata["schema_info"], "schema"
                )
                transformed_entities.append(schema_entity)
            
            # Transform table metadata
            if "tables_info" in raw_metadata and raw_metadata["tables_info"]:
                for table_info in raw_metadata["tables_info"]:
                    table_entity = self._transform_entity(table_info, "table")
                    transformed_entities.append(table_entity)
            
            # Transform column metadata
            if "columns_info" in raw_metadata and raw_metadata["columns_info"]:
                for column_info in raw_metadata["columns_info"]:
                    column_entity = self._transform_entity(column_info, "column")
                    transformed_entities.append(column_entity)
            
            # Transform visualization metadata
            if "visualizations" in raw_metadata and raw_metadata["visualizations"]:
                for viz_info in raw_metadata["visualizations"]:
                    viz_entity = self._transform_entity(viz_info, "visualization")
                    transformed_entities.append(viz_entity)
            
            logger.info(f"Transformed {len(transformed_entities)} entities")
            return transformed_entities
            
        except Exception as e:
            logger.error(f"Error during transformation: {str(e)}")
            # Return empty list instead of raising to prevent app crash
            return []
    
    def _transform_entity(self, raw_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Transform a single entity from raw data to Atlan format.
        
        Args:
            raw_data: Raw metadata for the entity
            entity_type: Type of entity (database, schema, table, column, visualization)
            
        Returns:
            Dict[str, Any]: Transformed Atlan entity
        """
        try:
            entity_class = self.ENTITY_TYPE_MAPPING.get(entity_type)
            if not entity_class:
                logger.warning(f"Unknown entity type: {entity_type}")
                return {}
            
            transformed_data = entity_class.get_attributes(raw_data)
            
            # Add common entity metadata
            entity = {
                "typeName": f"Excel{entity_type.capitalize()}",
                "attributes": transformed_data.get("attributes", {}),
                "customAttributes": transformed_data.get("custom_attributes", {}),
                "status": "ACTIVE",
                "createdBy": "ExcelSourceSense",
                "updatedBy": "ExcelSourceSense",
                "createTime": int(datetime.now().timestamp() * 1000),  # Atlan expects milliseconds
                "updateTime": int(datetime.now().timestamp() * 1000),
            }
            
            return entity
            
        except Exception as e:
            logger.error(f"Error transforming {entity_type} entity: {str(e)}")
            return {}
