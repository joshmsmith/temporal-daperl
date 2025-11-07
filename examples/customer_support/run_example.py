#!/usr/bin/env python3
"""
Customer Support Domain Example using DAPERL.

This example demonstrates how to use the DAPERL framework for intelligent 
customer support automation, detecting issues, analyzing customer context,
planning response strategies, executing actions, and learning from outcomes.
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
    """Run the customer support processing example."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="DAPERL Customer Support Automation Example")
    parser.add_argument(
        "--auto-approve", 
        action="store_true",
        help="Auto-approve actions without human intervention (default: False)"
    )
    args = parser.parse_args()
    
    print("=" * 65)
    print("DAPERL Customer Support Automation Example")
    print("=" * 65)
    
    # Load customer support data
    data_path = Path(__file__).parent / "data.json"
    with open(data_path, 'r') as f:
        all_data = json.load(f)
        # Extract the nested customer support data
        support_data = all_data.get("customer_support_data", all_data)
    
    print(f"\nLoaded customer support data:")
    print(f"  📊 {len(support_data.get('tickets', []))} support tickets")
    print(f"  👥 {len(support_data.get('customers', []))} customer profiles")
    print(f"  💬 {len(support_data.get('forum_posts', []))} forum posts")
    print(f"  📦 {len(support_data.get('products', []))} product definitions")
    print(f"  📚 {len(support_data.get('knowledge_base', []))} knowledge base articles")
    
    # Show sample tickets
    tickets = support_data.get('tickets', [])
    if tickets:
        print(f"\nSample tickets:")
        for ticket in tickets[:3]:
            print(f"  - {ticket.get('ticket_id', 'N/A')}: {ticket.get('subject', 'No subject')[:50]}...")
            print(f"    Priority: {ticket.get('priority', 'N/A')} | Status: {ticket.get('status', 'N/A')}")
    
    # Configure for customer support domain
    config = {
        "detection_instructions": """
            Detect customer support issues including:
            - SLA violations (response and resolution deadlines)
            - Customer sentiment problems (frustrated, angry customers)
            - Escalation patterns (repeat issues, high-value customer problems)
            - Knowledge base gaps (issues without documented solutions)
            - Account health risks (churn indicators, satisfaction drops)
        """,
        "analysis_instructions": """
            Analyze customer support context:
            - Customer account type, value, and history
            - Churn risk assessment based on issue patterns
            - Issue complexity and required expertise
            - Customer satisfaction correlation factors
            - Support tier optimization opportunities
        """,
        "planning_instructions": """
            Plan intelligent customer support responses:
            - Response strategy (white glove, expedited, standard)
            - Escalation workflows to appropriate specialists
            - Account management interventions
            - Follow-up scheduling and satisfaction tracking
            - Resource allocation optimization
        """,
        "available_actions": [
            "update_ticket_status",
            "send_customer_response", 
            "update_customer_account",
            "search_knowledge_base",
            "escalate_to_specialist",
            "notify_account_manager",
            "create_follow_up_task"
        ],
        "domain_specific_config": {
            "sla_monitoring": True,
            "sentiment_analysis": True,
            "churn_prediction": True,
            "auto_escalation": True,
            "knowledge_base_integration": True
        }
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
            domain="customer-support",
            data=support_data,
            config=config,
            auto_approve=args.auto_approve,
            metadata={"example": "customer_support"}
        )
        
        # Generate workflow ID
        workflow_id = f"customer-support-demo"
        
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
        print(f"\nProcessing customer support through DAPERL cycle...")
        print("  1. Detection  - Identifying issues and patterns...")
        print("  2. Analysis   - Customer context and risk assessment...")
        print("  3. Planning   - Response strategies and workflows...")
        print("  4. Execution  - Ticket updates and communications...")
        print("  5. Reporting  - Metrics and satisfaction tracking...")
        print("  6. Learning   - Insights for continuous improvement...")
        
        # Wait for result
        print("\nWaiting for workflow to complete...")
        result = await handle.result()
        
        print("\n" + "=" * 65)
        print("WORKFLOW COMPLETED!")
        print("=" * 65)
        
        # Display results
        print(f"\nStatus: {result.status.value}")
        print(f"Summary: {result.summary}")
        
        if result.detection_result:
            print(f"\n📡 DETECTION:")
            print(f"   Issues found: {len(result.detection_result.problems)}")
            for i, problem in enumerate(result.detection_result.problems, 1):
                print(f"   {i}. [{problem.severity}] {problem.description}")
        
        if result.analysis_result:
            print(f"\n🔍 ANALYSIS:")
            print(f"   Root causes: {len(result.analysis_result.root_causes)}")
            for cause in result.analysis_result.root_causes:
                print(f"   - {cause}")
        
        if result.planning_result and result.planning_result.plan:
            print(f"\n� PLANNING:")
            print(f"   Actions planned: {len(result.planning_result.plan.actions)}")
            for action in result.planning_result.plan.actions:
                print(f"   - {action.action_type}: {action.description}")
        
        if result.execution_result:
            print(f"\n⚙️  EXECUTION:")
            print(f"   Success: {result.execution_result.success_count}/{len(result.execution_result.actions_executed)}")
            print(f"   Failed: {result.execution_result.failure_count}")
            
            # Show some execution details
            for action in result.execution_result.actions_executed[:3]:
                status = "✓" if action.success else "✗"
                print(f"   {status} {action.action_type}: {action.result[:60]}...")
        
        if result.reporting_result:
            print(f"\n📊 REPORTING:")
            print(f"   Metrics: {result.reporting_result.metrics}")
            
            # Show key customer support metrics
            metrics = result.reporting_result.metrics
            if isinstance(metrics, dict):
                if 'tickets_processed' in metrics:
                    print(f"   Tickets processed: {metrics['tickets_processed']}")
                if 'sla_violations' in metrics:
                    print(f"   SLA violations: {metrics['sla_violations']}")
                if 'customer_satisfaction' in metrics:
                    print(f"   Avg satisfaction: {metrics['customer_satisfaction']}")
                if 'escalations_created' in metrics:
                    print(f"   Escalations: {metrics['escalations_created']}")
        
        if result.learning_result:
            print(f"\n🧠 LEARNING:")
            print(f"   Insights generated: {len(result.learning_result.insights)}")
            print(f"   Patterns found: {result.learning_result.patterns_found}")
            for insight in result.learning_result.insights[:3]:
                print(f"   - {insight.description}")
        
        print("\n" + "=" * 65)
        print("Customer Support Example Completed Successfully!")
        print("=" * 65)
        
        print(f"\n🎯 BUSINESS VALUE DELIVERED:")
        print("• Automated issue detection and prioritization")
        print("• Intelligent customer context analysis") 
        print("• Dynamic response strategy optimization")
        print("• Proactive escalation and account management")
        print("• Continuous learning and improvement")
        
        print(f"\n� NEXT STEPS:")
        print("• Review execution results and customer feedback")
        print("• Analyze patterns for process optimization")
        print("• Update knowledge base with new insights")
        print("• Refine escalation rules and response strategies")
        
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