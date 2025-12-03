# How Tools Work in DAPERL

This document explains the complete end-to-end flow of how actions are executed in the DAPERL framework, from the initial `available_actions` configuration to the actual execution of tool code.

## Overview

The DAPERL framework uses a sophisticated pipeline to dynamically load, register, and execute domain-specific tools. This architecture allows different domains (e.g., customer support, expense reports) to define their own tools without modifying the core framework.

## The Complete Pipeline

### 1. Configuration Setup

**Location**: `examples/customer_support/ui/backend/main.py` (or any workflow starter)

When starting a DAPERL workflow, you provide a configuration that includes `available_actions`:

```python
config = {
    "detection_instructions": "...",
    "analysis_instructions": "...",
    "planning_instructions": "...",
    "available_actions": [
        "update_ticket_status",
        "send_customer_response",
        "update_customer_account",
        "search_knowledge_base",
        "escalate_to_specialist",
        "notify_account_manager",
        "create_follow_up_task"
    ],
    # ... other config
}
```

These action names are passed into the `DAPERLInput` and flow through the entire system.

### 2. Planning Phase

**Location**: `daperl/agents/planning.py`

The Planning Agent is responsible for creating an execution plan with specific actions to address detected problems.

#### 2a. Tool Discovery

When the planning agent runs, it first loads domain tools to discover what actions are available:

```python
# In run_planning_agent activity (agent_activities.py)
if context.config.get("available_actions"):
    _load_domain_tools(context)
```

The `_load_domain_tools()` function:
1. Converts domain name (e.g., "customer-support" → "customer_support")
2. Dynamically imports `{domain_module}.tools` module
3. Calls the registration function (e.g., `register_customer_support_tools()`)

#### 2b. Building the LLM Prompt

The Planning Agent queries the `ToolRegistry` to get detailed information about each available action:

```python
# From planning.py
if "available_actions" in context.config:
    from daperl.core.tools import ToolRegistry
    
    available_actions = context.config['available_actions']
    
    # Get detailed tool information including parameters
    tool_details = []
    for action_name in available_actions:
        tools_for_domain = ToolRegistry.get_tools_for_domain(context.domain)
        tool_info = next((t for t in tools_for_domain if t['name'] == action_name), None)
        
        if tool_info:
            tool_details.append({
                "action_type": tool_info['name'],
                "description": tool_info['description'],
                "required_parameters": tool_info['parameters']
            })
```

This information is included in the LLM prompt so the AI knows:
- What actions are available
- What each action does
- What parameters each action requires

#### 2c. LLM Response

The LLM analyzes the problems and returns a plan with `Action` objects:

```json
{
    "plan": {
        "id": "plan-123",
        "actions": [
            {
                "id": "action-1",
                "action_type": "update_ticket_status",
                "description": "Update ticket to in-progress",
                "target": "TICKET-001",
                "parameters": {
                    "ticket_id": "TICKET-001",
                    "status": "in_progress",
                    "notes": "Starting investigation"
                },
                "confidence": 0.95
            }
        ]
    }
}
```

Each `Action` has:
- **action_type**: Must match one of the available_actions (e.g., "update_ticket_status")
- **parameters**: Dictionary of arguments for that specific tool
- **target**, **description**, metadata, etc.

### 3. Execution Phase Begins

**Location**: `daperl/workflows/execution_workflow.py`

The `ExecutionAgentWorkflow` is a child workflow that executes the planned actions:

```python
@workflow.run
async def run(self, context: AgentContext) -> ExecutionResult:
    # Get the plan from context history
    planning_result = self._get_planning_result(context)
    plan = planning_result.plan
    
    # Execute each action sequentially
    for action in plan.actions:
        action_result = await workflow.execute_activity(
            execute_action_activity,
            args=[action, context],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )
```

Key points:
- Actions are executed **sequentially** (one at a time, in order)
- Each action is executed as a **separate Temporal activity** for better visibility
- The workflow continues even if some actions fail, collecting all results

### 4. Action Execution Activity

**Location**: `daperl/activities/agent_activities.py`

The `execute_action_activity` is where the magic happens - this is where we convert an `Action` object into actual tool execution.

#### Step 4a: Load Domain Tools

```python
@activity.defn
async def execute_action_activity(action: Action, context: AgentContext) -> ActionResult:
    # Import the tool registry
    from daperl.core.tools import ToolRegistry
    
    # Load domain-specific tools
    _load_domain_tools(context)
```

The `_load_domain_tools()` function dynamically imports the domain's tools module:

```python
def _load_domain_tools(context: AgentContext) -> None:
    # Convert domain name for import
    domain_module = context.domain.replace("-", "_")  # "customer-support" → "customer_support"
    
    # Import the tools module
    tools_module_name = f"{domain_module}.tools"
    tools_module = importlib.import_module(tools_module_name)
    
    # Call the registration function
    register_func_name = f"register_{domain_module}_tools"
    if hasattr(tools_module, register_func_name):
        register_func = getattr(tools_module, register_func_name)
        register_func(domain=context.domain)
```

#### Step 4b: Tool Registration

