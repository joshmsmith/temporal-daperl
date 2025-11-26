#!/usr/bin/env python3
"""Test script to verify settings configuration."""

from daperl.config.settings import settings

# Test settings loading
print("=" * 60)
print("SETTINGS TEST")
print("=" * 60)

# Check if API key is loaded
print(f"\nOpenAI API Key loaded: {settings.openai_api_key is not None}")
if settings.openai_api_key:
    print(f"  Key preview: {settings.openai_api_key[:20]}...")

print(f"\nDefault LLM Provider: {settings.default_llm_provider}")
print(f"Default LLM Model: {settings.default_llm_model}")

# Get DAPERL config
print("\n" + "=" * 60)
print("DAPERL CONFIG TEST")
print("=" * 60)

daperl_config = settings.get_daperl_config()

print("\nDetection Agent LLM Config:")
print(f"  Provider: {daperl_config.detection_llm.provider}")
print(f"  Model: {daperl_config.detection_llm.model}")
print(f"  Temperature: {daperl_config.detection_llm.temperature}")
print(f"  Max Tokens: {daperl_config.detection_llm.max_tokens}")
print(f"  API Key set: {daperl_config.detection_llm.api_key is not None}")
if daperl_config.detection_llm.api_key:
    print(f"  API Key preview: {daperl_config.detection_llm.api_key[:20]}...")

print("\nAnalysis Agent LLM Config:")
print(f"  Provider: {daperl_config.analysis_llm.provider}")
print(f"  Model: {daperl_config.analysis_llm.model}")
print(f"  API Key set: {daperl_config.analysis_llm.api_key is not None}")

