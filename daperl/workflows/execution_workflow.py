"""Execution Agent Child Workflow implementation."""

from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from daperl.core.models import (
        AgentContext,
        ExecutionResult,
        PlanningResult,
        ActionResult,
        Action,
    )
    from daperl.core.exceptions import ActionExecutionError
    from daperl.activities import execute_action_activity


@workflow.defn
class ExecutionAgentWorkflow:
    """
    Child workflow that executes planned actions.
    
    Each action in the plan is executed as a separate activity,
    providing better visibility and tracing in Temporal.
    """
    
    def __init__(self):
        """Initialize the execution workflow."""
        self._actions_executed = []
        self._success_count = 0
        self._failure_count = 0
    
    @workflow.run
    async def run(self, context: AgentContext) -> ExecutionResult:
        """
        Execute all actions in the plan.
        
        Args:
            context: The agent context with execution plan in history
            
        Returns:
            Execution result with action outcomes
        """
        workflow.logger.info("Starting Execution Agent Workflow")
        
        # Get planning results from history
        planning_result = self._get_planning_result(context)
        if not planning_result or not planning_result.plan:
            workflow.logger.info("No plan to execute")
            return ExecutionResult(
                success=True,
                message="No plan to execute",
                confidence=1.0,
                confidence_level="very_high",
                plan_id="none",
                execution_summary="No plan found, no execution needed"
            )
        
        plan = planning_result.plan
        workflow.logger.info(f"Executing plan with {len(plan.actions)} actions")
        
        # Retry policy for action execution activities
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            backoff_coefficient=2.0,
        )
        
        # Execute each action in the plan as a separate activity
        for action in plan.actions:
            workflow.logger.info(f"Executing action: {action.id} ({action.action_type})")
            
            try:
                # Execute this action as a separate activity
                action_result = await workflow.execute_activity(
                    execute_action_activity,
                    args=[action, context],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=retry_policy
                )
                
                # Note: we won't reach here if action fails, as activity now raises ActionExecutionError
                self._success_count += 1
                workflow.logger.info(f"Action {action.id} succeeded")
                self._actions_executed.append(action_result)
                
            except ActionExecutionError as e:
                # Action execution failed - extract the ActionResult from the exception
                self._failure_count += 1
                action_result = e.action_result
                workflow.logger.warning(
                    f"Action {action.id} failed: {action_result.message}",
                    extra={"error": action_result.error}
                )
                self._actions_executed.append(action_result)
                
            except Exception as e:
                # Unexpected exception (not ActionExecutionError)
                self._failure_count += 1
                error_message = str(e)
                workflow.logger.error(f"Action {action.id} execution failed with unexpected error: {error_message}")
                
                self._actions_executed.append(
                    ActionResult(
                        action_id=action.id,
                        success=False,
                        message=f"Unexpected execution failure: {error_message}",
                        error=error_message
                    )
                )
        
        # Calculate overall results
        overall_success = self._failure_count == 0
        confidence = self._success_count / len(self._actions_executed) if self._actions_executed else 0.0
        
        workflow.logger.info(
            f"Execution complete: {self._success_count} succeeded, {self._failure_count} failed"
        )
        
        return ExecutionResult(
            success=overall_success,
            message=f"Execution complete: {self._success_count} succeeded, {self._failure_count} failed",
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            plan_id=plan.id,
            actions_executed=self._actions_executed,
            success_count=self._success_count,
            failure_count=self._failure_count,
            execution_summary=f"Executed {len(self._actions_executed)} actions with {self._success_count} successes"
        )
    
    def _get_planning_result(self, context: AgentContext) -> PlanningResult:
        """Extract planning result from context history."""
        for result in context.history:
            if isinstance(result, PlanningResult):
                return result
        return None
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level."""
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.7:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        elif confidence >= 0.3:
            return "low"
        else:
            return "very_low"
