"""Execution agent implementation."""

from temporalio import activity
from typing import Any, Dict, Callable

from daperl.core.agents import BaseExecutionAgent
from daperl.core.models import (
    AgentContext,
    ExecutionResult,
    PlanningResult,
    ActionResult,
)
from daperl.llm.base import LLMMessage


class ExecutionAgent(BaseExecutionAgent):
    """
    Agent that executes planned actions.
    
    This is a generic implementation that can be extended for specific domains.
    The actual execution tools should be provided via context.config.
    """
    
    def __init__(self, action_registry: Dict[str, Callable] = None, **kwargs):
        """
        Initialize the execution agent.
        
        Args:
            action_registry: Dictionary mapping action types to callable functions
            **kwargs: Additional arguments for base agent
        """
        super().__init__(**kwargs)
        self.action_registry = action_registry or {}
    
    async def execute(self, context: AgentContext) -> ExecutionResult:
        """
        Execute the planned actions.
        
        Args:
            context: The agent context with execution plan
            
        Returns:
            Execution result with action outcomes
        """
        
        activity.logger.info(f"In Execution agent, action_registry keys: {list(self.action_registry.keys())}")

        # Get planning results from history
        planning_result = self._get_planning_result(context)
        if not planning_result or not planning_result.plan:
            return ExecutionResult(
                success=True,
                message="No plan to execute",
                confidence=1.0,
                confidence_level="very_high",
                plan_id="none",
                execution_summary="No plan found, no execution needed"
            )
        
        plan = planning_result.plan
        actions_executed = []
        success_count = 0
        failure_count = 0
        
        # Execute each action in the plan
        for action in plan.actions:
            try:
                # Check if we have a handler for this action type
                if action.action_type in self.action_registry:
                    # Execute using registered handler
                    handler = self.action_registry[action.action_type]
                    result = await handler(action, context)
                    
                    action_result = ActionResult(
                        action_id=action.id,
                        success=result.get("success", True),
                        message=result.get("message", f"Executed {action.action_type}"),
                        data=result.get("data", {})
                    )
                else:
                    # No handler registered - fail the action
                    activity.logger.error(f"No handler registered for action type: {action.action_type}")
                    action_result = ActionResult(
                        action_id=action.id,
                        success=False,
                        message=f"No handler registered for action type: {action.action_type}",
                        error=f"Action type '{action.action_type}' requires a registered handler in action_registry"
                    )
                
                if action_result.success:
                    success_count += 1
                else:
                    failure_count += 1
                
                actions_executed.append(action_result)
                
            except Exception as e:
                failure_count += 1
                actions_executed.append(
                    ActionResult(
                        action_id=action.id,
                        success=False,
                        message=f"Execution failed: {str(e)}",
                        error=str(e)
                    )
                )
        
        overall_success = failure_count == 0
        confidence = success_count / len(actions_executed) if actions_executed else 0.0
        
        return ExecutionResult(
            success=overall_success,
            message=f"Execution complete: {success_count} succeeded, {failure_count} failed",
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            plan_id=plan.id,
            actions_executed=actions_executed,
            success_count=success_count,
            failure_count=failure_count,
            execution_summary=f"Executed {len(actions_executed)} actions with {success_count} successes"
        )

    def validate_output(self, output: Any) -> bool:
        """
        Validate the execution output.
        
        Args:
            output: The output to validate
            
        Returns:
            True if valid, False otherwise
        """
        # For execution, we validate individual action results
        if isinstance(output, ActionResult):
            return True
        return False
    
    def _get_planning_result(self, context: AgentContext) -> PlanningResult:
        """Extract planning result from context history."""
        for result in context.history:
            if isinstance(result, PlanningResult):
                return result
        return None
