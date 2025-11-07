"""Base storage interface for learning data."""

from abc import ABC, abstractmethod
from typing import List, Optional

from daperl.core.models import ExecutionMetric, LearningInsight


class BaseLearningStorage(ABC):
    """Abstract base class for learning data storage."""
    
    @abstractmethod
    async def store_metric(self, metric: ExecutionMetric) -> None:
        """
        Store an execution metric.
        
        Args:
            metric: The execution metric to store
        """
        pass
    
    @abstractmethod
    async def get_recent_metrics(self, limit: int = 10) -> List[ExecutionMetric]:
        """
        Retrieve recent execution metrics.
        
        Args:
            limit: Maximum number of metrics to retrieve
            
        Returns:
            List of recent execution metrics
        """
        pass
    
    @abstractmethod
    async def get_metric(self, workflow_id: str) -> Optional[ExecutionMetric]:
        """
        Retrieve a specific execution metric.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            The execution metric if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def store_insight(self, insight: LearningInsight) -> None:
        """
        Store a learning insight.
        
        Args:
            insight: The learning insight to store
        """
        pass
    
    @abstractmethod
    async def get_insights(self, limit: int = 10) -> List[LearningInsight]:
        """
        Retrieve recent learning insights.
        
        Args:
            limit: Maximum number of insights to retrieve
            
        Returns:
            List of learning insights
        """
        pass
