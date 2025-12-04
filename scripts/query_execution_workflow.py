"""Query an Execution Agent Child Workflow status."""

import asyncio
import argparse
import json
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from daperl.config.settings import settings
from daperl.workflows.execution_workflow import ExecutionAgentWorkflow


async def main():
    """Query execution workflow status."""
    parser = argparse.ArgumentParser(description="Query Execution Agent Workflow status")
    parser.add_argument(
        "--workflow-id", 
        required=True, 
        help="Parent workflow ID (will append '-execution' automatically)"
    )
    parser.add_argument(
        "--show-actions", 
        action="store_true", 
        help="Show detailed action results"
    )
    parser.add_argument(
        "--watch", 
        action="store_true", 
        help="Watch execution progress in real-time"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=2, 
        help="Watch interval in seconds (default: 2)"
    )
    
    args = parser.parse_args()
    
    # Get Temporal configuration
    temporal_config = settings.get_temporal_config()
    
    # Connect to Temporal with Pydantic v2 data converter
    client = await Client.connect(
        temporal_config.host, 
        namespace=temporal_config.namespace,
        data_converter=pydantic_data_converter
    )
    
    # Get execution workflow handle (child workflow ID)
    execution_workflow_id = f"{args.workflow_id}-execution"
    handle = client.get_workflow_handle(execution_workflow_id)
    
    if args.watch:
        # Watch mode: continuously query until completed
        print(f"Watching Execution Workflow: {execution_workflow_id}")
        print("=" * 60)
        
        previous_completed = -1
        
        while True:
            try:
                # Query execution status
                status = await handle.query(ExecutionAgentWorkflow.get_execution_status)
                
                # Only print if progress changed
                if status['completed'] != previous_completed:
                    print(f"\rProgress: {status['completed']}/{status['total']} actions | "
                          f"✓ {status['success_count']} succeeded | "
                          f"✗ {status['failure_count']} failed | "
                          f"Status: {status['status']}", end="")
                    previous_completed = status['completed']
                
                # Check if completed
                if status['status'] == 'completed':
                    print("\n\n✓ Execution completed!")
                    
                    # Show final summary
                    summary = await handle.query(ExecutionAgentWorkflow.get_execution_summary)
                    print(f"\nFinal Summary:")
                    print(f"  Total Executed: {summary['total_executed']}")
                    print(f"  Successes: {summary['success_count']}")
                    print(f"  Failures: {summary['failure_count']}")
                    
                    if args.show_actions:
                        actions = await handle.query(ExecutionAgentWorkflow.get_executed_actions)
                        print(f"\n=== Action Details ===")
                        for i, action in enumerate(actions, 1):
                            status_icon = "✓" if action['success'] else "✗"
                            print(f"  {i}. {status_icon} {action['action_id']}: {action['message']}")
                            if action.get('error'):
                                print(f"     Error: {action['error']}")
                    break
                
                # Wait before next query
                await asyncio.sleep(args.interval)
                
            except KeyboardInterrupt:
                print("\n\nWatch interrupted by user")
                break
            except Exception as e:
                print(f"\nError querying workflow: {e}")
                break
    
    else:
        # Single query mode
        print(f"Execution Workflow ID: {execution_workflow_id}")
        print("=" * 60)
        
        # Get execution status
        status = await handle.query(ExecutionAgentWorkflow.get_execution_status)
        print(f"\n=== Execution Status ===")
        print(f"Status: {status['status']}")
        print(f"Progress: {status['completed']}/{status['total']} actions")
        print(f"  Successes: {status['success_count']}")
        print(f"  Failures: {status['failure_count']}")
        
        # Get summary
        summary = await handle.query(ExecutionAgentWorkflow.get_execution_summary)
        print(f"\n=== Summary ===")
        print(f"Total Executed: {summary['total_executed']}")
        print(f"Success Rate: {summary['success_count']}/{summary['total_executed']} "
              f"({100 * summary['success_count'] / summary['total_executed']:.1f}%)" 
              if summary['total_executed'] > 0 else "N/A")
        
        # Show detailed actions if requested
        if args.show_actions:
            actions = await handle.query(ExecutionAgentWorkflow.get_executed_actions)
            print(f"\n=== Action Details ===")
            if actions:
                for i, action in enumerate(actions, 1):
                    status_icon = "✓" if action['success'] else "✗"
                    print(f"\n{i}. {status_icon} Action ID: {action['action_id']}")
                    print(f"   Message: {action['message']}")
                    if action.get('error'):
                        print(f"   Error: {action['error']}")
                    if action.get('data'):
                        print(f"   Data: {json.dumps(action['data'], indent=6)}")
            else:
                print("No actions executed yet")


if __name__ == "__main__":
    asyncio.run(main())
