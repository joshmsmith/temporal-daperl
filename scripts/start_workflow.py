"""Start a DAPERL workflow."""

import asyncio
import argparse
import json
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from daperl.config.settings import settings
from daperl.workflows import DAPERLWorkflow
from daperl.core.models import DAPERLInput


async def main():
    """Start a DAPERL workflow."""
    parser = argparse.ArgumentParser(description="Start a DAPERL workflow")
    parser.add_argument("--domain", required=True, help="Domain for the workflow")
    parser.add_argument("--data", required=True, help="JSON data file or string")
    parser.add_argument("--workflow-id", help="Custom workflow ID")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve execution plan")
    
    args = parser.parse_args()
    
    # Load data
    try:
        # Try to load as file first
        with open(args.data, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        # Try to parse as JSON string
        data = json.loads(args.data)
    
    # Get Temporal configuration
    temporal_config = settings.get_temporal_config()
    
    # Connect to Temporal with Pydantic v2 data converter
    client = await Client.connect(
        temporal_config.host, 
        namespace=temporal_config.namespace,
        data_converter=pydantic_data_converter
    )
    
    # Create workflow input
    workflow_input = DAPERLInput(
        domain=args.domain,
        data=data,
        auto_approve=args.auto_approve
    )
    
    # Generate workflow ID if not provided
    workflow_id = args.workflow_id or f"daperl-{args.domain}-{asyncio.get_event_loop().time():.0f}"
    
    print(f"Starting DAPERL workflow")
    print(f"Domain: {args.domain}")
    print(f"Workflow ID: {workflow_id}")
    print(f"Auto-approve: {args.auto_approve}")
    
    # Start workflow
    handle = await client.start_workflow(
        DAPERLWorkflow.run,
        workflow_input,
        id=workflow_id,
        task_queue=temporal_config.task_queue,
    )
    
    print(f"\nWorkflow started successfully!")
    print(f"Workflow ID: {handle.id}")
    print(f"Run ID: {handle.result_run_id}")
    print(f"\nTo query status: python scripts/query_workflow.py --workflow-id {handle.id}")
    if not args.auto_approve:
        print(f"To approve plan: python scripts/approve_workflow.py --workflow-id {handle.id}")


if __name__ == "__main__":
    asyncio.run(main())
