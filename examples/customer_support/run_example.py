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
import datetime
from pathlib import Path
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from daperl.workflows import DAPERLWorkflow
from daperl.core.models import DAPERLInput
from daperl.config.settings import settings


def load_customer_support_data() -> dict:
    """Load and validate customer support data from JSON file."""
    data_path = Path(__file__).parent / "data.json"
    
    try:
        with open(data_path, 'r') as f:
            all_data = json.load(f)
            # Extract the nested customer support data
            support_data = all_data.get("customer_support_data", all_data)
            
        # Validate required data structures
        required_keys = ['tickets', 'customers', 'knowledge_base']
        for key in required_keys:
            if key not in support_data:
                support_data[key] = []
                
        return support_data
        
    except FileNotFoundError:
        print(f"❌ Error: Data file not found at {data_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in data file: {e}")
        raise


async def main():
    """Run the customer support processing example using DAPER framework."""
    
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
    print("📁 Loading customer support data...")
    try:
        support_data = load_customer_support_data()
        print("✅ Data loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Display data summary
    print(f"\n📊 Data Summary:")
    print(f"  🎫 {len(support_data.get('tickets', []))} support tickets")
    print(f"  👥 {len(support_data.get('customers', []))} customer profiles")
    print(f"  💬 {len(support_data.get('forum_posts', []))} forum posts")
    print(f"  📦 {len(support_data.get('products', []))} product definitions")
    print(f"  📚 {len(support_data.get('knowledge_base', []))} knowledge base articles")
    
    # Enhanced data preparation for DAPER workflow
    print(f"\n🔧 Preparing data for DAPER workflow...")
    
    # Add metadata and context to support data
    enhanced_data = {
        **support_data,
        "workflow_metadata": {
            "processing_timestamp": json.dumps(datetime.datetime.now().isoformat()),
            "total_tickets": len(support_data.get('tickets', [])),
            "auto_approve_enabled": args.auto_approve
        }
    }
    
    # Configure for customer support domain
    config = {
        "detection_instructions": """
            Analyze customer support data and detect critical issues:
            
            SLA VIOLATIONS:
            - Response time SLA breaches (check against ticket priority and creation time)
            - Resolution time SLA violations based on customer tier and issue complexity
            - Escalation timeouts where tickets haven't been properly escalated
            - Follow-up missed deadlines for customer communications
            
            CUSTOMER SENTIMENT ISSUES:
            - Frustrated, angry, or disappointed customer language in tickets
            - Declining satisfaction scores or negative feedback patterns
            - Escalation language indicating customer dissatisfaction
            - Social media mentions or forum posts expressing problems
            
            ACCOUNT HEALTH RISKS:
            - High-value customers with unresolved issues
            - Repeat issues indicating systemic problems
            - Churn risk indicators (cancellation requests, downgrade attempts)
            - Support tier mismatches (enterprise customers getting basic support)
            
            KNOWLEDGE GAPS:
            - Common issues without documented solutions
            - Complex technical problems requiring repeated escalation
            - Customer confusion about product features or capabilities
            - Missing self-service resources for frequent questions
            
            OPERATIONAL ISSUES:
            - Tickets stuck in queues without assignment
            - High-priority issues assigned to junior staff
            - Resource bottlenecks in specialized support areas
            - Knowledge base outdated or incorrect information
            
            Classify severity based on customer impact, revenue risk, and operational efficiency.
        """,
        "analysis_instructions": """
            Conduct deep customer context analysis to understand root causes:
            
            CUSTOMER PROFILE ANALYSIS:
            - Account value, growth trajectory, and strategic importance
            - Historical support patterns and satisfaction trends
            - Product usage patterns and adoption challenges
            - Decision-maker involvement and escalation preferences
            
            CHURN RISK ASSESSMENT:
            - Recent support issue frequency and severity trends
            - Satisfaction score declines and negative feedback patterns
            - Product usage changes or feature abandonment
            - Contract renewal timeline and competitive risk factors
            
            TECHNICAL COMPLEXITY EVALUATION:
            - Issue technical depth and required expertise level
            - Integration complexity with customer's environment
            - Documentation quality and availability for the issue
            - Estimated resolution effort and resource requirements
            
            ORGANIZATIONAL IMPACT:
            - Customer's business criticality of the affected functionality
            - Number of end users impacted by the issue
            - Potential revenue or productivity impact for customer
            - Regulatory or compliance implications of the issue
            
            SUPPORT OPTIMIZATION:
            - Appropriate support tier and resource allocation
            - Escalation path effectiveness and timing
            - Knowledge sharing opportunities across the team
            - Process improvements to prevent similar issues
            
            Provide actionable insights for improving customer experience and preventing churn.
        """,
        "planning_instructions": """
            Create intelligent customer support response strategies:
            
            RESPONSE STRATEGY SELECTION:
            - White-glove service for enterprise customers and churn risks
            - Expedited handling for SLA violations and high-severity issues
            - Standard process for routine issues with clear solutions
            - Proactive outreach for customers showing stress signals
            
            ESCALATION WORKFLOW DESIGN:
            - Route technical issues to appropriate specialists immediately
            - Involve account managers for high-value customer issues
            - Escalate to product team for feature requests or bugs
            - Engage executive team for enterprise account risks
            
            COMMUNICATION PLANNING:
            - Personalized response templates based on customer sentiment
            - Proactive status updates for complex issues
            - Educational content to prevent future similar issues
            - Follow-up schedules to ensure satisfaction
            
            ACCOUNT MANAGEMENT ACTIONS:
            - Health score adjustments based on support interactions
            - Support tier upgrades for customers with complex needs
            - Success manager assignment for at-risk accounts
            - Product training recommendations for struggling users
            
            KNOWLEDGE OPTIMIZATION:
            - Document solutions for novel issues in knowledge base
            - Update existing articles based on customer confusion
            - Create self-service resources for common questions
            - Develop troubleshooting guides for complex scenarios
            
            RESOURCE ALLOCATION:
            - Prioritize specialist time for highest-impact issues
            - Balance workload across support team members
            - Schedule follow-ups and proactive check-ins
            - Plan capacity for anticipated support volume
            
            Focus on maximizing customer satisfaction while optimizing operational efficiency.
        """,
        "reporting_instructions": """
            Generate comprehensive customer support performance analytics:
            
            SLA PERFORMANCE:
            - Response and resolution time compliance by priority and tier
            - Escalation effectiveness and timing analysis
            - Customer satisfaction correlation with SLA adherence
            - Trend analysis of SLA performance over time
            
            CUSTOMER HEALTH METRICS:
            - Account health score distributions and trends
            - Churn risk indicators and early warning signals
            - Customer satisfaction scores and feedback sentiment
            - Support tier effectiveness and optimization opportunities
            
            OPERATIONAL EFFICIENCY:
            - Agent productivity and issue resolution rates
            - Knowledge base utilization and gap identification
            - First-contact resolution rates and quality metrics
            - Resource allocation effectiveness across support areas
            
            BUSINESS IMPACT ANALYSIS:
            - Support cost per customer by tier and issue type
            - Customer lifetime value impact from support quality
            - Product improvement opportunities from support feedback
            - Competitive intelligence from customer issues
            
            QUALITY METRICS:
            - Issue resolution accuracy and customer validation
            - Knowledge base article effectiveness and usage
            - Customer education success and adoption rates
            - Proactive support impact on issue prevention
            
            Provide actionable insights for strategic decision-making and operational improvements.
        """,
        "learning_instructions": """
            Extract strategic insights for continuous customer support improvement:
            
            PATTERN DISCOVERY:
            - Identify issue patterns predicting customer churn
            - Recognize seasonal support volume and type variations
            - Detect customer success patterns and replication opportunities
            - Spot product feature gaps causing repeated support issues
            
            PREDICTIVE INTELLIGENCE:
            - Develop early warning systems for account health risks
            - Predict support volume and resource needs
            - Forecast customer satisfaction trends and interventions needed
            - Anticipate product adoption challenges and support requirements
            
            PROCESS OPTIMIZATION:
            - Learn which response strategies maximize customer satisfaction
            - Identify optimal escalation timing and specialist involvement
            - Understand communication preferences by customer segment
            - Recognize when proactive outreach prevents issues
            
            KNOWLEDGE ENHANCEMENT:
            - Capture tribal knowledge from successful issue resolutions
            - Identify knowledge base gaps causing customer confusion
            - Build predictive models for issue complexity and resolution time
            - Create customer education strategies based on common misunderstandings
            
            STRATEGIC INSIGHTS:
            - Understand support investment ROI on customer retention
            - Identify support-driven upsell and expansion opportunities
            - Recognize competitive threats and positioning opportunities
            - Develop customer success playbooks for different segments
            
            Use insights to continuously improve support processes and customer outcomes.
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
        # Connect to Temporal with Pydantic v2 data converter
        print(f"\nConnecting to Temporal at {temporal_config.host}...")
        client = await Client.connect(
            temporal_config.host, 
            namespace=temporal_config.namespace,
            data_converter=pydantic_data_converter
        )
        print("✓ Connected to Temporal")
        
        # Create workflow input with enhanced data
        workflow_input = DAPERLInput(
            domain="customer-support",
            data=enhanced_data,
            config=config,
            auto_approve=args.auto_approve,
            metadata={
                "example": "customer_support",
                "processing_mode": "auto" if args.auto_approve else "manual"
            }
        )
        
        # Generate workflow ID
        workflow_id = f"customer-support-{int(datetime.datetime.now().timestamp())}"
        
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
