"""Reporting agent implementation."""

import json
from typing import Any

from daperl.core.agents import BaseReportingAgent
from daperl.core.models import (
    AgentContext,
    ReportingResult,
    DetectionResult,
    AnalysisResult,
    PlanningResult,
    ExecutionResult,
)
from daperl.llm.base import LLMMessage


class ReportingAgent(BaseReportingAgent):
    """
    Agent that generates reports of the workflow execution.
    
    This is a generic implementation that can be extended for specific domains.
    """
    
    async def execute(self, context: AgentContext) -> ReportingResult:
        """
        Generate a report of the workflow execution.
        
        Args:
            context: The agent context with all phase results
            
        Returns:
            Reporting result with summary and metrics
        """
        if not self.llm_client:
            raise ValueError("LLM client not configured for ReportingAgent")
        
        # Gather results from all phases
        detection_result = self._get_result(context, DetectionResult)
        analysis_result = self._get_result(context, AnalysisResult)
        planning_result = self._get_result(context, PlanningResult)
        execution_result = self._get_result(context, ExecutionResult)
        
        # Build reporting prompt
        system_prompt = self._build_system_prompt(context)
        user_message = self._build_user_message(
            context,
            detection_result,
            analysis_result,
            planning_result,
            execution_result
        )
        
        messages = [LLMMessage(role="user", content=user_message)]
        
        # Get report from LLM
        response = await self.llm_client.complete_with_json(
            messages=messages,
            system_prompt=system_prompt
        )
        
        # Validate and parse response
        if not self.validate_output(response):
            raise ValueError(f"Invalid reporting output: {response}")
        
        confidence = response.get("confidence", 0.8)
        
        return ReportingResult(
            success=True,
            message="Report generated successfully",
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            report=response.get("report", ""),
            metrics=response.get("metrics", {}),
            recommendations=response.get("recommendations", [])
        )
    
    def validate_output(self, output: Any) -> bool:
        """
        Validate the reporting output.
        
        Args:
            output: The output to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(output, dict):
            return False
        
        required_fields = ["report", "metrics", "confidence"]
        for field in required_fields:
            if field not in output:
                return False
        
        if not isinstance(output["metrics"], dict):
            return False
        
        return True
    
    def _get_result(self, context: AgentContext, result_type):
        """Extract specific result type from context history."""
        for result in context.history:
            if isinstance(result, result_type):
                return result
        return None
    
    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build the system prompt for reporting."""
        return f"""You are a reporting agent for the {context.domain} domain.

Your task is to generate a comprehensive report of the DAPERL workflow execution,
including what was detected, analyzed, planned, and executed.

Respond with a JSON object in this format:
{{
    "report": "A comprehensive markdown-formatted report of the entire workflow",
    "metrics": {{
        "problems_detected": 0,
        "problems_resolved": 0,
        "actions_executed": 0,
        "success_rate": 0.0,
        "total_duration": "duration string"
    }},
    "recommendations": ["list of recommendations for future improvements"],
    "confidence": 0.0-1.0
}}

The report should be clear, concise, and actionable."""
    
    def _build_user_message(
        self,
        context: AgentContext,
        detection_result: DetectionResult,
        analysis_result: AnalysisResult,
        planning_result: PlanningResult,
        execution_result: ExecutionResult
    ) -> str:
        """Build the user message with all phase results."""
        message = f"""Domain: {context.domain}
Workflow ID: {context.workflow_id}

"""
        
        # Detection phase
        if detection_result:
            message += f"""## Detection Phase
- Problems detected: {len(detection_result.problems)}
- Confidence: {detection_result.confidence}
- Summary: {detection_result.summary}

Problems:
{json.dumps([p.model_dump() for p in detection_result.problems], indent=2)}

"""
        
        # Analysis phase
        if analysis_result:
            message += f"""## Analysis Phase
- Root causes identified: {len(analysis_result.root_causes)}
- Confidence: {analysis_result.confidence}
- Summary: {analysis_result.analysis_summary}

Root Causes:
{json.dumps(analysis_result.root_causes, indent=2)}

Recommendations:
{json.dumps(analysis_result.recommendations, indent=2)}

"""
        
        # Planning phase
        if planning_result and planning_result.plan:
            message += f"""## Planning Phase
- Actions planned: {len(planning_result.plan.actions)}
- Confidence: {planning_result.confidence}
- Summary: {planning_result.planning_summary}

Plan:
{json.dumps(planning_result.plan.model_dump(), indent=2)}

"""
        
        # Execution phase
        if execution_result:
            message += f"""## Execution Phase
- Actions executed: {len(execution_result.actions_executed)}
- Successful: {execution_result.success_count}
- Failed: {execution_result.failure_count}
- Confidence: {execution_result.confidence}
- Summary: {execution_result.execution_summary}

Action Results:
{json.dumps([a.model_dump() for a in execution_result.actions_executed], indent=2)}

"""
        
        message += "\nGenerate a comprehensive report of this workflow execution."
        
        return message
