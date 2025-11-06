"""LiteLLM provider implementation for multi-provider support."""

import json
from typing import Any, Dict, List, Optional

import litellm
from litellm import acompletion

from daperl.llm.base import BaseLLMClient, LLMMessage, LLMResponse


class LiteLLMClient(BaseLLMClient):
    """LLM client using LiteLLM for multi-provider support."""
    
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
        Initialize the LiteLLM client.
        
        Args:
            model: The model to use (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
            api_key: API key for authentication
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters
        """
        super().__init__(model, api_key, temperature, max_tokens, timeout, **kwargs)
        
        # Set API key in environment if provided
        if api_key:
            # LiteLLM will automatically detect the provider from the model name
            # and use the appropriate environment variable
            if "gpt" in model or "o1" in model:
                import os
                os.environ["OPENAI_API_KEY"] = api_key
            elif "claude" in model:
                import os
                os.environ["ANTHROPIC_API_KEY"] = api_key
    
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
        # Convert messages to dict format
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
        
        # Merge kwargs with defaults
        params = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "timeout": kwargs.get("timeout", self.timeout),
        }
        
        # Add any additional parameters
        params.update({k: v for k, v in self.kwargs.items()})
        params.update({k: v for k, v in kwargs.items() if k not in params})
        
        # Call LiteLLM
        response = await acompletion(**params)
        
        # Extract response
        content = response.choices[0].message.content
        
        # Extract usage info
        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        
        return LLMResponse(
            content=content,
            model=response.model,
            usage=usage,
            metadata={"response_id": response.id if hasattr(response, "id") else None}
        )
    
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
        # Add JSON formatting instruction to system prompt
        json_instruction = "\n\nYou must respond with valid JSON only. No other text."
        if system_prompt:
            system_prompt = system_prompt + json_instruction
        else:
            system_prompt = "You are a helpful assistant that responds with valid JSON." + json_instruction
        
        # Some models support response_format parameter
        if "gpt" in self.model or "o1" in self.model:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = await self.complete(messages, system_prompt, **kwargs)
        
        # Parse JSON from response
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            # Try to extract JSON from markdown code blocks
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse JSON from LLM response: {e}") from e
