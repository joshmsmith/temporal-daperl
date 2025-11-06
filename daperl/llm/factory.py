"""Factory for creating LLM clients."""

from typing import Optional

from daperl.config.settings import LLMConfig
from daperl.llm.base import BaseLLMClient
from daperl.llm.providers.litellm_provider import LiteLLMClient


class LLMFactory:
    """Factory for creating LLM clients based on configuration."""
    
    @staticmethod
    def create(config: LLMConfig) -> BaseLLMClient:
        """
        Create an LLM client based on the configuration.
        
        Args:
            config: LLM configuration
            
        Returns:
            Configured LLM client
            
        Raises:
            ValueError: If the provider is not supported
        """
        # For now, we use LiteLLM for all providers as it supports multiple providers
        # This gives us flexibility to add provider-specific clients later if needed
        
        provider = config.provider.lower()
        
        # LiteLLM supports openai, anthropic, and many others
        # We can use it for all providers
        return LiteLLMClient(
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            **config.additional_params
        )
    
    @staticmethod
    def create_from_env(
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> BaseLLMClient:
        """
        Create an LLM client with explicit parameters.
        
        Args:
            provider: Provider name (openai, anthropic, etc.)
            model: Model name
            api_key: API key for authentication
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Configured LLM client
        """
        config = LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            additional_params=kwargs
        )
        return LLMFactory.create(config)
