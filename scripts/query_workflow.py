"""Query a DAPERL workflow status."""

import asyncio
import argparse
import json
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from daperl.config.settings import settings
from daperl.workflows import DAPERLWorkflow


async def main():
    """Query workflow status."""
    parser = argparse.ArgumentParser(description="Query DAPERL workflow status")
    parser.add_argument("--workflow-id", required=True, help="Workflow ID to query")
    parser.add_argument("--show-results", action="store_true", help="Show full results")
    
    args = parser.parse_args()
    
    # Get Temporal configuration
    temporal_config = settings.get_temporal_config()
    
    # Connect to Temporal with Pydantic v2 data converter
    client = await Client.connect(
        temporal_config.host, 
        namespace=temporal_config.namespace,
        data_converter=pydantic_data_converter
    )
    
    # Get workflow handle
    handle = client.get_workflow_handle(args.workflow_id)
    
    # Query status
    status = await handle.query(DAPERLWorkflow.get_status)
    
    print(f"Workflow ID: {args.workflow_id}")
    print(f"Status: {status['status']}")
    print(f"\nPhase Completion:")
    print(f"  Detection: {'✓' if status['detection_complete'] else '✗'}")
    print(f"  Analysis: {'✓' if status['analysis_complete'] else '✗'}")
    print(f"  Planning: {'✓' if status['planning_complete'] else '✗'}")
    print(f"  Execution: {'✓' if status['execution_complete'] else '✗'}")
    print(f"  Reporting: {'✓' if status['reporting_complete'] else '✗'}")
    print(f"  Learning: {'✓' if status['learning_complete'] else '✗'}")
    print(f"\nPlan Approved: {status['plan_approved']}")
    
    # Show plan if available
    plan = await handle.query(DAPERLWorkflow.get_plan)
    if plan:
        print(f"\n=== Execution Plan ===")
        print(f"Actions: {len(plan['actions'])}")
        for i, action in enumerate(plan['actions'], 1):
            print(f"  {i}. {action['action_type']}: {action['description']}")
    
    # Show full results if requested
    if args.show_results:
        results = await handle.query(DAPERLWorkflow.get_results)
        print(f"\n=== Full Results ===")
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
