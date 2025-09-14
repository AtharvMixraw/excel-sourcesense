"""
This file contains the workflow definition for the Excel metadata extraction application.
Orchestrates Excel file analysis and metadata extraction activities.
"""
from datetime import timedelta
from typing import Any, Callable, Dict, List
from app.activities import ExcelMetadataExtractionActivities
from application_sdk.workflows.metadata_extraction.sql import (
    BaseSQLMetadataExtractionWorkflow,
)
from temporalio import workflow
from temporalio.common import RetryPolicy

@workflow.defn(name="excel_sourcesense_workflow")
class ExcelMetadataExtractionWorkflow(BaseSQLMetadataExtractionWorkflow):
    
    @workflow.run
    async def run(self, workflow_config: Dict[str, Any]):
        """
        Run the Excel metadata extraction workflow.
        
        Args:
            workflow_config: The workflow configuration containing file path and options
        """
        # Only use workflow.logger - no external loggers
        workflow.logger.info("Starting Excel metadata extraction workflow")
        
        activities_instance = ExcelMetadataExtractionActivities()
        
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            backoff_coefficient=2,
        )
        
        # Sequential execution - all non-deterministic code must be in activities
        try:
            # Get workflow arguments (moved to activity to avoid issues)
            workflow_args = await workflow.execute_activity(
                activities_instance.get_workflow_args,
                workflow_config,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # Pre-flight checks
            await workflow.execute_activity(
                activities_instance.preflight_check,
                workflow_args,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=2),
            )
            
            # Sequential extraction of metadata
            workflow.logger.info("Starting database metadata extraction")
            await workflow.execute_activity(
                activities_instance.fetch_databases,
                workflow_args,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=5),
            )
            
            workflow.logger.info("Starting schema metadata extraction")
            await workflow.execute_activity(
                activities_instance.fetch_schemas,
                workflow_args,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=2),
            )
            
            workflow.logger.info("Starting table metadata extraction")
            await workflow.execute_activity(
                activities_instance.fetch_tables,
                workflow_args,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=5),
            )
            
            workflow.logger.info("Starting column metadata extraction")
            await workflow.execute_activity(
                activities_instance.fetch_columns,
                workflow_args,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=5),
            )
            
            # Generate visualizations
            workflow.logger.info("Starting visualization generation")
            await workflow.execute_activity(
                activities_instance.generate_visualizations,
                workflow_args,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=3),
            )
            
            # Transform all extracted metadata to Atlan format
            workflow.logger.info("Starting metadata transformation")
            await workflow.execute_activity(
                activities_instance.transform_data,
                workflow_args,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=2),
            )
            
            workflow.logger.info("Excel metadata extraction workflow completed successfully")
            return {"status": "completed", "workflow_id": workflow_config.get("workflow_id")}
            
        except Exception as e:
            workflow.logger.error(f"Workflow failed: {str(e)}")
            raise
    
    @staticmethod
    def get_activities(
        activities: ExcelMetadataExtractionActivities,
    ) -> List[Callable[..., Any]]:
        """Get the list of activities for the Excel metadata extraction workflow."""
        return [
            activities.get_workflow_args,
            activities.preflight_check,
            activities.fetch_databases,
            activities.fetch_schemas,
            activities.fetch_tables,
            activities.fetch_columns,
            activities.generate_visualizations,
            activities.transform_data,
        ]
