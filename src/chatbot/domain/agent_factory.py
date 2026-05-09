"""
Generic Agent Factory — creates chatbot instances with default configurations.

This is a convenience factory for the domain layer.
The application layer has a separate AgentFactory (in application/agent/factory.py)
that manages LLM, embeddings, and vector stores.

This domain factory is primarily for creating Chatbot configuration objects
with sensible defaults for the heat pump domain.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .chatbot import Chatbot


class BotFactory:
    """Factory for creating preconfigured Chatbot instances."""

    @staticmethod
    def create_heat_pump_assistant() -> Chatbot:
        """Create a chatbot configured for heat pump system support."""
        return Chatbot(
            id="heat-pump-assistant",
            name="Heat Pump Assistant",
            description="Intelligent assistant for heat pump system inquiries and support",
            system_prompt=(
                "You are a helpful and knowledgeable assistant specialized in heat pump systems. "
                "Your role is to provide clear, accurate information about heat pump operation, "
                "efficiency, maintenance, troubleshooting, and performance optimization.\n\n"
                "When answering questions:\n"
                "1. Be accurate and cite relevant documentation when possible\n"
                "2. Explain technical concepts in accessible terms\n"
                "3. Provide practical, actionable advice\n"
                "4. If unsure, admit it and suggest contacting support\n"
                "5. Focus on Tabreed systems specifically when relevant\n"
                "6. Prioritize safety and efficiency considerations"
            ),
            tools=["retriever"],
            config={
                "temperature": 0.7,
                "max_tokens": 1024,
                "response_format": "conversational",
                "domain": "heat_pump",
                "company": "Tabreed Thermal Control",
            },
            metadata={
                "version": "2.0",
                "created_date": datetime.utcnow().isoformat(),
                "domain_focus": ["heat_pump", "hvac", "efficiency", "maintenance"],
                "supported_languages": ["en"],
                "capabilities": [
                    "technical_qa",
                    "troubleshooting",
                    "efficiency_advice",
                    "maintenance_scheduling",
                    "conversational",
                ],
            },
        )

    @staticmethod
    def create_generic_assistant(
        name: str = "Assistant",
        system_prompt: str | None = None,
        tools: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ) -> Chatbot:
        """Create a generic chatbot with custom configuration."""
        return Chatbot(
            id=name.lower().replace(" ", "-"),
            name=name,
            description=f"{name} - A helpful conversational assistant",
            system_prompt=(
                system_prompt
                or (
                    "You are a helpful and friendly assistant. "
                    "Answer questions clearly and concisely. "
                    "If unsure about something, say so honestly."
                )
            ),
            tools=tools or ["retriever"],
            config=config
            or {
                "temperature": 0.7,
                "max_tokens": 1024,
            },
            metadata={
                "version": "1.0",
                "created_date": datetime.utcnow().isoformat(),
            },
        )
