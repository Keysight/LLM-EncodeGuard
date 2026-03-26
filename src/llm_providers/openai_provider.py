"""OpenAI LLM Provider"""

import os
from typing import Optional
from openai import OpenAI
from .base import BaseLLMProvider


def get_max_tokens_for_model(model_name: str, requested_max_tokens: int = 6000) -> int:
    """Get appropriate max_tokens based on model capabilities"""
    # GPT-3.5 models have 4096 token limit
    if "gpt-3.5" in model_name.lower():
        return min(requested_max_tokens, 4096)
    # GPT-4 and newer models support higher limits
    return requested_max_tokens


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider for GPT models"""

    def __init__(self, model_name: str = "gpt-4.1-mini", temperature: float = 0.0, max_tokens: int = 6000):
        # Adjust max_tokens based on model capabilities
        adjusted_max_tokens = get_max_tokens_for_model(model_name, max_tokens)
        super().__init__(model_name, temperature, adjusted_max_tokens)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    def call(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=180
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            raise


class OpenAIJudge(BaseLLMProvider):
    """OpenAI provider specifically for judging responses"""

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        super().__init__(model_name, temperature, max_tokens=1000)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "openai-judge"

    def call(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call OpenAI API for judging"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=180
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during OpenAI judge call: {e}")
            raise
