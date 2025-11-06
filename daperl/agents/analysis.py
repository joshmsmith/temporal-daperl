"""Analysis agent implementation."""

import json
from typing import Any

from daperl.core.agents import BaseAnalysisAgent
from daperl.core.models import AgentContext, AnalysisResult, DetectionResult, Problem
from daperl.llm.base import LLMMessage


class AnalysisAgent(BaseAnalysisAgent):
    """
    Agent that analyzes detected problems to find root causes.
    
    This is a generic implementation that can be extended for specific domains.
    """
    
    async def execute(self, context: AgentContext) -> AnalysisResult:
        """
        Analyze detected problems.
        
        Args:
            context: The agent context with detection results
            
        Returns:
            Analysis result with root causes and recommendations
        """
        if not self.llm_client:
            raise ValueError("LLM client not configured for AnalysisAgent")
        
        # Get detection results from history
        detection_result = self._get_detection_result(context)
        if not detection_result or not detection_result.problems:
            return AnalysisResult(
                success=True,
                message="No problems to analyze",
                confidence=1.0,
                confidence_level="very_high",
                analysis_summary="No problems detected, no analysis needed"
            )
        
        # Build analysis prompt
        system_prompt = self._build_system_prompt(context)
        user_message = self._build_user_message(context, detection_result)
        
        messages = [LLMMessage(role="user", content=user_message)]
        
        # Get analysis from LLM
        response = await self.llm_client.complete_with_json(
            messages=messages,
            system_prompt=system_prompt
        )
        
        # Validate and parse response
        if not self.validate_output(response):
            raise ValueError(f"Invalid analysis output: {response}")
        
        confidence = response.get("confidence", 0.7)
        
        return AnalysisResult(
            success=True,
            message=f"Analysis complete: {len(response.get('root_causes', []))} root causes identified",
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            analyzed_problems=detection_result.problems,
            root_causes=response.get("root_causes", []),
            recommendations=response.get("recommendations", []),
            analysis_summary=response.get("summary", "Analysis complete")
        )
    
    def validate_output(self, output: Any) -> bool:
        """
        Validate the analysis output.
        
        Args:
            output: The output to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(output, dict):
            return False
        
        required_fields = ["root_causes", "recommendations", "confidence"]
        for field in required_fields:
            if field not in output:
                return False
        
        if not isinstance(output["root_causes"], list):
            return False
        if not isinstance(output["recommendations"], list):
            return False
        
        return True
    
    def _get_detection_result(self, context: AgentContext) -> DetectionResult:
        """Extract detection result from context history."""
        for result in context.history:
            if isinstance(result, DetectionResult):
                return result
        return None
    
    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build the system prompt for analysis."""
        return f"""You are an analysis agent for the {context.domain} domain.

Your task is to analyze detected problems and identify root causes and provide recommendations.

Respond with a JSON object in this format:
{{
    "root_causes": ["list of identified root causes"],
    "recommendations": ["list of recommendations for addressing the issues"],
    "confidence": 0.0-1.0,
    "summary": "brief summary of the analysis"
}}"""
    
    def _build_user_message(self, context: AgentContext, detection_result: DetectionResult) -> str:
        """Build the user message with detected problems."""
        problems_str = json.dumps([p.model_dump() for p in detection_result.problems], indent=2)
        data_str = json.dumps(context.data, indent=2)
        
        message = f"""Domain: {context.domain}

Detected Problems:
{problems_str}

Context Data:
{data_str}

Analyze these problems, identify root causes, and provide recommendations."""
        
        # Include any domain-specific instructions from config
        if "analysis_instructions" in context.config:
            message += f"\n\nAdditional instructions:\n{context.config['analysis_instructions']}"
        
        return message
