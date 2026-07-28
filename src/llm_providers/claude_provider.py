"""Claude LLM Provider via Anthropic API"""

import os
from typing import Optional
from anthropic import Anthropic
from .base import BaseLLMProvider


class ClaudeFoundryProvider(BaseLLMProvider):
    """Claude provider using Anthropic API.

    Required environment variables:
        CLAUDE_API_KEY  - Anthropic API key
        CLAUDE_BASE_URL - Custom endpoint (optional, defaults to api.anthropic.com)
    """

    def __init__(self, model_name: str = "claude-opus-4-1", temperature: float = 0.0, max_tokens: int = 6000):
        super().__init__(model_name, temperature, max_tokens)
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY environment variable not set")
        base_url = os.getenv("CLAUDE_ENDPOINT")
        self.client = Anthropic(api_key=api_key, base_url=base_url) if base_url else Anthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "claude"

    def call(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        kwargs = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": self.max_tokens,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        try:
            response = self.client.messages.create(**kwargs)
            if not response.content:
                print(f"Empty response content (stop_reason={response.stop_reason})")
                return ""
            if response.content[0].type != "text":
                print(f"Unexpected content type: {response.content[0].type}")
                return ""
            return response.content[0].text
        except Exception as e:
            print(f"Error during Claude API call: {e}")
            raise
