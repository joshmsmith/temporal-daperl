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

## Installation

### Prerequisites

- Python 3.12+
- Temporal Server (local or cloud)
- API keys for LLM providers (OpenAI, Anthropic, etc.)

## Configuration

### Environment Variables

See `.env.example` for all configuration options:

- **Temporal Settings**: `TEMPORAL_HOST`, `TEMPORAL_NAMESPACE`, `TEMPORAL_TASK_QUEUE`
- **Per-Agent LLM**: `<AGENT>_LLM_PROVIDER`, `<AGENT>_LLM_MODEL`, etc.
- **API Keys**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Learning Storage**: `LEARNING_STORAGE_TYPE`, `LEARNING_STORAGE_PATH`

### Per-Agent LLM Configuration Example

Each agent can be configured with its own LLM:

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

## Run it!

The easiest way to see DAPERL in action is with the [expense report example](/examples/expense_reports/README.md) (simple, no UI) or the [customer support example](/examples/customer_support/README.md) (more complex, with an API layer and a UI).

## Create Your Own (Domain-Specific) Implementation!

The framework is highly extensible - you can use the building blocks to create your own DAPERLWorkflow or ExecutionAgentWorkflow implementation, or you can create a customized agent implementation, or you can use everything as-is and simply define your domain and create the tools you might want the AI to execute. The instructions below are for this last option:

1. Define your domain data structure
2. Figure out how the data will get into the [DAPERLWorkflow](/daperl/workflows/daperl_workflow.py), potentially adding an activity for data loading (see the note re: Phase 0)
3. Configure domain-specific prompts for each agent, which are passed in from the client as part of the workflow starting data ([expense_reports example](/examples/expense_reports/run_example.py), see the setup of the config)
4. Provide action handlers for the tool execution/for the [execution agent](/daperl/workflows/execution_workflow.py) to use ([Details re: How Tool Resolution Works](/daperl/HowToolsWork.MD))

This is an example of creating your own DetectionAgent using the BaseDetectionAgent: 

```python
from daperl.core.agents import BaseDetectionAgent
from daperl.core.models import AgentContext, DetectionResult

class MyDetectionAgent(BaseDetectionAgent):
    async def execute(self, context: AgentContext) -> DetectionResult:
        # Add domain-specific detection logic
        # Or use the generic implementation
        return await super().execute(context)
```

### Remember, it's all just code. This is one of the reasons that Temporal is code-first, because then you can combine the benefits of Temporal with things like inheritance and object-orientation.

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

## Potential Future Enhancements
- Add proactive monitoring agent
- Look at adding stuff in customer_support/ui/backend to the framework (API layer for UI)
- Add MCP server
- Add ability to approve/deny specific proposed solutions OR the whole set (currently it's the whole set)

## References

- [Temporal Documentation](https://docs.temporal.io/)
- [Reference Implementation](https://github.com/joshmsmith/temporal-multi-agent-order-repair)
- [LiteLLM Documentation](https://docs.litellm.ai/)
# temporal-daperl
