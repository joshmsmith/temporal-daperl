"""Base LLM client interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """A message in an LLM conversation."""
    
    role: str  # "system", "user", "assistant"
    content: str


class LLMResponse(BaseModel):
    """Response from an LLM."""
    
    content: str
    model: str
    usage: Dict[str, int] = {}
    metadata: Dict[str, Any] = {}


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        timeout: int = 60,
        **kwargs
    ):
        """
        Initialize the LLM client.
        
        Args:
            model: The model to use
            api_key: API key for authentication
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters
        """
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.kwargs = kwargs
    
    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion from the LLM.
        
        Args:
            messages: List of messages in the conversation
            system_prompt: Optional system prompt to prepend
            **kwargs: Additional parameters for this specific call
            
        Returns:
            LLM response with generated content
        """
        pass
    
    @abstractmethod
    async def complete_with_json(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a JSON completion from the LLM.
        
        Args:
            messages: List of messages in the conversation
            system_prompt: Optional system prompt to prepend
            **kwargs: Additional parameters for this specific call
            
        Returns:
            Parsed JSON response
        """
        pass
