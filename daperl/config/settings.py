"""Settings and configuration for the DAPERL framework."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    """Configuration for LLM client."""
    
    provider: str = "openai"  # "openai", "anthropic", "litellm"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60
    additional_params: Dict[str, Any] = Field(default_factory=dict)


class TemporalConfig(BaseModel):
    """Configuration for Temporal connection."""
    
    host: str = "localhost:7233"
    namespace: str = "default"
    task_queue: str = "daperl-task-queue"


class LearningConfig(BaseModel):
    """Configuration for learning storage."""
    
    storage_type: str = "json"  # "json", "sqlite", "postgresql"
    storage_path: str = "./data/learning.json"


class DAPERLConfig(BaseModel):
    """Configuration for DAPERL workflow agents."""
    
    detection_llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=2000
        )
    )
    
    analysis_llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(
            provider="openai",
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4000
        )
    )
    
    planning_llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=8000
        )
    )
    
    execution_llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(
            provider="openai",
            model="gpt-4o",
            temperature=0.2,
            max_tokens=4000
        )
    )
    
    reporting_llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=3000
        )
    )
    
    learning_llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(
            provider="openai",
            model="gpt-4o",
            temperature=0.5,
            max_tokens=4000
        )
    )


class Settings(BaseSettings):
    """Main settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Temporal Configuration
    temporal_host: str = Field(default="localhost:7233", alias="TEMPORAL_HOST")
    temporal_namespace: str = Field(default="default", alias="TEMPORAL_NAMESPACE")
    temporal_task_queue: str = Field(default="daperl-task-queue", alias="TEMPORAL_TASK_QUEUE")
    
    # Default LLM Configuration
    default_llm_provider: Optional[str] = Field(default=None, alias="DEFAULT_LLM_PROVIDER")
    default_llm_model: Optional[str] = Field(default=None, alias="DEFAULT_LLM_MODEL")
    default_llm_temperature: Optional[float] = Field(default=None, alias="DEFAULT_LLM_TEMPERATURE")
    default_llm_max_tokens: Optional[int] = Field(default=None, alias="DEFAULT_LLM_MAX_TOKENS")
    
    # Detection Agent LLM
    detection_llm_provider: Optional[str] = Field(default=None, alias="DETECTION_LLM_PROVIDER")
    detection_llm_model: Optional[str] = Field(default=None, alias="DETECTION_LLM_MODEL")
    detection_llm_temperature: Optional[float] = Field(default=None, alias="DETECTION_LLM_TEMPERATURE")
    detection_llm_max_tokens: Optional[int] = Field(default=None, alias="DETECTION_LLM_MAX_TOKENS")
    
    # Analysis Agent LLM
    analysis_llm_provider: Optional[str] = Field(default=None, alias="ANALYSIS_LLM_PROVIDER")
    analysis_llm_model: Optional[str] = Field(default=None, alias="ANALYSIS_LLM_MODEL")
    analysis_llm_temperature: Optional[float] = Field(default=None, alias="ANALYSIS_LLM_TEMPERATURE")
    analysis_llm_max_tokens: Optional[int] = Field(default=None, alias="ANALYSIS_LLM_MAX_TOKENS")
    
    # Planning Agent LLM
    planning_llm_provider: Optional[str] = Field(default=None, alias="PLANNING_LLM_PROVIDER")
    planning_llm_model: Optional[str] = Field(default=None, alias="PLANNING_LLM_MODEL")
    planning_llm_temperature: Optional[float] = Field(default=None, alias="PLANNING_LLM_TEMPERATURE")
    planning_llm_max_tokens: Optional[int] = Field(default=None, alias="PLANNING_LLM_MAX_TOKENS")
    
    # Execution Agent LLM
    execution_llm_provider: Optional[str] = Field(default=None, alias="EXECUTION_LLM_PROVIDER")
    execution_llm_model: Optional[str] = Field(default=None, alias="EXECUTION_LLM_MODEL")
    execution_llm_temperature: Optional[float] = Field(default=None, alias="EXECUTION_LLM_TEMPERATURE")
    execution_llm_max_tokens: Optional[int] = Field(default=None, alias="EXECUTION_LLM_MAX_TOKENS")
    
    # Reporting Agent LLM
    reporting_llm_provider: Optional[str] = Field(default=None, alias="REPORTING_LLM_PROVIDER")
    reporting_llm_model: Optional[str] = Field(default=None, alias="REPORTING_LLM_MODEL")
    reporting_llm_temperature: Optional[float] = Field(default=None, alias="REPORTING_LLM_TEMPERATURE")
    reporting_llm_max_tokens: Optional[int] = Field(default=None, alias="REPORTING_LLM_MAX_TOKENS")
    
    # Learning Agent LLM
    learning_llm_provider: Optional[str] = Field(default=None, alias="LEARNING_LLM_PROVIDER")
    learning_llm_model: Optional[str] = Field(default=None, alias="LEARNING_LLM_MODEL")
    learning_llm_temperature: Optional[float] = Field(default=None, alias="LEARNING_LLM_TEMPERATURE")
    learning_llm_max_tokens: Optional[int] = Field(default=None, alias="LEARNING_LLM_MAX_TOKENS")
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    
    # Learning Storage
    learning_storage_type: str = Field(default="json", alias="LEARNING_STORAGE_TYPE")
    learning_storage_path: str = Field(default="./data/learning.json", alias="LEARNING_STORAGE_PATH")
    
    # MCP Server
    mcp_server_name: str = Field(default="daperl-server", alias="MCP_SERVER_NAME")
    
    def get_temporal_config(self) -> TemporalConfig:
        """Get Temporal configuration."""
        return TemporalConfig(
            host=self.temporal_host,
            namespace=self.temporal_namespace,
            task_queue=self.temporal_task_queue
        )
    
    def get_daperl_config(self) -> DAPERLConfig:
        """Get DAPERL configuration with per-agent LLM configs."""
        # Detection Agent
        detection_provider = self._resolve_provider(self.detection_llm_provider, "DETECTION_LLM_PROVIDER", "openai")
        detection_model = self._resolve_model(self.detection_llm_model, "DETECTION_LLM_MODEL", "gpt-3.5-turbo")
        detection_temperature = self._resolve_temperature(self.detection_llm_temperature, "DETECTION_LLM_TEMPERATURE", 0.3)
        detection_max_tokens = self._resolve_max_tokens(self.detection_llm_max_tokens, "DETECTION_LLM_MAX_TOKENS", 2000)
        
        # Analysis Agent
        analysis_provider = self._resolve_provider(self.analysis_llm_provider, "ANALYSIS_LLM_PROVIDER", "openai")
        analysis_model = self._resolve_model(self.analysis_llm_model, "ANALYSIS_LLM_MODEL", "gpt-4o")
        analysis_temperature = self._resolve_temperature(self.analysis_llm_temperature, "ANALYSIS_LLM_TEMPERATURE", 0.5)
        analysis_max_tokens = self._resolve_max_tokens(self.analysis_llm_max_tokens, "ANALYSIS_LLM_MAX_TOKENS", 4000)
        
        # Planning Agent
        planning_provider = self._resolve_provider(self.planning_llm_provider, "PLANNING_LLM_PROVIDER", "anthropic")
        planning_model = self._resolve_model(self.planning_llm_model, "PLANNING_LLM_MODEL", "claude-3-5-sonnet-20241022")
        planning_temperature = self._resolve_temperature(self.planning_llm_temperature, "PLANNING_LLM_TEMPERATURE", 0.7)
        planning_max_tokens = self._resolve_max_tokens(self.planning_llm_max_tokens, "PLANNING_LLM_MAX_TOKENS", 8000)
        
        # Execution Agent
        execution_provider = self._resolve_provider(self.execution_llm_provider, "EXECUTION_LLM_PROVIDER", "openai")
        execution_model = self._resolve_model(self.execution_llm_model, "EXECUTION_LLM_MODEL", "gpt-4o")
        execution_temperature = self._resolve_temperature(self.execution_llm_temperature, "EXECUTION_LLM_TEMPERATURE", 0.2)
        execution_max_tokens = self._resolve_max_tokens(self.execution_llm_max_tokens, "EXECUTION_LLM_MAX_TOKENS", 4000)
        
        # Reporting Agent
        reporting_provider = self._resolve_provider(self.reporting_llm_provider, "REPORTING_LLM_PROVIDER", "openai")
        reporting_model = self._resolve_model(self.reporting_llm_model, "REPORTING_LLM_MODEL", "gpt-3.5-turbo")
        reporting_temperature = self._resolve_temperature(self.reporting_llm_temperature, "REPORTING_LLM_TEMPERATURE", 0.7)
        reporting_max_tokens = self._resolve_max_tokens(self.reporting_llm_max_tokens, "REPORTING_LLM_MAX_TOKENS", 3000)
        
        # Learning Agent
        learning_provider = self._resolve_provider(self.learning_llm_provider, "LEARNING_LLM_PROVIDER", "openai")
        learning_model = self._resolve_model(self.learning_llm_model, "LEARNING_LLM_MODEL", "gpt-4o")
        learning_temperature = self._resolve_temperature(self.learning_llm_temperature, "LEARNING_LLM_TEMPERATURE", 0.5)
        learning_max_tokens = self._resolve_max_tokens(self.learning_llm_max_tokens, "LEARNING_LLM_MAX_TOKENS", 4000)
        
        return DAPERLConfig(
            detection_llm=LLMConfig(
                provider=detection_provider,
                model=detection_model,
                api_key=self._get_api_key(detection_provider),
                temperature=detection_temperature,
                max_tokens=detection_max_tokens
            ),
            analysis_llm=LLMConfig(
                provider=analysis_provider,
                model=analysis_model,
                api_key=self._get_api_key(analysis_provider),
                temperature=analysis_temperature,
                max_tokens=analysis_max_tokens
            ),
            planning_llm=LLMConfig(
                provider=planning_provider,
                model=planning_model,
                api_key=self._get_api_key(planning_provider),
                temperature=planning_temperature,
                max_tokens=planning_max_tokens
            ),
            execution_llm=LLMConfig(
                provider=execution_provider,
                model=execution_model,
                api_key=self._get_api_key(execution_provider),
                temperature=execution_temperature,
                max_tokens=execution_max_tokens
            ),
            reporting_llm=LLMConfig(
                provider=reporting_provider,
                model=reporting_model,
                api_key=self._get_api_key(reporting_provider),
                temperature=reporting_temperature,
                max_tokens=reporting_max_tokens
            ),
            learning_llm=LLMConfig(
                provider=learning_provider,
                model=learning_model,
                api_key=self._get_api_key(learning_provider),
                temperature=learning_temperature,
                max_tokens=learning_max_tokens
            )
        )
    
    def get_learning_config(self) -> LearningConfig:
        """Get learning storage configuration."""
        return LearningConfig(
            storage_type=self.learning_storage_type,
            storage_path=self.learning_storage_path
        )
    
    def _resolve_provider(self, agent_provider: Optional[str], agent_env_var: str, hardcoded_default: str) -> str:
        """
        Resolve provider with cascading fallback:
        1. Agent-specific env var (if set)
        2. DEFAULT_LLM_PROVIDER env var (if set)
        3. Hardcoded default for the specific agent
        """
        # Check if agent-specific value was set (not None)
        if agent_provider is not None:
            return agent_provider
        
        # Check if DEFAULT_LLM_PROVIDER was set (not None)
        if self.default_llm_provider is not None:
            return self.default_llm_provider
        
        # Fall back to hardcoded default for this agent
        return hardcoded_default
    
    def _resolve_model(self, agent_model: Optional[str], agent_env_var: str, hardcoded_default: str) -> str:
        """
        Resolve model with cascading fallback:
        1. Agent-specific env var (if set)
        2. DEFAULT_LLM_MODEL env var (if set)
        3. Hardcoded default for the specific agent
        """
        if agent_model is not None:
            return agent_model
        
        if self.default_llm_model is not None:
            return self.default_llm_model
        
        return hardcoded_default
    
    def _resolve_temperature(self, agent_temperature: Optional[float], agent_env_var: str, hardcoded_default: float) -> float:
        """
        Resolve temperature with cascading fallback:
        1. Agent-specific env var (if set)
        2. DEFAULT_LLM_TEMPERATURE env var (if set)
        3. Hardcoded default for the specific agent
        """
        if agent_temperature is not None:
            return agent_temperature
        
        if self.default_llm_temperature is not None:
            return self.default_llm_temperature
        
        return hardcoded_default
    
    def _resolve_max_tokens(self, agent_max_tokens: Optional[int], agent_env_var: str, hardcoded_default: int) -> int:
        """
        Resolve max_tokens with cascading fallback:
        1. Agent-specific env var (if set)
        2. DEFAULT_LLM_MAX_TOKENS env var (if set)
        3. Hardcoded default for the specific agent
        """
        if agent_max_tokens is not None:
            return agent_max_tokens
        
        if self.default_llm_max_tokens is not None:
            return self.default_llm_max_tokens
        
        return hardcoded_default
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider."""
        if provider == "openai":
            return self.openai_api_key
        elif provider == "anthropic":
            return self.anthropic_api_key
        return None


# Global settings instance
settings = Settings()
