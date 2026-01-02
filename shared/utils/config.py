"""
Configuration utilities.
"""

import os
from typing import Any, Optional
from pathlib import Path


def get_env(key: str, default: Any = None) -> Any:
    """
    Get environment variable with optional default.

    Args:
        key: Environment variable name
        default: Default value if not set

    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)


def load_config(env_file: str = ".env") -> dict:
    """
    Load configuration from environment file.

    Args:
        env_file: Path to .env file

    Returns:
        Dictionary of configuration values
    """
    config = {}

    # Try to load from .env file
    env_path = Path(env_file)
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            # Manual parsing if python-dotenv not installed
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

    # Load standard config keys
    config["anthropic_api_key"] = get_env("ANTHROPIC_API_KEY")
    config["openai_api_key"] = get_env("OPENAI_API_KEY")
    config["default_model"] = get_env("DEFAULT_MODEL", "claude-sonnet-4-20250514")
    config["temperature"] = float(get_env("TEMPERATURE", "0.3"))
    config["chroma_persist_dir"] = get_env("CHROMA_PERSIST_DIR", "./data/chroma")
    config["log_level"] = get_env("LOG_LEVEL", "INFO")

    return config


def get_llm_config() -> dict:
    """
    Get LLM-specific configuration.

    Returns:
        LLM configuration dictionary
    """
    return {
        "model": get_env("DEFAULT_MODEL", "claude-sonnet-4-20250514"),
        "temperature": float(get_env("TEMPERATURE", "0.3")),
        "max_tokens": int(get_env("MAX_TOKENS", "4096")),
        "api_key": get_env("ANTHROPIC_API_KEY")
    }


def get_vector_store_config() -> dict:
    """
    Get vector store configuration.

    Returns:
        Vector store configuration dictionary
    """
    return {
        "persist_directory": get_env("CHROMA_PERSIST_DIR", "./data/chroma"),
        "collection_name": get_env("CHROMA_COLLECTION", "policies"),
        "embedding_model": get_env("EMBEDDING_MODEL", "text-embedding-3-small")
    }
