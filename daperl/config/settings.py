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
    default_llm_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")
    default_llm_model: str = Field(default="gpt-4o", alias="DEFAULT_LLM_MODEL")
    default_llm_temperature: float = Field(default=0.7, alias="DEFAULT_LLM_TEMPERATURE")
    default_llm_max_tokens: int = Field(default=4000, alias="DEFAULT_LLM_MAX_TOKENS")
    
    # Detection Agent LLM
    detection_llm_provider: str = Field(default="openai", alias="DETECTION_LLM_PROVIDER")
    detection_llm_model: str = Field(default="gpt-3.5-turbo", alias="DETECTION_LLM_MODEL")
    detection_llm_temperature: float = Field(default=0.3, alias="DETECTION_LLM_TEMPERATURE")
    detection_llm_max_tokens: int = Field(default=2000, alias="DETECTION_LLM_MAX_TOKENS")
    
    # Analysis Agent LLM
    analysis_llm_provider: str = Field(default="openai", alias="ANALYSIS_LLM_PROVIDER")
    analysis_llm_model: str = Field(default="gpt-4o", alias="ANALYSIS_LLM_MODEL")
    analysis_llm_temperature: float = Field(default=0.5, alias="ANALYSIS_LLM_TEMPERATURE")
    analysis_llm_max_tokens: int = Field(default=4000, alias="ANALYSIS_LLM_MAX_TOKENS")
    
    # Planning Agent LLM
    planning_llm_provider: str = Field(default="anthropic", alias="PLANNING_LLM_PROVIDER")
    planning_llm_model: str = Field(default="claude-3-5-sonnet-20241022", alias="PLANNING_LLM_MODEL")
    planning_llm_temperature: float = Field(default=0.7, alias="PLANNING_LLM_TEMPERATURE")
    planning_llm_max_tokens: int = Field(default=8000, alias="PLANNING_LLM_MAX_TOKENS")
    
    # Execution Agent LLM
    execution_llm_provider: str = Field(default="openai", alias="EXECUTION_LLM_PROVIDER")
    execution_llm_model: str = Field(default="gpt-4o", alias="EXECUTION_LLM_MODEL")
    execution_llm_temperature: float = Field(default=0.2, alias="EXECUTION_LLM_TEMPERATURE")
    execution_llm_max_tokens: int = Field(default=4000, alias="EXECUTION_LLM_MAX_TOKENS")
    
    # Reporting Agent LLM
    reporting_llm_provider: str = Field(default="openai", alias="REPORTING_LLM_PROVIDER")
    reporting_llm_model: str = Field(default="gpt-3.5-turbo", alias="REPORTING_LLM_MODEL")
    reporting_llm_temperature: float = Field(default=0.7, alias="REPORTING_LLM_TEMPERATURE")
    reporting_llm_max_tokens: int = Field(default=3000, alias="REPORTING_LLM_MAX_TOKENS")
    
    # Learning Agent LLM
    learning_llm_provider: str = Field(default="openai", alias="LEARNING_LLM_PROVIDER")
    learning_llm_model: str = Field(default="gpt-4o", alias="LEARNING_LLM_MODEL")
    learning_llm_temperature: float = Field(default=0.5, alias="LEARNING_LLM_TEMPERATURE")
    learning_llm_max_tokens: int = Field(default=4000, alias="LEARNING_LLM_MAX_TOKENS")
    
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
        return DAPERLConfig(
            detection_llm=LLMConfig(
                provider=self.detection_llm_provider,
                model=self.detection_llm_model,
                api_key=self._get_api_key(self.detection_llm_provider),
                temperature=self.detection_llm_temperature,
                max_tokens=self.detection_llm_max_tokens
            ),
            analysis_llm=LLMConfig(
                provider=self.analysis_llm_provider,
                model=self.analysis_llm_model,
                api_key=self._get_api_key(self.analysis_llm_provider),
                temperature=self.analysis_llm_temperature,
                max_tokens=self.analysis_llm_max_tokens
            ),
            planning_llm=LLMConfig(
                provider=self.planning_llm_provider,
                model=self.planning_llm_model,
                api_key=self._get_api_key(self.planning_llm_provider),
                temperature=self.planning_llm_temperature,
                max_tokens=self.planning_llm_max_tokens
            ),
            execution_llm=LLMConfig(
                provider=self.execution_llm_provider,
                model=self.execution_llm_model,
                api_key=self._get_api_key(self.execution_llm_provider),
                temperature=self.execution_llm_temperature,
                max_tokens=self.execution_llm_max_tokens
            ),
            reporting_llm=LLMConfig(
                provider=self.reporting_llm_provider,
                model=self.reporting_llm_model,
                api_key=self._get_api_key(self.reporting_llm_provider),
                temperature=self.reporting_llm_temperature,
                max_tokens=self.reporting_llm_max_tokens
            ),
            learning_llm=LLMConfig(
                provider=self.learning_llm_provider,
                model=self.learning_llm_model,
                api_key=self._get_api_key(self.learning_llm_provider),
                temperature=self.learning_llm_temperature,
                max_tokens=self.learning_llm_max_tokens
            )
        )
    
    def get_learning_config(self) -> LearningConfig:
        """Get learning storage configuration."""
        return LearningConfig(
            storage_type=self.learning_storage_type,
            storage_path=self.learning_storage_path
        )
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider."""
        if provider == "openai":
            return self.openai_api_key
        elif provider == "anthropic":
            return self.anthropic_api_key
        return None


# Global settings instance
settings = Settings()
