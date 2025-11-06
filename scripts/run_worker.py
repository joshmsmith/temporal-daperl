"""Run a Temporal worker for DAPERL workflows."""

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

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
    
    # Connect to Temporal
    client = await Client.connect(temporal_config.host, namespace=temporal_config.namespace)
    
    print(f"Connected to Temporal at {temporal_config.host}")
    print(f"Namespace: {temporal_config.namespace}")
    print(f"Task Queue: {temporal_config.task_queue}")
    
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
    )
    
    print("\nWorker started. Polling for tasks...")
    print("Press Ctrl+C to stop")
    
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
