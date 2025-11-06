"""Planning agent implementation."""

import json
import uuid
from typing import Any

from daperl.core.agents import BasePlanningAgent
from daperl.core.models import (
    AgentContext,
    PlanningResult,
    AnalysisResult,
    ExecutionPlan,
    Action,
)
from daperl.llm.base import LLMMessage


class PlanningAgent(BasePlanningAgent):
    """
    Agent that creates execution plans based on analysis.
    
    This is a generic implementation that can be extended for specific domains.
    """
    
    async def execute(self, context: AgentContext) -> PlanningResult:
        """
        Create an execution plan based on analysis.
        
        Args:
            context: The agent context with analysis results
            
        Returns:
            Planning result with execution plan
        """
        if not self.llm_client:
            raise ValueError("LLM client not configured for PlanningAgent")
        
        # Get analysis results from history
        analysis_result = self._get_analysis_result(context)
        if not analysis_result or not analysis_result.analyzed_problems:
            return PlanningResult(
                success=True,
                message="No problems to plan for",
                confidence=1.0,
                confidence_level="very_high",
                planning_summary="No problems found, no planning needed"
            )
        
        # Build planning prompt
        system_prompt = self._build_system_prompt(context)
        user_message = self._build_user_message(context, analysis_result)
        
        messages = [LLMMessage(role="user", content=user_message)]
        
        # Get plan from LLM
        response = await self.llm_client.complete_with_json(
            messages=messages,
            system_prompt=system_prompt
        )
        
        # Validate and parse response
        if not self.validate_output(response):
            raise ValueError(f"Invalid planning output: {response}")
        
        # Parse the plan
        plan = self._parse_plan(response.get("plan", {}))
        
        # Parse alternatives
        alternatives = []
        for alt in response.get("alternatives", []):
            alternatives.append(self._parse_plan(alt))
        
        confidence = response.get("confidence", 0.7)
        
        return PlanningResult(
            success=True,
            message=f"Plan created with {len(plan.actions)} actions",
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            plan=plan,
            alternatives=alternatives,
            planning_summary=response.get("summary", "Planning complete")
        )
    
    def validate_output(self, output: Any) -> bool:
        """
        Validate the planning output.
        
        Args:
            output: The output to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(output, dict):
            return False
        
        if "plan" not in output or "confidence" not in output:
            return False
        
        plan = output["plan"]
        if not isinstance(plan, dict) or "actions" not in plan:
            return False
        
        if not isinstance(plan["actions"], list):
            return False
        
        # Validate each action has required fields
        for action in plan["actions"]:
            if not isinstance(action, dict):
                return False
            required_fields = ["action_type", "description", "target"]
            if not all(field in action for field in required_fields):
                return False
        
        return True
    
    def _parse_plan(self, plan_data: dict) -> ExecutionPlan:
        """Parse plan data into ExecutionPlan model."""
        actions = []
        for action_data in plan_data.get("actions", []):
            action = Action(
                id=action_data.get("id", str(uuid.uuid4())),
                action_type=action_data.get("action_type", "unknown"),
                description=action_data.get("description", ""),
                target=action_data.get("target", ""),
                parameters=action_data.get("parameters", {}),
                confidence=action_data.get("confidence", 0.7),
                requires_approval=action_data.get("requires_approval", True)
            )
            actions.append(action)
        
        return ExecutionPlan(
            id=plan_data.get("id", str(uuid.uuid4())),
            actions=actions,
            estimated_duration=plan_data.get("estimated_duration"),
            risk_level=plan_data.get("risk_level", "medium"),
            requires_approval=plan_data.get("requires_approval", True)
        )
    
    def _get_analysis_result(self, context: AgentContext) -> AnalysisResult:
        """Extract analysis result from context history."""
        for result in context.history:
            if isinstance(result, AnalysisResult):
                return result
        return None
    
    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build the system prompt for planning."""
        return f"""You are a planning agent for the {context.domain} domain.

Your task is to create an execution plan to address the analyzed problems.

Respond with a JSON object in this format:
{{
    "plan": {{
        "id": "plan-id",
        "actions": [
            {{
                "id": "action-id",
                "action_type": "type_of_action",
                "description": "what this action does",
                "target": "what/who this action targets",
                "parameters": {{}},
                "confidence": 0.0-1.0,
                "requires_approval": true/false
            }}
        ],
        "estimated_duration": "estimated time",
        "risk_level": "low|medium|high",
        "requires_approval": true/false
    }},
    "alternatives": [],  // optional alternative plans
    "confidence": 0.0-1.0,
    "summary": "brief summary of the plan"
}}

Consider:
- What actions are needed to fix the problems
- The order of actions
- Dependencies between actions
- Risk level and approval requirements"""
    
    def _build_user_message(self, context: AgentContext, analysis_result: AnalysisResult) -> str:
        """Build the user message with analysis results."""
        problems_str = json.dumps([p.model_dump() for p in analysis_result.analyzed_problems], indent=2)
        
        message = f"""Domain: {context.domain}

Problems:
{problems_str}

Root Causes:
{json.dumps(analysis_result.root_causes, indent=2)}

Recommendations:
{json.dumps(analysis_result.recommendations, indent=2)}

Context Data:
{json.dumps(context.data, indent=2)}

Create a detailed execution plan to address these problems."""
        
        # Include any available tools/actions from config
        if "available_actions" in context.config:
            message += f"\n\nAvailable Actions:\n{json.dumps(context.config['available_actions'], indent=2)}"
        
        # Include any domain-specific instructions from config
        if "planning_instructions" in context.config:
            message += f"\n\nAdditional instructions:\n{context.config['planning_instructions']}"
        
        return message
