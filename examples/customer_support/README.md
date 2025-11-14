# Customer Support Domain Example

This example demonstrates how to use the DAPER framework for intelligent customer support automation. It showcases sophisticated detection, analysis, and planning capabilities for real-world customer service scenarios.

## Overview

The customer support domain implements a comprehensive automation system that:
- Detects support issues, SLA violations, and customer sentiment patterns
- Analyzes customer context, churn risk, and expertise requirements
- Plans intelligent response strategies and escalation workflows
- Integrates with ticketing systems, CRM platforms, and knowledge bases

## Files Structure

```
customer_support/
├── README.md              # This documentation file
├── run_example.py         # Main example runner and demonstration
├── domain.py             # Core DAPER activities (Detect, Analyze, Plan)
├── tools.py              # Customer support tools and integrations
├── data_loaders.py       # Data loaders for various support systems
└── data.json             # Comprehensive sample dataset
```

## Key Features

### 🔍 Detection Capabilities
- **SLA Violation Monitoring**: Real-time tracking of response and resolution deadlines
- **Sentiment Analysis**: Customer emotion detection from tickets and forum posts
- **Escalation Pattern Recognition**: Identification of issues requiring specialist attention
- **Knowledge Base Gap Detection**: Discovery of missing documentation areas
- **Customer Health Monitoring**: Early warning system for account issues

### 📊 Analysis Capabilities
- **Customer Context Analysis**: Deep understanding of account history and value
- **Churn Risk Assessment**: Predictive scoring for customer retention
- **Expertise Matching**: Intelligent routing based on issue complexity
- **Satisfaction Correlation**: Analysis of factors affecting customer happiness
- **Support Tier Optimization**: Data-driven recommendations for account upgrades

### 📋 Planning Capabilities
- **Response Strategy Planning**: Dynamic determination of service level (white glove, expedited, standard)
- **Escalation Workflow Design**: Intelligent routing to appropriate specialists
- **Account Management Actions**: Proactive customer health interventions
- **Follow-up Scheduling**: Automated satisfaction tracking and check-ins
- **Resource Allocation**: Optimization of support team capacity

### 🛠️ Tool Integrations
- **Ticket Management**: Status updates, assignments, and lifecycle tracking
- **Customer Communications**: Multi-channel messaging (email, chat, phone)
- **Knowledge Base Operations**: Search, article suggestions, and gap reporting
- **Account Management**: Tier adjustments, health score updates, and notes
- **Specialist Escalation**: Expert routing and context transfer
- **Task Automation**: Follow-up creation and reminder scheduling

## Sample Data

The example includes realistic sample data:
- **5 Support Tickets**: Various priorities, categories, and customer sentiment
- **5 Customer Profiles**: Different account types, tiers, and health scores
- **3 Forum Posts**: Community discussions with engagement metrics
- **6 Product Definitions**: Features, availability, and plan restrictions
- **5 Knowledge Base Articles**: Documentation with categories and search tags

## Business Value

This implementation demonstrates how DAPER can deliver:

- **Faster Response Times**: Intelligent priority detection and routing
- **Higher Customer Satisfaction**: Personalized service based on customer context
- **Proactive Churn Prevention**: Early risk detection and intervention strategies
- **Optimized Resource Utilization**: Smart specialist allocation and workload balancing
- **Continuous Knowledge Improvement**: Gap identification and content optimization
- **End-to-End Automation**: Seamless workflow orchestration with human oversight

## Real-World Integration

The domain is designed to integrate with:

### Ticketing Systems
- Zendesk, Salesforce Service Cloud, Jira Service Management
- ServiceNow, Freshdesk, Help Scout

### CRM Platforms  
- Salesforce, HubSpot, Microsoft Dynamics
- Pipedrive, Zoho CRM, Copper

### Communication Tools
- Email platforms, Slack, Microsoft Teams
- Twilio, Intercom, LiveChat

### Knowledge Management
- Confluence, Notion, GitBook
- Internal documentation systems, wikis

## Installation

This example uses Poetry for Python package management. Install dependencies:

```bash
# From the customer_support directory
cd examples/customer_support
poetry install
```

This will install all required dependencies including:
- The main `temporal-daperl` framework (from the parent directory)
- FastAPI and Uvicorn for the UI backend
- WebSockets support
- Pydantic for data validation

## Running the Example

**Start the Worker in the daperl folder**:
```bash
poetry run python ../../scripts/run_worker.py
```

**Start the front end (API layer and UI)**:
```bash
poetry run python run_ui.py
```

**Start the Workflow**:

```bash
# Run with manual approval (default)
poetry run python run_example.py

# Run with auto-approval for demo purposes
poetry run python run_example.py --auto-approve
```

### Command Line Options

- `--auto-approve`: Auto-approve actions without human intervention (default: False)
- `--help`: Show help message and available options

This will:
1. Load the sample customer support data
2. Run the complete DAPER workflow (Detect → Analyze → Plan → Execute → Report → Learn)
3. Demonstrate key capabilities and business value
4. Show detailed workflow results and next steps
5. Execute actions based on auto-approve setting

## Architecture Notes

The customer support domain follows DAPER best practices:

- **Modular Design**: Separate concerns for detection, analysis, and planning
- **Extensible Tools**: Plugin architecture for easy integration additions
- **Flexible Data Loading**: Support for multiple data source types
- **Comprehensive Testing**: End-to-end workflow validation
- **Production Ready**: Enterprise-grade error handling and logging

## Future Enhancements

Potential extensions include:
- Machine learning integration for predictive analytics
- Advanced NLP for better sentiment analysis and intent detection
- Real-time dashboard integration for live monitoring
- A/B testing framework for response strategy optimization
- Integration with workforce management systems

## Technical Requirements

- Python 3.8+
- DAPER framework core components
- Optional: Integration with specific platforms (Zendesk SDK, Salesforce API, etc.)

This example serves as a comprehensive template for building sophisticated customer support automation systems that scale with business needs while maintaining high service quality.
