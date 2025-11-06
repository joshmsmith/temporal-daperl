"""Base agent classes for the DAPERL framework."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from daperl.core.models import (
    AgentContext,
    AgentResult,
    DetectionResult,
    AnalysisResult,
    PlanningResult,
    ExecutionResult,
    ReportingResult,
    LearningResult,
)
from daperl.llm.base import BaseLLMClient
from daperl.config.settings import LLMConfig


class BaseAgent(ABC):
    """Abstract base class for all DAPERL agents."""
    
    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        llm_config: Optional[LLMConfig] = None,
    ):
        """
        Initialize the agent.
        
        Args:
            llm_client: Pre-configured LLM client (takes precedence)
            llm_config: Configuration to create LLM client
        """
        self.llm_client = llm_client
        self.llm_config = llm_config
        
        # Lazy initialization of LLM client
        if self.llm_client is None and self.llm_config is not None:
            from daperl.llm.factory import LLMFactory
            self.llm_client = LLMFactory.create(self.llm_config)
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's logic.
        
        Args:
            context: The agent context with shared state
            
        Returns:
            The result of the agent's execution
        """
        pass
    
    @abstractmethod
    def validate_output(self, output: Any) -> bool:
        """
        Validate the agent's output.
        
        Args:
            output: The output to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert numeric confidence to level."""
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.7:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"


class BaseDetectionAgent(BaseAgent):
    """Base class for detection agents."""
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> DetectionResult:
        """
        Detect problems in the given context.
        
        Args:
            context: The agent context
            
        Returns:
            Detection result with identified problems
        """
        pass


class BaseAnalysisAgent(BaseAgent):
    """Base class for analysis agents."""
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AnalysisResult:
        """
        Analyze detected problems.
        
        Args:
            context: The agent context with detection results
            
        Returns:
            Analysis result with root causes and recommendations
        """
        pass


class BasePlanningAgent(BaseAgent):
    """Base class for planning agents."""
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> PlanningResult:
        """
        Create an execution plan based on analysis.
        
        Args:
            context: The agent context with analysis results
            
        Returns:
            Planning result with execution plan
        """
        pass


class BaseExecutionAgent(BaseAgent):
    """Base class for execution agents."""
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> ExecutionResult:
        """
        Execute the planned actions.
        
        Args:
            context: The agent context with execution plan
            
        Returns:
            Execution result with action outcomes
        """
        pass


class BaseReportingAgent(BaseAgent):
    """Base class for reporting agents."""
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> ReportingResult:
        """
        Generate a report of the workflow execution.
        
        Args:
            context: The agent context with all phase results
            
        Returns:
            Reporting result with summary and metrics
        """
        pass


class BaseLearningAgent(BaseAgent):
    """Base class for learning agents."""
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> LearningResult:
        """
        Learn from the workflow execution.
        
        Args:
            context: The agent context with all phase results
            
        Returns:
            Learning result with insights and patterns
        """
        pass
