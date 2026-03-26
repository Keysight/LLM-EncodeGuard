"""Base LLM Provider Interface"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, model_name: str, temperature: float = 0.0, max_tokens: int = 6000):
        """
        Initialize base LLM provider.

        Args:
            model_name: Name of the model to use
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'openai', 'gemini', 'custom')"""
        pass

    @abstractmethod
    def call(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call the LLM with a user prompt and optional system prompt.

        Args:
            user_prompt: The user's message/question
            system_prompt: Optional system instructions/context

        Returns:
            The LLM's response text
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name}, temp={self.temperature})"
