"""Data models for the DAPERL framework."""

from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from daperl.core.types import AgentPhase, WorkflowStatus, ConfidenceLevel


class AgentContext(BaseModel):
    """Shared context passed between agents."""
    
    workflow_id: str
    domain: str
    data: Dict[str, Any] = Field(default_factory=dict)
    history: List[
        Annotated[
            Union[
                "DetectionResult",
                "AnalysisResult", 
                "PlanningResult",
                "ExecutionResult",
                "ReportingResult",
                "LearningResult"
            ],
            Field(discriminator="phase")
        ]
    ] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Base result from an agent."""
    
    phase: AgentPhase
    success: bool
    message: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Problem(BaseModel):
    """Represents a detected problem."""
    
    id: str
    type: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    data: Dict[str, Any] = Field(default_factory=dict)


class DetectionResult(AgentResult):
    """Result from the detection agent."""
    
    phase: Literal[AgentPhase.DETECTION] = AgentPhase.DETECTION
    problems_detected: bool = False
    problems: List[Problem] = Field(default_factory=list)
    summary: str = ""


class AnalysisResult(AgentResult):
    """Result from the analysis agent."""
    
    phase: Literal[AgentPhase.ANALYSIS] = AgentPhase.ANALYSIS
    analyzed_problems: List[Problem] = Field(default_factory=list)
    root_causes: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    analysis_summary: str = ""


class Action(BaseModel):
    """Represents a planned action."""
    
    id: str
    action_type: str
    description: str
    target: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    requires_approval: bool = True


class ExecutionPlan(BaseModel):
    """A plan for execution."""
    
    id: str
    actions: List[Action]
    estimated_duration: Optional[str] = None
    risk_level: str = "medium"
    requires_approval: bool = True


class PlanningResult(AgentResult):
    """Result from the planning agent."""
    
    phase: Literal[AgentPhase.PLANNING] = AgentPhase.PLANNING
    plan: Optional[ExecutionPlan] = None
    alternatives: List[ExecutionPlan] = Field(default_factory=list)
    planning_summary: str = ""


class ActionResult(BaseModel):
    """Result from executing an action."""
    
    action_id: str
    success: bool
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ExecutionResult(AgentResult):
    """Result from the execution agent."""
    
    phase: Literal[AgentPhase.EXECUTION] = AgentPhase.EXECUTION
    plan_id: str
    actions_executed: List[ActionResult] = Field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    execution_summary: str = ""


class ReportingResult(AgentResult):
    """Result from the reporting agent."""
    
    phase: Literal[AgentPhase.REPORTING] = AgentPhase.REPORTING
    report: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class ExecutionMetric(BaseModel):
    """Metrics from a workflow execution."""
    
    workflow_id: str
    timestamp: datetime
    domain: str
    detection_result: Optional[DetectionResult] = None
    analysis_result: Optional[AnalysisResult] = None
    planning_result: Optional[PlanningResult] = None
    execution_result: Optional[ExecutionResult] = None
    reporting_result: Optional[ReportingResult] = None
    overall_success: bool
    total_duration_seconds: Optional[float] = None


class LearningInsight(BaseModel):
    """An insight learned from past executions."""
    
    id: str
    insight_type: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_executions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LearningResult(AgentResult):
    """Result from the learning agent."""
    
    phase: Literal[AgentPhase.LEARNING] = AgentPhase.LEARNING
    insights: List[LearningInsight] = Field(default_factory=list)
    patterns_found: int = 0
    recommendations: List[str] = Field(default_factory=list)
    learning_summary: str = ""


class DAPERLInput(BaseModel):
    """Input to the DAPERL workflow."""
    
    domain: str
    data: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    auto_approve: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DAPERLResult(BaseModel):
    """Result from the DAPERL workflow."""
    
    workflow_id: str
    status: WorkflowStatus
    detection_result: Optional[DetectionResult] = None
    analysis_result: Optional[AnalysisResult] = None
    planning_result: Optional[PlanningResult] = None
    execution_result: Optional[ExecutionResult] = None
    reporting_result: Optional[ReportingResult] = None
    learning_result: Optional[LearningResult] = None
    summary: str
    started_at: datetime
    completed_at: Optional[datetime] = None


# Update forward references
AgentContext.model_rebuild()
