"""JSON file-based storage for learning data."""

import json
import os
from pathlib import Path
from typing import List, Optional
import asyncio

from daperl.storage.base import BaseLearningStorage
from daperl.core.models import ExecutionMetric, LearningInsight


class JSONLearningStorage(BaseLearningStorage):
    """Simple JSON file-based storage for learning data."""
    
    def __init__(self, storage_path: str = "./data/learning.json"):
        """
        Initialize JSON storage.
        
        Args:
            storage_path: Path to the JSON storage file
        """
        self.storage_path = Path(storage_path)
        self.metrics_path = self.storage_path.parent / "metrics.json"
        self.insights_path = self.storage_path.parent / "insights.json"
        
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        if not self.metrics_path.exists():
            self.metrics_path.write_text("[]")
        if not self.insights_path.exists():
            self.insights_path.write_text("[]")
        
        # Simple lock for concurrent access
        self._lock = asyncio.Lock()
    
    async def store_metric(self, metric: ExecutionMetric) -> None:
        """Store an execution metric."""
        async with self._lock:
            metrics = await self._read_metrics()
            metrics.append(metric.model_dump(mode='json'))
            await self._write_metrics(metrics)
    
    async def get_recent_metrics(self, limit: int = 10) -> List[ExecutionMetric]:
        """Retrieve recent execution metrics."""
        async with self._lock:
            metrics_data = await self._read_metrics()
            recent = metrics_data[-limit:] if len(metrics_data) > limit else metrics_data
            return [ExecutionMetric(**m) for m in reversed(recent)]
    
    async def get_metric(self, workflow_id: str) -> Optional[ExecutionMetric]:
        """Retrieve a specific execution metric."""
        async with self._lock:
            metrics_data = await self._read_metrics()
            for m in reversed(metrics_data):
                if m.get("workflow_id") == workflow_id:
                    return ExecutionMetric(**m)
            return None
    
    async def store_insight(self, insight: LearningInsight) -> None:
        """Store a learning insight."""
        async with self._lock:
            insights = await self._read_insights()
            insights.append(insight.model_dump(mode='json'))
            await self._write_insights(insights)
    
    async def get_insights(self, limit: int = 10) -> List[LearningInsight]:
        """Retrieve recent learning insights."""
        async with self._lock:
            insights_data = await self._read_insights()
            recent = insights_data[-limit:] if len(insights_data) > limit else insights_data
            return [LearningInsight(**i) for i in reversed(recent)]
    
    async def _read_metrics(self) -> list:
        """Read metrics from file."""
        return await asyncio.to_thread(self._read_json, self.metrics_path)
    
    async def _write_metrics(self, metrics: list) -> None:
        """Write metrics to file."""
        await asyncio.to_thread(self._write_json, self.metrics_path, metrics)
    
    async def _read_insights(self) -> list:
        """Read insights from file."""
        return await asyncio.to_thread(self._read_json, self.insights_path)
    
    async def _write_insights(self, insights: list) -> None:
        """Write insights to file."""
        await asyncio.to_thread(self._write_json, self.insights_path, insights)
    
    def _read_json(self, path: Path) -> list:
        """Read JSON file synchronously."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_json(self, path: Path, data: list) -> None:
        """Write JSON file synchronously."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
