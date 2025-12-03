# DAPERL Framework: Intelligent Automation

A multi-agent Temporal framework implementing the **DAPERL** pattern: **D**etection, **A**nalysis, **P**lanning, **E**xecution, **R**eporting, and **L**earning.

## Overview: Humans + Agents Getting Things Done Together

DAPERL is a generic, extensible framework for building intelligent automation systems using Temporal workflows and AI agents. Each phase of the DAPERL cycle is handled by a specialized agent that can use different LLMs and configurations.

### Key Features

- **6 Specialized Agents**: Detection, Analysis, Planning, Execution, Reporting, and Learning
- **Per-Agent LLM Configuration**: Each agent can use different LLM providers and models
- **Multi-LLM Support**: OpenAI, Anthropic, and any provider via LiteLLM
- **Temporal Best Practices**: Proper workflow/activity separation, idempotency, error handling
- **Python Best Practices**: Type hints, dependency injection, modular design
- **Learning Component**: Stores execution metrics and provides insights for improvement
- **Human-in-the-Loop**: Approval workflow for execution plans
- **Domain Agnostic**: Easily adaptable to any domain

## Architecture

```
┌───────────────────────────────────────────────────────┐
│                   DAPERL Workflow                     │
├───────────────────────────────────────────────────────┤
│  1. Detection  →  2. Analysis  →  3. Planning         │
│       ↓               ↓               ↓               │
│  Find Problems   Root Causes    Create Plan           │
│                       ↓                               │
│               4. Await Approval                       │
│                       ↓                               │
│  5. Execution  →  6. Reporting  →  7. Learning        │
│       ↓               ↓               ↓               │
│  Execute Plan    Generate Report   Extract Insights   │
└───────────────────────────────────────────────────────┘
```

### Per-Agent LLM Configuration

Each agent can be configured with its own LLM:

```python
# Detection: Fast, cheap model
DETECTION_LLM_MODEL=gpt-3.5-turbo

# Analysis: More powerful model
ANALYSIS_LLM_MODEL=gpt-4o

# Planning: Different provider
PLANNING_LLM_PROVIDER=anthropic
PLANNING_LLM_MODEL=claude-3-5-sonnet-20241022

# And so on for Execution, Reporting, Learning...
```

## Installation

### Prerequisites

- Python 3.10+
- Temporal Server (local or cloud)
- API keys for LLM providers (OpenAI, Anthropic, etc.)

### Setup

The easiest way to see DAPERL in action is with the [expense report example](/examples/expense_reports/README.md) (simple, no UI) or the [customer support example](/examples/customer_support/README.md) (more complex, with an API layer and a UI).

## Configuration

### Environment Variables

See `.env.example` for all configuration options:

- **Temporal Settings**: `TEMPORAL_HOST`, `TEMPORAL_NAMESPACE`, `TEMPORAL_TASK_QUEUE`
- **Per-Agent LLM**: `<AGENT>_LLM_PROVIDER`, `<AGENT>_LLM_MODEL`, etc.
- **API Keys**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Learning Storage**: `LEARNING_STORAGE_TYPE`, `LEARNING_STORAGE_PATH`

### Per-Agent LLM Configuration Example

```env
# Detection Agent - Fast & Cheap
DETECTION_LLM_PROVIDER=openai
DETECTION_LLM_MODEL=gpt-3.5-turbo
DETECTION_LLM_TEMPERATURE=0.3
DETECTION_LLM_MAX_TOKENS=2000

# Analysis Agent - More Powerful
ANALYSIS_LLM_PROVIDER=openai
ANALYSIS_LLM_MODEL=gpt-4o
ANALYSIS_LLM_TEMPERATURE=0.5
ANALYSIS_LLM_MAX_TOKENS=4000

# Planning Agent - Different Provider
PLANNING_LLM_PROVIDER=anthropic
PLANNING_LLM_MODEL=claude-3-5-sonnet-20241022
PLANNING_LLM_TEMPERATURE=0.7
PLANNING_LLM_MAX_TOKENS=8000
```

## Extending the Framework
(NEEDS MORE DETAIL)

### Creating a Domain-Specific Implementation

1. **Define your domain data structure**
2. **Optionally extend agents** with domain-specific logic
3. **Provide action handlers** for the execution agent
4. **Configure domain-specific prompts**

Example:

```python
from daperl.core.agents import BaseDetectionAgent
from daperl.core.models import AgentContext, DetectionResult

class MyDetectionAgent(BaseDetectionAgent):
    async def execute(self, context: AgentContext) -> DetectionResult:
        # Add domain-specific detection logic
        # Or use the generic implementation
        return await super().execute(context)
```

### How Tools Are Resolved

[Details re: How Tool Resolution Works](/daperl/HowToolsWork.MD)


## Project Structure

