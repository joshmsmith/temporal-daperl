"""Type definitions for the DAPERL framework."""

from enum import Enum
from typing import Any, Dict, List, Optional


class AgentPhase(str, Enum):
    """Phases in the DAPERL workflow."""
    
    DETECTION = "detection"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    REPORTING = "reporting"
    LEARNING = "learning"


class WorkflowStatus(str, Enum):
    """Status of the DAPERL workflow."""
    
    INITIALIZING = "INITIALIZING"
    DETECTING = "DETECTING"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    EXECUTING = "EXECUTING"
    REPORTING = "REPORTING"
    LEARNING = "LEARNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ConfidenceLevel(str, Enum):
    """Confidence levels for agent results."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
