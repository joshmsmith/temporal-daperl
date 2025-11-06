"""Activity wrappers for DAPERL agents."""

from temporalio import activity

from daperl.core.models import (
    AgentContext,
    DetectionResult,
    AnalysisResult,
    PlanningResult,
    ExecutionResult,
    ReportingResult,
    LearningResult,
)
from daperl.agents import (
    DetectionAgent,
    AnalysisAgent,
    PlanningAgent,
    ExecutionAgent,
    ReportingAgent,
    LearningAgent,
)
from daperl.config.settings import settings
from daperl.storage.json_storage import JSONLearningStorage


@activity.defn
async def run_detection_agent(context: AgentContext) -> DetectionResult:
    """
    Run the detection agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Detection result
    """
    activity.logger.info("Starting detection agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = DetectionAgent(llm_config=daperl_config.detection_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Detection complete",
        extra={
            "problems_found": len(result.problems),
            "confidence": result.confidence
        }
    )
    
    return result


@activity.defn
async def run_analysis_agent(context: AgentContext) -> AnalysisResult:
    """
    Run the analysis agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Analysis result
    """
    activity.logger.info("Starting analysis agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = AnalysisAgent(llm_config=daperl_config.analysis_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Analysis complete",
        extra={
            "root_causes": len(result.root_causes),
            "confidence": result.confidence
        }
    )
    
    return result


@activity.defn
async def run_planning_agent(context: AgentContext) -> PlanningResult:
    """
    Run the planning agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Planning result
    """
    activity.logger.info("Starting planning agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = PlanningAgent(llm_config=daperl_config.planning_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Planning complete",
        extra={
            "actions_planned": len(result.plan.actions) if result.plan else 0,
            "confidence": result.confidence
        }
    )
    
    return result


@activity.defn
async def run_execution_agent(context: AgentContext) -> ExecutionResult:
    """
    Run the execution agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Execution result
    """
    activity.logger.info("Starting execution agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    # Note: Action registry should be provided via context.config if needed
    agent = ExecutionAgent(llm_config=daperl_config.execution_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Execution complete",
        extra={
            "success_count": result.success_count,
            "failure_count": result.failure_count,
            "confidence": result.confidence
        }
    )
    
    return result


@activity.defn
async def run_reporting_agent(context: AgentContext) -> ReportingResult:
    """
    Run the reporting agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Reporting result
    """
    activity.logger.info("Starting reporting agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    
    # Create and run agent
    agent = ReportingAgent(llm_config=daperl_config.reporting_llm)
    result = await agent.execute(context)
    
    activity.logger.info(
        "Reporting complete",
        extra={"confidence": result.confidence}
    )
    
    return result


@activity.defn
async def run_learning_agent(context: AgentContext) -> LearningResult:
    """
    Run the learning agent as a Temporal activity.
    
    Args:
        context: Agent context
        
    Returns:
        Learning result
    """
    activity.logger.info("Starting learning agent", extra={"domain": context.domain})
    
    # Get configuration
    daperl_config = settings.get_daperl_config()
    learning_config = settings.get_learning_config()
    
    # Create storage backend
    storage = None
    if learning_config.storage_type == "json":
        storage = JSONLearningStorage(learning_config.storage_path)
    
    # Create and run agent
    agent = LearningAgent(
        llm_config=daperl_config.learning_llm,
        storage=storage
    )
    result = await agent.execute(context)
    
    activity.logger.info(
        "Learning complete",
        extra={
            "insights_generated": len(result.insights),
            "patterns_found": result.patterns_found,
            "confidence": result.confidence
        }
    )
    
    return result
