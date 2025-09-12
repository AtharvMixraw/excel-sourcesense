"""
This file contains the workflow definition for the Excel metadata extraction application.
Orchestrates Excel file analysis and metadata extraction activities.
"""
import asyncio
from datetime import timedelta
from typing import Any, Callable, Dict, List
from app.activities import ExcelMetadataExtractionActivities
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.workflows.metadata_extraction.sql import (
    BaseSQLMetadataExtractionWorkflow,
)
from temporalio import workflow
from temporalio.common import RetryPolicy

logger = get_logger(__name__)
workflow.logger = logger
metrics = get_metrics()
traces = get_traces()

@workflow.defn
class ExcelMetadataExtractionWorkflow(BaseSQLMetadataExtractionWorkflow):
    
    @observability(logger=logger, metrics=metrics, traces=traces)
    @workflow.run
    async def run(self, workflow_config: Dict[str, Any]):
        """
        Run the Excel metadata extraction workflow.
        
        Args:
            workflow_config: The workflow configuration containing file path and options
        """
        activities_instance = ExcelMetadataExtractionActivities()
        
        # Get workflow arguments 
        workflow_args: Dict[str, Any] = await workflow.execute_activity_method(
            activities_instance.get_workflow_args,
            workflow_config,
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            backoff_coefficient=2,
        )
        
        # Pre-flight checks
        await workflow.execute_activity_method(
            activities_instance.preflight_check,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )
        
        # Sequential extraction of metadata (order matters for dependencies)
        logger.info("Starting database metadata extraction")
        await workflow.execute_activity_method(
            activities_instance.fetch_databases,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )
        
        logger.info("Starting schema metadata extraction")
        await workflow.execute_activity_method(
            activities_instance.fetch_schemas,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )
        
        logger.info("Starting table metadata extraction")
        await workflow.execute_activity_method(
            activities_instance.fetch_tables,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )
        
        logger.info("Starting column metadata extraction")
        await workflow.execute_activity_method(
            activities_instance.fetch_columns,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )
        
        # Generate visualizations
        logger.info("Starting visualization generation")
        await workflow.execute_activity_method(
            activities_instance.generate_visualizations,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )
        
        # Transform all extracted metadata to Atlan format
        logger.info("Starting metadata transformation")
        await workflow.execute_activity_method(
            activities_instance.transform_data,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )
        
        logger.info("Excel metadata extraction workflow completed successfully")
    
    @staticmethod
    def get_activities(
        activities: ExcelMetadataExtractionActivities,
    ) -> List[Callable[..., Any]]:
        """
        Get the list of activities for the Excel metadata extraction workflow.
        
        Args:
            activities: The activities instance containing the workflow activities.
            
        Returns:
            List[Callable[..., Any]]: A list of activity methods that can be executed by the workflow.
        """
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
