"""Activity wrappers for DAPERL agents."""

from temporalio import activity
import importlib
import sys
from pathlib import Path

from daperl.core.models import (
    AgentContext,
    DetectionResult,
    AnalysisResult,
    PlanningResult,
    ExecutionResult,
    ReportingResult,
    LearningResult,
    Action,
    ActionResult,
)
from daperl.agents import (
    DetectionAgent,
    AnalysisAgent,
    PlanningAgent,
    ReportingAgent,
    LearningAgent,
)
from daperl.config.settings import settings
from daperl.storage.json_storage import JSONLearningStorage


def _load_domain_tools(context: AgentContext) -> None:
    """
    Load and register domain-specific tools.
    
    This function dynamically imports and registers tools for the given domain.
    Convention: examples/{domain}/tools.py should have register_{domain}_tools() function.
    
    Args:
        context: Agent context containing domain information
    """
    try:
        # Convert domain to module-friendly format (e.g., "customer-support" -> "customer_support")
        domain_module = context.domain.replace("-", "_")
        
        # Add examples directory to path if not already there
        project_root = Path(__file__).parent.parent.parent
        examples_path = project_root / "examples"
        if str(examples_path) not in sys.path:
            sys.path.insert(0, str(examples_path))
        
        activity.logger.info(
            f"Added examples path to sys.path: {examples_path}",
            extra={"exists": examples_path.exists()}
        )
        
        # Import the domain's tools module
        tools_module_name = f"{domain_module}.tools"
        activity.logger.info(f"Attempting to load tools module: {tools_module_name}")
        tools_module = importlib.import_module(tools_module_name)
        
        # Look for register function
        register_func_name = f"register_{domain_module}_tools"
        if hasattr(tools_module, register_func_name):
            register_func = getattr(tools_module, register_func_name)
            register_func(domain=context.domain)
            activity.logger.info(f"Registered tools for domain: {context.domain}")
        else:
            activity.logger.warning(
                f"Tools module found but no {register_func_name} function",
                extra={"module": tools_module_name}
            )
    except ImportError as e:
        activity.logger.warning(
            f"Could not import tools module for domain {context.domain}: {e}",
            extra={"domain": context.domain}
        )
    except Exception as e:
        activity.logger.warning(
            f"Error loading tools for domain {context.domain}: {e}",
            extra={"domain": context.domain}
        )


@activity.defn
async def run_detection_agent(context: AgentContext) -> DetectionResult:
    """
    Run the detection agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Detection result
    """
    activity.logger.info("Starting detection agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = DetectionAgent(llm_config=daperl_config.detection_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Detection complete",
        extra={
            "problems_found": len(result.problems),
            "confidence": result.confidence
        }
    )
    
    return result


@activity.defn
async def run_analysis_agent(context: AgentContext) -> AnalysisResult:
    """
    Run the analysis agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Analysis result
    """
    activity.logger.info("Starting analysis agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = AnalysisAgent(llm_config=daperl_config.analysis_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Analysis complete",
        extra={
            "root_causes": len(result.root_causes),
            "confidence": result.confidence
        }
    )
    
    return result


@activity.defn
async def run_planning_agent(context: AgentContext) -> PlanningResult:
    """
    Run the planning agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Planning result
    """
    activity.logger.info("Starting planning agent", extra={"domain": context.domain})
    
    # Load domain tools so Planning agent can access tool parameter information
    if context.config.get("available_actions"):
        _load_domain_tools(context)
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = PlanningAgent(llm_config=daperl_config.planning_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Planning complete",
        extra={
            "actions_planned": len(result.plan.actions) if result.plan else 0,
            "confidence": result.confidence
        }
    )
    
    return result


@activity.defn
async def execute_action_activity(action: Action, context: AgentContext) -> ActionResult:
    """
    Execute a single action as a Temporal activity.
    
    This activity is called by the ExecutionAgentWorkflow for each action
    in the execution plan, providing better visibility and tracing.
    
    Args:
        action: The action to execute
        context: Agent context
        
    Returns:
        Action result
    """
    activity.logger.info(
        f"Executing action: {action.id} ({action.action_type})",
        extra={"domain": context.domain, "action_type": action.action_type}
    )
    
    # Build action registry from available actions in config
    from daperl.core.tools import ToolRegistry
    
    available_actions = context.config.get("available_actions", [])
    
    if not available_actions:
        activity.logger.error("No available_actions specified in config")
        return ActionResult(
            action_id=action.id,
            success=False,
            message="No available_actions configured",
            error="Configuration missing available_actions"
        )
    
    # Load domain tools
    _load_domain_tools(context)
    
    # Build action registry from registered tools
    action_registry = ToolRegistry.create_action_registry(
        available_actions=available_actions,
        domain=context.domain
    )
    
    activity.logger.info(
        f"Action registry created with {len(action_registry)} handlers",
        extra={"handlers": list(action_registry.keys())}
    )
    
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
            
            activity.logger.info(
                f"Action {action.id} executed successfully",
                extra={"success": action_result.success}
            )
            
            return action_result
        else:
            # No handler registered - fail the action
            activity.logger.error(
                f"No handler registered for action type: {action.action_type}",
                extra={"action_type": action.action_type, "available": list(action_registry.keys())}
            )
            return ActionResult(
                action_id=action.id,
                success=False,
                message=f"No handler registered for action type: {action.action_type}",
                error=f"Action type '{action.action_type}' requires a registered handler in action_registry"
            )
    
    except Exception as e:
        activity.logger.error(
            f"Action execution failed: {str(e)}",
            extra={"action_id": action.id, "action_type": action.action_type}
        )
        return ActionResult(
            action_id=action.id,
            success=False,
            message=f"Execution failed: {str(e)}",
            error=str(e)
        )


@activity.defn
async def run_reporting_agent(context: AgentContext) -> ReportingResult:
    """
    Run the reporting agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Reporting result
    """
    activity.logger.info("Starting reporting agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = ReportingAgent(llm_config=daperl_config.reporting_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Reporting complete",
        extra={"confidence": result.confidence}
    )
    
    return result


@activity.defn
async def run_learning_agent(context: AgentContext) -> LearningResult:
    """
    Run the learning agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Learning result
    """
    activity.logger.info("Starting learning agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    learning_config = settings.get_learning_config()
    
    # Create storage backend
    storage = None
    if learning_config.storage_type == "json":
        storage = JSONLearningStorage(learning_config.storage_path)
    
    # Create and run agent
    agent = LearningAgent(
        llm_config=daperl_config.learning_llm,
        storage=storage
    )
    result = await agent.execute(context)
    
    activity.logger.info(
        "Learning complete",
        extra={
            "insights_generated": len(result.insights),
            "patterns_found": result.patterns_found,
            "confidence": result.confidence
        }
    )
    
    return result
