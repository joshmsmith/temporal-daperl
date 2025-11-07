"""Learning agent implementation."""

import json
import uuid
from datetime import datetime
from typing import Any, List

from daperl.core.agents import BaseLearningAgent
from daperl.core.models import (
    AgentContext,
    LearningResult,
    LearningInsight,
    DetectionResult,
    AnalysisResult,
    PlanningResult,
    ExecutionResult,
    ReportingResult,
    ExecutionMetric,
)
from daperl.llm.base import LLMMessage


class LearningAgent(BaseLearningAgent):
    """
    Agent that learns from workflow executions to improve future performance.
    
    This agent:
    - Stores execution metrics
    - Identifies patterns across executions
    - Provides recommendations for improvement
    - Adjusts detection thresholds based on outcomes
    
    This is a generic implementation that can be extended for specific domains.
    """
    
    def __init__(self, storage=None, **kwargs):
        """
        Initialize the learning agent.
        
        Args:
            storage: Storage backend for learning data
            **kwargs: Additional arguments for base agent
        """
        super().__init__(**kwargs)
        self.storage = storage
    
    async def execute(self, context: AgentContext) -> LearningResult:
        """
        Learn from the workflow execution.
        
        Args:
            context: The agent context with all phase results
            
        Returns:
            Learning result with insights and patterns
        """
        if not self.llm_client:
            raise ValueError("LLM client not configured for LearningAgent")
        
        # Gather current execution metrics
        current_metrics = self._gather_execution_metrics(context)
        
        # Store current execution
        if self.storage:
            await self.storage.store_metric(current_metrics)
        
        # Retrieve historical executions for analysis
        historical_metrics = []
        if self.storage:
            historical_metrics = await self.storage.get_recent_metrics(limit=10)
        
        # Build learning prompt
        system_prompt = self._build_system_prompt(context)
        user_message = self._build_user_message(context, current_metrics, historical_metrics)
        
        messages = [LLMMessage(role="user", content=user_message)]
        
        # Get learning insights from LLM
        response = await self.llm_client.complete_with_json(
            messages=messages,
            system_prompt=system_prompt
        )
        
        # Validate and parse response
        if not self.validate_output(response):
            raise ValueError(f"Invalid learning output: {response}")
        
        # Parse insights
        insights = []
        for insight_data in response.get("insights", []):
            insight = LearningInsight(
                id=insight_data.get("id", str(uuid.uuid4())),
                insight_type=insight_data.get("type", "general"),
                description=insight_data.get("description", ""),
                confidence=insight_data.get("confidence", 0.5),
                supporting_executions=[context.workflow_id]
            )
            insights.append(insight)
        
        # Store insights
        if self.storage:
            for insight in insights:
                await self.storage.store_insight(insight)
        
        confidence = response.get("confidence", 0.7)
        
        return LearningResult(
            success=True,
            message=f"Learning complete: {len(insights)} insights generated",
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            insights=insights,
            patterns_found=response.get("patterns_found", 0),
            recommendations=response.get("recommendations", []),
            learning_summary=response.get("summary", "Learning analysis complete")
        )
    
    def validate_output(self, output: Any) -> bool:
        """
        Validate the learning output.
        
        Args:
            output: The output to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(output, dict):
            return False
        
        required_fields = ["insights", "recommendations", "confidence"]
        for field in required_fields:
            if field not in output:
                return False
        
        if not isinstance(output["insights"], list):
            return False
        if not isinstance(output["recommendations"], list):
            return False
        
        return True
    
    def _gather_execution_metrics(self, context: AgentContext) -> ExecutionMetric:
        """Gather metrics from the current execution."""
        detection_result = self._get_result(context, DetectionResult)
        analysis_result = self._get_result(context, AnalysisResult)
        planning_result = self._get_result(context, PlanningResult)
        execution_result = self._get_result(context, ExecutionResult)
        reporting_result = self._get_result(context, ReportingResult)
        
        # Determine overall success
        overall_success = True
        if execution_result:
            overall_success = execution_result.success and execution_result.failure_count == 0
        
        return ExecutionMetric(
            workflow_id=context.workflow_id,
            timestamp=datetime.utcnow(),
            domain=context.domain,
            detection_result=detection_result,
            analysis_result=analysis_result,
            planning_result=planning_result,
            execution_result=execution_result,
            reporting_result=reporting_result,
            overall_success=overall_success
        )
    
    def _get_result(self, context: AgentContext, result_type):
        """Extract specific result type from context history."""
        for result in context.history:
            if isinstance(result, result_type):
                return result
        return None
    
    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build the system prompt for learning."""
        return f"""You are a learning agent for the {context.domain} domain.

Your task is to analyze workflow executions and extract insights that can improve future performance.

Consider:
- What patterns emerge across executions?
- Are detection thresholds appropriate?
- Are certain problem types consistently resolved?
- Are there recurring failures or issues?
- What can be improved in future executions?

Respond with a JSON object in this format:
{{
    "insights": [
        {{
            "id": "insight-id",
            "type": "detection|analysis|planning|execution|general",
            "description": "description of the insight",
            "confidence": 0.0-1.0
        }}
    ],
    "patterns_found": 0,
    "recommendations": ["list of recommendations for improvement"],
    "confidence": 0.0-1.0,
    "summary": "brief summary of learning analysis"
}}"""
    
    def _build_user_message(
        self,
        context: AgentContext,
        current_metrics: ExecutionMetric,
        historical_metrics: List[ExecutionMetric]
    ) -> str:
        """Build the user message with execution metrics."""
        message = f"""Domain: {context.domain}

## Current Execution
Workflow ID: {current_metrics.workflow_id}
Success: {current_metrics.overall_success}

"""
        
        # Add current execution details
        if current_metrics.detection_result:
            message += f"""Detection:
- Problems found: {len(current_metrics.detection_result.problems)}
- Confidence: {current_metrics.detection_result.confidence}

"""
        
        if current_metrics.execution_result:
            message += f"""Execution:
- Actions executed: {len(current_metrics.execution_result.actions_executed)}
- Success rate: {current_metrics.execution_result.success_count}/{len(current_metrics.execution_result.actions_executed)}

"""
        
        # Add historical context if available
        if historical_metrics:
            message += f"""## Historical Executions ({len(historical_metrics)} recent)

"""
            for i, metric in enumerate(historical_metrics, 1):
                success_str = "✓" if metric.overall_success else "✗"
                problems = len(metric.detection_result.problems) if metric.detection_result else 0
                message += f"""{i}. {metric.workflow_id} {success_str}
   - Problems detected: {problems}
   - Overall success: {metric.overall_success}
"""
        
        message += "\nAnalyze these executions and provide learning insights and recommendations."
        
        return message