```
temporal-daperl/
├── daperl/                      # Main framework package
│   ├── core/                    # Base abstractions
│   │   ├── agents.py            # Base agent classes
│   │   ├── models.py            # Data models
│   │   ├── types.py             # Type definitions
│   │   ├── tools.py             # Tool execution system
│   │   └── exceptions.py        # Custom exceptions
│   ├── agents/                  # DAPERL agent implementations
│   │   ├── detection.py         # Detection agent
│   │   ├── analysis.py          # Analysis agent
│   │   ├── planning.py          # Planning agent
│   │   ├── reporting.py         # Reporting agent
│   │   └── learning.py          # Learning agent
│   ├── workflows/               # Temporal workflows
│   │   ├── daperl_workflow.py   # Main DAPERL workflow
│   │   └── execution_workflow.py # Execution workflow
│   ├── activities/              # Temporal activities
│   │   └── agent_activities.py  # Agent activity wrappers
│   ├── llm/                     # LLM provider abstraction
│   │   ├── base.py              # Base LLM interface
│   │   ├── factory.py           # LLM factory
│   │   └── providers/
│   │       └── litellm_provider.py # LiteLLM implementation
│   ├── storage/                 # Learning data storage
│   │   ├── base.py              # Storage interface
│   │   └── json_storage.py      # JSON storage implementation
│   ├── config/                  # Configuration
│   │   └── settings.py          # Settings management
├── scripts/                     # Utility scripts
│   ├── run_worker.py            # Start Temporal worker
│   ├── start_workflow.py        # Start a new workflow
│   ├── query_workflow.py        # Query workflow state
│   ├── query_execution_workflow.py # Query execution workflow
│   └── approve_workflow.py      # Approve execution plan
├── examples/                    # Example implementations
│   ├── expense_reports/         # Simple expense report example
│   └── customer_support/        # Advanced customer support example
├── data/                        # Runtime data directory
├── .env.example                 # Environment variables template
└── pyproject.toml               # Python project configuration
```

## DAPERL Agents

### 1. Detection Agent
- **Purpose**: Identify problems in the system
- **Input**: Domain data
- **Output**: List of detected problems with severity
- **LLM Use**: Analyzes data to find issues

### 2. Analysis Agent
- **Purpose**: Analyze root causes of detected problems
- **Input**: Detection results + domain data
- **Output**: Root causes and recommendations
- **LLM Use**: Deep analysis of problems

### 3. Planning Agent
- **Purpose**: Create execution plans to fix problems
- **Input**: Analysis results
- **Output**: Detailed action plan with confidence scores
- **LLM Use**: Strategic planning of remediation steps

### 4. Execution Agent
- **Purpose**: Execute planned actions
- **Input**: Execution plan
- **Output**: Results of each action
- **Action Handlers**: Pluggable domain-specific handlers

### 5. Reporting Agent
- **Purpose**: Generate comprehensive reports
- **Input**: All phase results
- **Output**: Summary report with metrics
- **LLM Use**: Synthesize results into readable report

### 6. Learning Agent (NEW!)
- **Purpose**: Learn from executions to improve future performance
- **Input**: All phase results + historical data
- **Output**: Insights, patterns, recommendations
- **Storage**: Persists metrics and insights
- **LLM Use**: Pattern recognition and insight extraction

## Learning Component

The Learning Agent provides continuous improvement:

- **Stores Execution Metrics**: Every workflow execution is recorded
- **Pattern Recognition**: Identifies recurring issues and successful patterns
- **Confidence Tracking**: Monitors accuracy of confidence scores
- **Recommendations**: Suggests improvements to detection thresholds and strategies
- **Knowledge Base**: Pluggable storage (JSON, SQLite, PostgreSQL, Vector DB)

Example insights:
- "Detection confidence threshold should be lowered for problem type X"
- "Action Y has 95% success rate for problem type Z"
- "Executions with root cause A typically require 3 specific actions"

## Best Practices

### Temporal Best Practices
- Activities are idempotent and can safely retry
- Workflows are deterministic
- Clear separation between orchestration and execution
- Proper error handling and retry policies

### Python Best Practices
- Full type hints with Pydantic models
- Dependency injection for flexibility
- Modular, reusable components
- Comprehensive docstrings

### LLM Best Practices
- Use faster/cheaper models for simple tasks (detection, reporting)
- Use powerful models for complex tasks (analysis, planning)
- Validate LLM outputs
- Retry on invalid responses

## Monitoring

Use Temporal UI to monitor workflows:

```bash
# Access Temporal UI
open http://localhost:8233
```

Features:
- View workflow execution history
- Inspect activity logs
- Query workflow state
- Send signals to workflows

## Troubleshooting

### Common Issues

**Worker not picking up tasks:**
- Ensure Temporal server is running
- Check task queue name matches
- Verify worker is connected to correct namespace

**LLM API errors:**
- Verify API keys are set correctly
- Check rate limits
- Ensure model names are correct

**Activity timeouts:**
- Increase `start_to_close_timeout` for slow LLM calls
- Check network connectivity
- Monitor LLM response times

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Examples

### Expense Report Processing

A simple, relatable example in `examples/expense_reports/`:

**The Problem**: Expense reports with missing receipts, policy violations, duplicate submissions

**How DAPERL Solves It**:
- **Detection**: Finds 4-5 problems (missing receipts, over limits, duplicates, etc.)
- **Analysis**: Determines root causes (employee error, unclear policy)
- **Planning**: Creates actions (request receipt, calculate mileage, flag for review)
- **Execution**: Simulates sending notifications and updating statuses
- **Reporting**: Generates summary of processed reports
- **Learning**: Identifies patterns (which employees need training, common errors)

Run it: `poetry run python examples/expense_reports/run_example.py`

## Potential Future Enhancements
- Add proactive monitoring agent
- Look at adding stuff in customer_support/ui/backend to the framework (API layer for UI)
- Add MCP server
- Add ability to approve/deny specific proposed solutions OR the whole set (currently it's the whole set)
f
## References

- [Temporal Documentation](https://docs.temporal.io/)
- [Reference Implementation](https://github.com/joshmsmith/temporal-multi-agent-order-repair)
- [LiteLLM Documentation](https://docs.litellm.ai/)
# temporal-daperl
