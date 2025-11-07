"""Storage backends for learning data."""

from daperl.storage.base import BaseLearningStorage
from daperl.storage.json_storage import JSONLearningStorage

__all__ = [
    "BaseLearningStorage",
    "JSONLearningStorage",
]
