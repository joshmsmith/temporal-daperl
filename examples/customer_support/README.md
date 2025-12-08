# Customer Support Domain Example

This example demonstrates how to use the DAPERL framework for intelligent customer support automation. It showcases sophisticated detection, analysis, and planning capabilities for real-world customer service scenarios.

## Overview

The customer support domain implements a comprehensive automation system that:
- Detects support issues, SLA violations, and customer sentiment patterns
- Analyzes customer context, churn risk, and expertise requirements
- Plans intelligent response strategies and escalation workflows
- Could integrate with ticketing systems, CRM platforms, and knowledge bases (current implementation updates in-repo data.json file)

## Files Structure

```
customer_support/
├── README.md              # This documentation file
├── run_ui.py              # UI server launcher
├── tools.py               # Customer support tools and integrations
├── data.json              # Comprehensive sample dataset
├── data/                  # Runtime data directory
│   ├── insights.json      # Generated insights data
│   └── metrics.json       # Generated metrics data
└── ui/                    # User interface components
    ├── backend/           # FastAPI backend server
    │   └── main.py        # API endpoints and WebSocket handlers
    └── frontend/          # React/TypeScript frontend
        └── src/           # Frontend source code
            └── components/ # React components for workflow visualization
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

The implementation of DAPERL could integrate with:

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

## Running the Example

This example uses Poetry for Python package management. Install dependencies:

```bash
# Start the Temporal server (if connecting locally)
temporal server start-dev

# In another terminal, starting from the project root, create or copy a .env file into the expense_reports folder
cp .env examples/customer_support/.

# Move to the expense_reports directory
cd examples/customer_support

# Install the Python dependencies
poetry install

# Install the Node dependencies, then go back up to the customer_support folder
cd ui
npm install
cd ..

# Start the worker
poetry run python ../../scripts/run_worker.py

# In a third terminal, run the API layer and UI
poetry run python run_ui.py
```

## Future Enhancements

Potential extensions include:
- EscalateToSpecialistTool: make this "real" tool functionality that pulls from the data file
- CreateFollowUpTaskTool: change this to create and persist a new KB article 
- Add tests

This example serves as a comprehensive template for building sophisticated customer support automation systems that scale with business needs while maintaining high service quality.
