"""Run a Temporal worker for DAPERL workflows."""

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from daperl.config.settings import settings
from daperl.workflows import DAPERLWorkflow
from daperl.activities import (
    run_detection_agent,
    run_analysis_agent,
    run_planning_agent,
    run_execution_agent,
    run_reporting_agent,
    run_learning_agent,
)


async def main():
    """Run the DAPERL worker."""
    # Get Temporal configuration
    temporal_config = settings.get_temporal_config()
    
    # Connect to Temporal with Pydantic v2 data converter
    client = await Client.connect(
        temporal_config.host, 
        namespace=temporal_config.namespace,
        data_converter=pydantic_data_converter
    )
    
    print(f"Connected to Temporal at {temporal_config.host}")
    print(f"Namespace: {temporal_config.namespace}")
    print(f"Task Queue: {temporal_config.task_queue}")
    
    # Configure workflow sandbox to allow Pydantic imports
    restrictions = SandboxRestrictions.default
    restrictions = restrictions.with_passthrough_modules(
        "pydantic",
        "pydantic_core",
        "pydantic_core._pydantic_core",
    )
    
    # Create and run worker
    worker = Worker(
        client,
        task_queue=temporal_config.task_queue,
        workflows=[DAPERLWorkflow],
        activities=[
            run_detection_agent,
            run_analysis_agent,
            run_planning_agent,
            run_execution_agent,
            run_reporting_agent,
            run_learning_agent,
        ],
        workflow_runner=SandboxedWorkflowRunner(restrictions=restrictions),
    )
    
    print("\nWorker started. Polling for tasks...")
    print("Press Ctrl+C to stop")
    
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
