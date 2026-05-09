"""
AgentLoader — loads AgentConfig from different sources.

Priority (highest → lowest):
  1. Explicit dict / kwargs passed programmatically
  2. YAML file (path from AGENT_CONFIG_PATH env var or argument)
  3. Environment variables (AGENT_* prefix)
  4. Built-in defaults in AgentConfig

Single-agent design: we always load exactly one config.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from .config import AgentConfig, EvaluationConfig, LLMConfig, MemoryConfig, RAGConfig

logger = logging.getLogger(__name__)


class AgentLoader:
    """Responsible for constructing an AgentConfig from external sources."""

    # ------------------------------------------------------------------ #
    #  Public entry point                                                  #
    # ------------------------------------------------------------------ #

    @classmethod
    def load(
        cls,
        config_path: str | Path | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> AgentConfig:
        """
        Build and return an AgentConfig.

        Args:
            config_path: Optional path to a YAML config file.
                         Falls back to the AGENT_CONFIG_PATH env var.
            overrides:   Optional dict that is merged on top of whatever
                         was loaded from YAML/env.  Useful for tests.
        """
        data: dict[str, Any] = {}

        # 1. Load from YAML if available
        yaml_data = cls._load_yaml(config_path)
        data.update(yaml_data)

        # 2. Overlay env-var values (flat AGENT_* keys)
        env_data = cls._load_env()
        cls._deep_merge(data, env_data)

        # 3. Apply explicit overrides last
        if overrides:
            cls._deep_merge(data, overrides)

        config = AgentConfig(**data)
        logger.info(
            "AgentConfig loaded: id=%s  llm=%s/%s  rag=%s  memory=%s",
            config.id,
            config.llm.provider,
            config.llm.model,
            "enabled" if config.rag.enabled else "disabled",
            config.memory.backend,
        )
        return config

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    @classmethod
    def _load_yaml(cls, config_path: str | Path | None) -> dict[str, Any]:
        path = config_path or os.getenv("AGENT_CONFIG_PATH")
        if not path:
            return {}

        path = Path(path)
        if not path.exists():
            logger.warning("Agent config file not found: %s — using defaults.", path)
            return {}

        try:
            import yaml  # optional dependency
        except ImportError:
            logger.warning("PyYAML not installed; skipping YAML config loading.")
            return {}

        with path.open() as f:
            data = yaml.safe_load(f) or {}

        logger.debug("Loaded YAML config from %s", path)
        return data

    @classmethod
    def _load_env(cls) -> dict[str, Any]:
        """
        Map flat AGENT_* environment variables into a nested dict.

        Examples
        --------
        AGENT_ID=chatbot                  → {"id": "chatbot"}
        AGENT_LLM_PROVIDER=openai         → {"llm": {"provider": "openai"}}
        AGENT_LLM_MODEL=gpt-4o            → {"llm": {"model": "gpt-4o"}}
        AGENT_RAG_ENABLED=false           → {"rag": {"enabled": False}}
        AGENT_MEMORY_BACKEND=memory       → {"memory": {"backend": "memory"}}
        """
        mapping: dict[str, Any] = {}
        prefix = "AGENT_"

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            # Strip prefix, lowercase, split on _
            parts = key[len(prefix) :].lower().split("_", 1)
            parsed = cls._parse_env_value(value)

            if len(parts) == 1:
                mapping[parts[0]] = parsed
            else:
                # Nested: e.g. ["llm", "provider"]
                group, field = parts
                mapping.setdefault(group, {})[field] = parsed

        return mapping

    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """Coerce string env values to Python primitives."""
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value

    @staticmethod
    def _deep_merge(base: dict, overlay: dict) -> None:
        """Merge overlay into base in-place, recursing into nested dicts."""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                AgentLoader._deep_merge(base[key], value)
            else:
                base[key] = value