**Location**: `examples/customer_support/tools.py`

Each domain has a registration function that registers all its tools:

```python
def register_customer_support_tools(domain: str = "customer_support"):
    """Register customer support tools for a domain."""
    tools = [
        UpdateTicketStatusTool,
        SendCustomerResponseTool,
        UpdateCustomerAccountTool,
        SearchKnowledgeBaseTool,
        EscalateToSpecialistTool,
        NotifyAccountManagerTool,
        CreateFollowUpTaskTool
    ]
    
    for tool_class in tools:
        ToolRegistry.register_tool(tool_class, domain)
```

The `ToolRegistry.register_tool()` method:

```python
@classmethod
def register_tool(cls, tool_class: type, domain: str = "default"):
    if domain not in cls._tools:
        cls._tools[domain] = {}
    
    # Create a temporary instance to get the tool info
    temp_instance = tool_class(domain=domain)
    tool_info = temp_instance.get_info()
    
    # Store: _tools[domain][tool_name] = tool_class
    cls._tools[domain][tool_info.name] = tool_class
```

After registration, the `ToolRegistry` has a mapping like:
```
{
    "customer-support": {
        "update_ticket_status": UpdateTicketStatusTool,
        "send_customer_response": SendCustomerResponseTool,
        ...
    }
}
```

#### Step 4c: Create Action Registry

Back in `execute_action_activity`, we create an action registry:

```python
action_registry = ToolRegistry.create_action_registry(
    available_actions=available_actions,
    domain=context.domain
)
```

**Location**: `daperl/core/tools.py`

The `create_action_registry()` method creates async handler functions:

```python
@classmethod
def create_action_registry(
    cls,
    available_actions: list[str],
    domain: str = "default"
) -> Dict[str, Callable]:
    """Create an action registry from available action names."""
    action_registry = {}
    
    for action_name in available_actions:
        # Get the tool class for this action
        tool_class = cls.get_tool(action_name, domain)
        
        if tool_class:
            # Create a closure to capture the tool_class properly
            def make_handler(tool_cls, dom):
                async def handler(action, context):
                    """Handler function for executing a tool."""
                    tool_instance = tool_cls(domain=dom)
                    # Action model has 'parameters' field
                    result = await tool_instance.execute(action.parameters)
                    return result
                return handler
            
            # Create the handler and add to registry
            action_registry[action_name] = make_handler(tool_class, domain)
    
    return action_registry
```

The action registry is now a mapping like:
```
{
    "update_ticket_status": <async handler function>,
    "send_customer_response": <async handler function>,
    ...
}
```

Each handler function:
1. Instantiates the tool class
2. Calls `tool.execute(action.parameters)`
3. Returns the result

#### Step 4d: Execute the Handler

```python
try:
    # Check if we have a handler for this action type
    if action.action_type in action_registry:
        # Execute using registered handler
        handler = action_registry[action.action_type]
        result = await handler(action, context)
        
        action_result = ActionResult(
            action_id=action.id,
            success=result.get("success", True),
            message=result.get("message", f"Executed {action.action_type}"),
            data=result.get("data", {})
        )
        
        # Raise exception if action failed
        if not action_result.success:
            raise ActionExecutionError(action_result)
        
        return action_result
```

### 5. Tool Execution

**Location**: `examples/customer_support/tools.py`

Finally, the actual tool code executes! For example, `UpdateTicketStatusTool`:

```python
class UpdateTicketStatusTool(BaseTool):
    """Tool for updating ticket status and adding notes."""
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update ticket status and add internal notes."""
        ticket_id = arguments.get("ticket_id")
        new_status = arguments.get("status")
        notes = arguments.get("notes", "")
        
        # Validate inputs
        if not ticket_id or not new_status:
            return self.create_response(
                success=False,
                data={"error": "ticket_id and status are required"},
                additional_notes="Missing required parameters"
            )
        
        # Read the data.json file
        data_file_path = os.path.join(os.path.dirname(__file__), "data.json")
        with open(data_file_path, 'r') as f:
            data = json.load(f)
        
        # Find and update the ticket
        tickets = data.get("customer_support_data", {}).get("tickets", [])
        for ticket in tickets:
            if ticket.get("ticket_id") == ticket_id:
                ticket["status"] = new_status
                ticket["last_updated"] = datetime.utcnow().isoformat()
                if notes:
                    # Add notes...
                break
        
        # Write back to file
        with open(data_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Return success response
        return self.create_response(
            success=True,
            data=update_result,
            additional_notes=f"Successfully updated ticket {ticket_id}"
        )
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="update_ticket_status",
            description="Update ticket status and add internal notes",
            parameters=["ticket_id", "status", "notes", "assigned_to"],
            domain=self.domain,
            tool_class=UpdateTicketStatusTool
        )
```

Key points about tool implementations:
- Tools inherit from `BaseTool`
- Must implement `execute(arguments)` - the actual business logic
- Must implement `get_info()` - metadata for discovery
- Use `create_response()` helper for standardized output format
- Return dict with `success`, `data`, `message` keys

### 6. Result Handling

The result flows back up the chain:

