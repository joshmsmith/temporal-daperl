"""
Simple expense report processing example using DAPERL.

This example demonstrates how to use the DAPERL framework to automatically
process expense reports, detecting issues, analyzing them, planning fixes,
executing actions, reporting results, and learning from the process.
"""

import argparse
import asyncio
import json
from pathlib import Path
from temporalio.client import Client

from daperl.workflows import DAPERLWorkflow
from daperl.core.models import DAPERLInput
from daperl.config.settings import settings


async def main():
    """Run the expense report processing example."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="DAPERL Expense Report Processing Example")
    parser.add_argument(
        "--auto-approve", 
        action="store_true",
        help="Auto-approve actions without human intervention (default: False)"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("DAPERL Expense Report Processing Example")
    print("=" * 60)
    
    # Load expense report data
    data_path = Path(__file__).parent / "data" / "expense_reports.json"
    with open(data_path, 'r') as f:
        expense_data = json.load(f)
    
    print(f"\nLoaded {len(expense_data['reports'])} expense reports")
    print("\nReports:")
    for report in expense_data['reports']:
        print(f"  - {report['report_id']}: {report['employee_name']} (${report.get('total', 'TBD')})")
    
    # Configure for expense report domain
    config = {
        "detection_instructions": """
            Check for:
            - Missing receipts (required for expenses over $25)
            - Expenses exceeding policy limits
            - Duplicate submissions
            - Missing calculations (e.g., mileage amounts)
            - Policy violations
        """,
        "available_actions": [
            "request_receipt",
            "calculate_mileage",
            "flag_for_manual_review",
            "auto_approve",
            "send_notification"
        ]
    }
    
    # Get Temporal configuration
    temporal_config = settings.get_temporal_config()
    
    try:
        # Connect to Temporal
        print(f"\nConnecting to Temporal at {temporal_config.host}...")
        client = await Client.connect(temporal_config.host, namespace=temporal_config.namespace)
        print("✓ Connected to Temporal")
        
        # Create workflow input
        workflow_input = DAPERLInput(
            domain="expense-reports",
            data=expense_data,
            config=config,
            auto_approve=args.auto_approve,
            metadata={"example": "expense_reports"}
        )
        
        # Generate workflow ID
        workflow_id = f"expense-reports-demo"
        
        print(f"\nStarting DAPERL workflow...")
        print(f"Workflow ID: {workflow_id}")
        print(f"Auto-approve: {args.auto_approve}")
        
        # Start workflow
        handle = await client.start_workflow(
            DAPERLWorkflow.run,
            workflow_input,
            id=workflow_id,
            task_queue=temporal_config.task_queue,
        )
        
        print("\n✓ Workflow started!")
        print(f"\nProcessing expense reports through DAPERL cycle...")
        print("  1. Detection  - Finding problems...")
        print("  2. Analysis   - Analyzing root causes...")
        print("  3. Planning   - Creating action plan...")
        print("  4. Execution  - Executing actions...")
        print("  5. Reporting  - Generating report...")
        print("  6. Learning   - Extracting insights...")
        
        # Wait for result
        print("\nWaiting for workflow to complete...")
        result = await handle.result()
        
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETED!")
        print("=" * 60)
        
        # Display results
        print(f"\nStatus: {result.status.value}")
        print(f"Summary: {result.summary}")
        
        if result.detection_result:
            print(f"\n📋 DETECTION:")
            print(f"   Problems found: {len(result.detection_result.problems)}")
            for i, problem in enumerate(result.detection_result.problems, 1):
                print(f"   {i}. [{problem.severity}] {problem.description}")
        
        if result.analysis_result:
            print(f"\n🔍 ANALYSIS:")
            print(f"   Root causes: {len(result.analysis_result.root_causes)}")
            for cause in result.analysis_result.root_causes:
                print(f"   - {cause}")
        
        if result.planning_result and result.planning_result.plan:
            print(f"\n📝 PLAN:")
            print(f"   Actions: {len(result.planning_result.plan.actions)}")
            for action in result.planning_result.plan.actions:
                print(f"   - {action.action_type}: {action.description}")
        
        if result.execution_result:
            print(f"\n⚙️  EXECUTION:")
            print(f"   Success: {result.execution_result.success_count}/{len(result.execution_result.actions_executed)}")
            print(f"   Failed: {result.execution_result.failure_count}")
        
        if result.reporting_result:
            print(f"\n📊 REPORT:")
            print(f"   Metrics: {result.reporting_result.metrics}")
        
        if result.learning_result:
            print(f"\n🧠 LEARNING:")
            print(f"   Insights generated: {len(result.learning_result.insights)}")
            print(f"   Patterns found: {result.learning_result.patterns_found}")
            for insight in result.learning_result.insights:
                print(f"   - {insight.description}")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)
        
        print(f"\nTo view in Temporal UI:")
        print(f"  http://localhost:8233/namespaces/{temporal_config.namespace}/workflows/{workflow_id}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Temporal server is running: temporal server start-dev")
        print("  2. Worker is running: poetry run python scripts/run_worker.py")
        print("  3. LLM API keys are configured in .env")
        raise


if __name__ == "__main__":
    asyncio.run(main())
