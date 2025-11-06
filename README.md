# DAPERL Framework

A multi-agent Temporal framework implementing the **DAPERL** pattern: **D**etection, **A**nalysis, **P**lanning, **E**xecution, **R**eporting, and **L**earning.

## Overview

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
┌─────────────────────────────────────────────────────────┐
│                   DAPERL Workflow                        │
├─────────────────────────────────────────────────────────┤
│  1. Detection  →  2. Analysis  →  3. Planning           │
│       ↓               ↓               ↓                  │
│  Find Problems   Root Causes    Create Plan             │
│                                      ↓                   │
│                              4. Await Approval           │
│                                      ↓                   │
│  5. Execution  →  6. Reporting  →  7. Learning          │
│       ↓               ↓               ↓                  │
│  Execute Plan    Generate Report   Extract Insights     │
└─────────────────────────────────────────────────────────┘
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

1. **Clone and Install**:
```bash
cd temporal-daperl
poetry install
```

2. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start Temporal** (if running locally):
```bash
temporal server start-dev
```

4. **Start Worker**:
```bash
poetry run python scripts/run_worker.py
```

## Usage

### Basic Example

```bash
# Start a workflow
poetry run python scripts/start_workflow.py \
  --domain "my-domain" \
  --data '{"items": ["item1", "item2"]}' \
  --auto-approve

# Query status
poetry run python scripts/query_workflow.py \
  --workflow-id daperl-my-domain-123456

# Approve plan (if not auto-approved)
poetry run python scripts/approve_workflow.py \
  --workflow-id daperl-my-domain-123456
```

### Python API

```python
from temporalio.client import Client
from daperl.workflows import DAPERLWorkflow
from daperl.core.models import DAPERLInput

# Connect to Temporal
client = await Client.connect("localhost:7233")

# Create workflow input
workflow_input = DAPERLInput(
    domain="my-domain",
    data={"key": "value"},
    config={
        "detection_instructions": "Look for X, Y, Z",
        "available_actions": ["action1", "action2"]
    },
    auto_approve=False
)

# Start workflow
handle = await client.start_workflow(
    DAPERLWorkflow.run,
    workflow_input,
    id="my-workflow-id",
    task_queue="daperl-task-queue",
)

# Query status
status = await handle.query(DAPERLWorkflow.get_status)
print(f"Status: {status['status']}")

# Approve plan
await handle.signal(DAPERLWorkflow.approve_plan)

# Wait for result
result = await handle.result()
print(f"Result: {result.summary}")
```

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

### Providing Execution Actions

```python
from daperl.agents import ExecutionAgent

# Define action handlers
async def handle_send_email(action, context):
    # Send email logic
    return {"success": True, "message": "Email sent"}

async def handle_update_database(action, context):
    # Update database logic
    return {"success": True, "message": "Database updated"}

# Create agent with action registry
action_registry = {
    "send_email": handle_send_email,
    "update_database": handle_update_database,
}

execution_agent = ExecutionAgent(
    action_registry=action_registry,
    llm_config=config.execution_llm
)
```

## Project Structure

```
temporal-daperl/
├── daperl/                      # Main framework package
│   ├── core/                    # Base abstractions
│   │   ├── agents.py            # Base agent classes
│   │   ├── models.py            # Data models
│   │   └── types.py             # Type definitions
│   ├── agents/                  # DAPERL agent implementations
│   │   ├── detection.py
│   │   ├── analysis.py
│   │   ├── planning.py
│   │   ├── execution.py
│   │   ├── reporting.py
│   │   └── learning.py          # NEW: Learning agent
│   ├── workflows/               # Temporal workflows
│   │   └── daperl_workflow.py
│   ├── activities/              # Temporal activities
│   │   └── agent_activities.py
│   ├── llm/                     # LLM provider abstraction
│   │   ├── base.py
│   │   ├── factory.py
│   │   └── providers/
│   ├── storage/                 # Learning data storage
│   │   ├── base.py
│   │   └── json_storage.py
│   └── config/                  # Configuration
│       └── settings.py
├── scripts/                     # Utility scripts
│   ├── run_worker.py
│   ├── start_workflow.py
│   ├── query_workflow.py
│   └── approve_workflow.py
├── examples/                    # Example implementations
└── tests/                       # Tests
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

## References

- [Temporal Documentation](https://docs.temporal.io/)
- [Reference Implementation](https://github.com/joshmsmith/temporal-multi-agent-order-repair)
- [LiteLLM Documentation](https://docs.litellm.ai/)