1. **Tool returns**: `{"success": True, "data": {...}, "message": "..."}`
2. **Handler returns**: Same result dict
3. **Activity creates**: `ActionResult` object
4. **If failed**: Raises `ActionExecutionError` with the ActionResult
5. **Workflow catches**: Exception or success, adds to results list
6. **Workflow returns**: `ExecutionResult` with all action results

```python
# In ExecutionAgentWorkflow
return ExecutionResult(
    success=overall_success,
    message=f"Execution complete: {self._success_count} succeeded, {self._failure_count} failed",
    confidence=confidence,
    plan_id=plan.id,
    actions_executed=self._actions_executed,
    success_count=self._success_count,
    failure_count=self._failure_count
)
```

## Key Design Patterns

### 1. Dynamic Tool Loading

Tools are loaded at runtime based on the domain, allowing different domains to have different tools without hardcoding:

```python
# Convention: examples/{domain}/tools.py with register_{domain}_tools() function
tools_module = importlib.import_module(f"{domain_module}.tools")
register_func = getattr(tools_module, f"register_{domain_module}_tools")
register_func(domain=context.domain)
```

### 2. Registry Pattern

The `ToolRegistry` acts as a central registry mapping tool names to tool classes:

```
_tools[domain][tool_name] → tool_class
```

This enables:
- **Discovery**: Planning agent can query available tools
- **Invocation**: Execution activity can instantiate and call tools
- **Decoupling**: Core framework doesn't need to know about specific tools

### 3. Closure for Handlers

The `create_action_registry` uses closures to properly capture the tool class and domain:

```python
def make_handler(tool_cls, dom):
    async def handler(action, context):
        tool_instance = tool_cls(domain=dom)
        result = await tool_instance.execute(action.parameters)
        return result
    return handler
```

This ensures each handler has its own copy of the tool class and domain, avoiding Python's late-binding closure issues.

### 4. Separation of Concerns

- **Planning Agent**: Decides WHAT actions to take based on analysis
- **Tool Registry**: Maintains the mapping of action names to implementations
- **Execution Activity**: Handles HOW to invoke the tools (registration, error handling)
- **Tool Classes**: Implement the actual business logic for each action
- **Execution Workflow**: Orchestrates the execution flow and collects results

## Adding a New Domain

To add a new domain with custom tools:

1. **Create tools file**: `examples/my_domain/tools.py`

2. **Define tool classes**:
```python
from daperl.core.tools import BaseTool, ToolInfo

class MyCustomTool(BaseTool):
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Your business logic here
        return self.create_response(success=True, data={...})
    
    def get_info(self) -> ToolInfo:
        return ToolInfo(
            name="my_custom_action",
            description="Does something custom",
            parameters=["param1", "param2"],
            domain=self.domain,
            tool_class=MyCustomTool
        )
```

3. **Create registration function**:
```python
def register_my_domain_tools(domain: str = "my_domain"):
    tools = [MyCustomTool, AnotherTool, ...]
    for tool_class in tools:
        ToolRegistry.register_tool(tool_class, domain)
```

4. **Use in workflow**:
```python
config = {
    "available_actions": ["my_custom_action", ...],
    ...
}

workflow_input = DAPERLInput(
    domain="my-domain",  # Note: hyphenated
    data=my_data,
    config=config
)
```

The framework will automatically:
- Load your tools module
- Register your tools
- Make them available to the planning agent
- Execute them when planned

## Flow Diagram

```
1. Start Workflow
   └─> DAPERLInput with config["available_actions"]

2. Planning Phase
   ├─> Load domain tools (_load_domain_tools)
   ├─> Register tools (register_customer_support_tools)
   ├─> Query ToolRegistry for tool metadata
   ├─> Send available actions + parameters to LLM
   └─> LLM returns plan with Action objects

3. Execution Phase (ExecutionAgentWorkflow)
   └─> For each Action in plan:
       └─> execute_activity(execute_action_activity)

4. Action Execution Activity
   ├─> Load domain tools (if not loaded)
   ├─> Create action registry (ToolRegistry.create_action_registry)
   ├─> Look up handler: action_registry[action.action_type]
   └─> Execute handler

5. Handler Execution
   ├─> Instantiate tool class
   ├─> Call tool.execute(action.parameters)
   └─> Return result

6. Tool Execution
   ├─> Validate parameters
   ├─> Perform business logic
   └─> Return {"success": bool, "data": {...}, "message": "..."}

7. Result Collection
   ├─> Create ActionResult
   ├─> Handle success/failure
   └─> Return to workflow

8. Workflow Completion
   └─> Return ExecutionResult with all action results
```

## Summary

The DAPERL framework's tool execution pipeline is designed for:

- **Flexibility**: New domains can add tools without modifying core code
- **Discoverability**: Tools self-describe their capabilities and parameters
- **Observability**: Each action is a separate Temporal activity with full tracing
- **Reliability**: Comprehensive error handling and result tracking
- **Intelligence**: LLM-driven planning with full knowledge of available tools

This architecture allows the framework to scale to many domains while maintaining clean separation between the core orchestration logic and domain-specific tool implementations.
