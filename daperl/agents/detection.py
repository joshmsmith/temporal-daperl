"""Detection agent implementation."""

import json
import uuid
from typing import Any

from daperl.core.agents import BaseDetectionAgent
from daperl.core.models import AgentContext, DetectionResult, Problem
from daperl.llm.base import LLMMessage


class DetectionAgent(BaseDetectionAgent):
    """
    Agent that detects problems in the system.
    
    This is a generic implementation that can be extended for specific domains.
    """
    
    async def execute(self, context: AgentContext) -> DetectionResult:
        """
        Detect problems in the given context.
        
        Args:
            context: The agent context with domain data
            
        Returns:
            Detection result with identified problems
        """
        if not self.llm_client:
            raise ValueError("LLM client not configured for DetectionAgent")
        
        # Build detection prompt
        system_prompt = self._build_system_prompt(context)
        user_message = self._build_user_message(context)
        
        messages = [LLMMessage(role="user", content=user_message)]
        
        # Get detection from LLM
        response = await self.llm_client.complete_with_json(
            messages=messages,
            system_prompt=system_prompt
        )
        
        # Validate and parse response
        if not self.validate_output(response):
            raise ValueError(f"Invalid detection output: {response}")
        
        # Extract problems
        problems = []
        for p in response.get("problems", []):
            problem = Problem(
                id=p.get("id", str(uuid.uuid4())),
                type=p.get("type", "unknown"),
                description=p.get("description", ""),
                severity=p.get("severity", "medium"),
                data=p.get("data", {})
            )
            problems.append(problem)
        
        confidence = response.get("confidence", 0.7)
        
        return DetectionResult(
            success=True,
            message=f"Detection complete: {len(problems)} problems found",
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            problems_detected=len(problems) > 0,
            problems=problems,
            summary=response.get("summary", f"Found {len(problems)} problems")
        )
    
    def validate_output(self, output: Any) -> bool:
        """
        Validate the detection output.
        
        Args:
            output: The output to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(output, dict):
            return False
        
        # Must have problems list and confidence
        if "problems" not in output or "confidence" not in output:
            return False
        
        if not isinstance(output["problems"], list):
            return False
        
        # Validate each problem has required fields
        for problem in output["problems"]:
            if not isinstance(problem, dict):
                return False
            if "type" not in problem or "description" not in problem:
                return False
        
        return True
    
    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build the system prompt for detection."""
        return f"""You are a detection agent for the {context.domain} domain.

Your task is to analyze the provided data and detect any problems or issues that need attention.

Respond with a JSON object in this format:
{{
    "problems": [
        {{
            "id": "unique-id",
            "type": "problem_type",
            "description": "description of the problem",
            "severity": "low|medium|high|critical",
            "data": {{}} // additional problem-specific data
        }}
    ],
    "confidence": 0.0-1.0,
    "summary": "brief summary of findings"
}}

If no problems are found, return an empty problems array with confidence and summary."""
    
    def _build_user_message(self, context: AgentContext) -> str:
        """Build the user message with domain data."""
        data_str = json.dumps(context.data, indent=2)
        
        message = f"""Domain: {context.domain}

Data to analyze:
{data_str}

Analyze this data and detect any problems or issues that need attention."""
        
        # Include any domain-specific instructions from config
        if "detection_instructions" in context.config:
            message += f"\n\nAdditional instructions:\n{context.config['detection_instructions']}"
        
        return message
