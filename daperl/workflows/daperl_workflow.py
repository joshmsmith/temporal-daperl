"""Main DAPERL workflow implementation."""

from datetime import datetime, timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from daperl.core.models import (
        DAPERLInput,
        DAPERLResult,
        AgentContext,
        WorkflowStatus,
    )
    from daperl.core.types import AgentPhase
    from daperl.activities import (
        run_detection_agent,
        run_analysis_agent,
        run_planning_agent,
        run_execution_agent,
        run_reporting_agent,
        run_learning_agent,
    )


@workflow.defn
class DAPERLWorkflow:
    """
    Main DAPERL workflow that orchestrates detection, analysis, planning,
    execution, reporting, and learning phases.
    """
    
    def __init__(self):
        """Initialize the workflow."""
        self._status = WorkflowStatus.INITIALIZING
        self._detection_result = None
        self._analysis_result = None
        self._planning_result = None
        self._execution_result = None
        self._reporting_result = None
        self._learning_result = None
        self._plan_approved = False
        self._started_at = None
    
    @workflow.run
    async def run(self, input: DAPERLInput) -> DAPERLResult:
        """
        Execute the DAPERL workflow.
        
        Args:
            input: Workflow input
            
        Returns:
            Workflow result with all phase outputs
        """
        self._started_at = workflow.now()
        workflow_id = workflow.info().workflow_id
        
        workflow.logger.info(
            f"Starting DAPERL workflow for domain: {input.domain}",
            extra={"domain": input.domain, "auto_approve": input.auto_approve}
        )
        
        # Phase 0: Get the data if it isn't sent in to the workflow
        # TODO

        # Create agent context
        context = AgentContext(
            workflow_id=workflow_id,
            domain=input.domain,
            data=input.data,
            history=[],
            config=input.config,
            metadata=input.metadata
        )
        
        # Retry policy for activities
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            backoff_coefficient=2.0,
        )
        
        try:
            # Phase 1: Detection
            self._status = WorkflowStatus.DETECTING
            workflow.logger.info("Phase 1: Detection")
            
            self._detection_result = await workflow.execute_activity(
                run_detection_agent,
                context,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            
            context.history.append(self._detection_result)
            workflow.logger.info(
                f"Detection complete: {len(self._detection_result.problems)} problems found"
            )
            
            # If no problems detected, complete workflow
            if not self._detection_result.problems_detected:
                workflow.logger.info("No problems detected, completing workflow")
                self._status = WorkflowStatus.COMPLETED
                return self._build_result(workflow_id, "No problems detected")
            
            # Phase 2: Analysis
            self._status = WorkflowStatus.ANALYZING
            workflow.logger.info("Phase 2: Analysis")
            
            self._analysis_result = await workflow.execute_activity(
                run_analysis_agent,
                context,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            
            context.history.append(self._analysis_result)
            workflow.logger.info(
                f"Analysis complete: {len(self._analysis_result.root_causes)} root causes identified"
            )
            
            # Phase 3: Planning
            self._status = WorkflowStatus.PLANNING
            workflow.logger.info("Phase 3: Planning")
            
            self._planning_result = await workflow.execute_activity(
                run_planning_agent,
                context,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            
            context.history.append(self._planning_result)
            workflow.logger.info(
                f"Planning complete: {len(self._planning_result.plan.actions) if self._planning_result.plan else 0} actions planned"
            )
            
            # Phase 4: Wait for approval (if required)
            if not input.auto_approve and self._planning_result.plan:
                self._status = WorkflowStatus.PENDING_APPROVAL
                workflow.logger.info("Waiting for plan approval")
                
                # Wait for approval signal or timeout
                await workflow.wait_condition(
                    lambda: self._plan_approved,
                    timeout=timedelta(hours=24)
                )
                
                if not self._plan_approved:
                    workflow.logger.info("Plan approval timeout, cancelling workflow")
                    self._status = WorkflowStatus.CANCELLED
                    return self._build_result(workflow_id, "Plan approval timeout")
                
                workflow.logger.info("Plan approved, proceeding with execution")
            else:
                self._plan_approved = True
                workflow.logger.info("Auto-approval enabled or no plan, skipping approval")
            
            # Phase 5: Execution
            self._status = WorkflowStatus.EXECUTING
            workflow.logger.info("Phase 4: Execution")
            
            self._execution_result = await workflow.execute_activity(
                run_execution_agent,
                context,
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=retry_policy
            )
            
            context.history.append(self._execution_result)
            workflow.logger.info(
                f"Execution complete: {self._execution_result.success_count} succeeded, "
                f"{self._execution_result.failure_count} failed"
            )
            
            # Phase 6: Reporting
            self._status = WorkflowStatus.REPORTING
            workflow.logger.info("Phase 5: Reporting")
            
            self._reporting_result = await workflow.execute_activity(
                run_reporting_agent,
                context,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            
            context.history.append(self._reporting_result)
            workflow.logger.info("Reporting complete")
            
            # Phase 7: Learning
            self._status = WorkflowStatus.LEARNING
            workflow.logger.info("Phase 6: Learning")
            
            self._learning_result = await workflow.execute_activity(
                run_learning_agent,
                context,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            
            context.history.append(self._learning_result)
            workflow.logger.info(
                f"Learning complete: {len(self._learning_result.insights)} insights generated"
            )
            
            # Complete
            self._status = WorkflowStatus.COMPLETED
            workflow.logger.info("DAPERL workflow completed successfully")
            
            return self._build_result(workflow_id, "Workflow completed successfully")
            
        except Exception as e:
            workflow.logger.error(f"Workflow failed: {str(e)}")
            self._status = WorkflowStatus.FAILED
            return self._build_result(workflow_id, f"Workflow failed: {str(e)}")
    
    @workflow.signal
    def approve_plan(self):
        """Signal to approve the execution plan."""
        workflow.logger.info("Plan approval signal received")
        self._plan_approved = True
    
    @workflow.signal
    def cancel_workflow(self):
        """Signal to cancel the workflow."""
        workflow.logger.info("Cancel signal received")
        self._status = WorkflowStatus.CANCELLED
    
    @workflow.query
    def get_status(self) -> dict:
        """Query to get current workflow status."""
        return {
            "status": self._status.value,
            "detection_complete": self._detection_result is not None,
            "analysis_complete": self._analysis_result is not None,
            "planning_complete": self._planning_result is not None,
            "execution_complete": self._execution_result is not None,
            "reporting_complete": self._reporting_result is not None,
            "learning_complete": self._learning_result is not None,
            "plan_approved": self._plan_approved,
        }
    
    @workflow.query
    def get_plan(self) -> dict:
        """Query to get the current execution plan."""
        if self._planning_result and self._planning_result.plan:
            return self._planning_result.plan.model_dump()
        return None
    
    @workflow.query
    def get_results(self) -> dict:
        """Query to get all results."""
        return {
            "detection": self._detection_result.model_dump() if self._detection_result else None,
            "analysis": self._analysis_result.model_dump() if self._analysis_result else None,
            "planning": self._planning_result.model_dump() if self._planning_result else None,
            "execution": self._execution_result.model_dump() if self._execution_result else None,
            "reporting": self._reporting_result.model_dump() if self._reporting_result else None,
            "learning": self._learning_result.model_dump() if self._learning_result else None,
        }
    
    def _build_result(self, workflow_id: str, summary: str) -> DAPERLResult:
        """Build the workflow result."""
        return DAPERLResult(
            workflow_id=workflow_id,
            status=self._status,
            detection_result=self._detection_result,
            analysis_result=self._analysis_result,
            planning_result=self._planning_result,
            execution_result=self._execution_result,
            reporting_result=self._reporting_result,
            learning_result=self._learning_result,
            summary=summary,
            started_at=self._started_at,
            completed_at=workflow.now()
        )
