"""Execution agent implementation."""

import json
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
                    # Use LLM to simulate/describe execution
                    action_result = await self._simulate_execution(action, context)
                
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
    
    async def _simulate_execution(self, action, context: AgentContext) -> ActionResult:
        """
        Simulate action execution using LLM when no handler is registered.
        
        This is useful for testing or when domain-specific handlers aren't provided.
        """
        if not self.llm_client:
            return ActionResult(
                action_id=action.id,
                success=True,
                message=f"Simulated execution of {action.action_type} (no LLM configured)",
                data={"simulated": True}
            )
        
        system_prompt = f"""You are an execution simulation agent for the {context.domain} domain.

Describe what would happen if this action were executed. Provide a realistic outcome.

Respond with JSON:
{{
    "success": true/false,
    "message": "description of what happened",
    "data": {{}} // any relevant data from the execution
}}"""
        
        user_message = f"""Action to execute:
Type: {action.action_type}
Description: {action.description}
Target: {action.target}
Parameters: {json.dumps(action.parameters, indent=2)}

Simulate the execution and describe the outcome."""
        
        messages = [LLMMessage(role="user", content=user_message)]
        
        response = await self.llm_client.complete_with_json(
            messages=messages,
            system_prompt=system_prompt
        )
        
        return ActionResult(
            action_id=action.id,
            success=response.get("success", True),
            message=response.get("message", "Action simulated"),
            data=response.get("data", {"simulated": True})
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
