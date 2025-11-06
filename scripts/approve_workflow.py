"""Approve an execution plan for a DAPERL workflow."""

import asyncio
import argparse
from temporalio.client import Client

from daperl.config.settings import settings
from daperl.workflows import DAPERLWorkflow


async def main():
    """Approve workflow execution plan."""
    parser = argparse.ArgumentParser(description="Approve DAPERL workflow execution plan")
    parser.add_argument("--workflow-id", required=True, help="Workflow ID to approve")
    
    args = parser.parse_args()
    
    # Get Temporal configuration
    temporal_config = settings.get_temporal_config()
    
    # Connect to Temporal
    client = await Client.connect(temporal_config.host, namespace=temporal_config.namespace)
    
    # Get workflow handle
    handle = client.get_workflow_handle(args.workflow_id)
    
    # Get current status
    status = await handle.query(DAPERLWorkflow.get_status)
    
    print(f"Workflow ID: {args.workflow_id}")
    print(f"Current Status: {status['status']}")
    
    if status['status'] != 'PENDING_APPROVAL':
        print(f"\nWorkflow is not waiting for approval (status: {status['status']})")
        return
    
    # Show plan
    plan = await handle.query(DAPERLWorkflow.get_plan)
    if plan:
        print(f"\n=== Execution Plan ===")
        print(f"Actions: {len(plan['actions'])}")
        print(f"Risk Level: {plan.get('risk_level', 'unknown')}")
        print(f"\nActions to execute:")
        for i, action in enumerate(plan['actions'], 1):
            print(f"  {i}. [{action['action_type']}] {action['description']}")
            print(f"     Target: {action['target']}")
            print(f"     Confidence: {action['confidence']}")
        
        # Confirm approval
        print(f"\n")
        confirm = input("Approve this plan? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y']:
            # Send approval signal
            await handle.signal(DAPERLWorkflow.approve_plan)
            print("\n✓ Plan approved! Workflow will proceed with execution.")
        else:
            print("\n✗ Plan not approved. Workflow will remain pending.")
    else:
        print("\nNo plan available to approve.")


if __name__ == "__main__":
    asyncio.run(main())
