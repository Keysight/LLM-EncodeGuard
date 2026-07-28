"""Custom LLM Provider for self-hosted or third-party endpoints"""

import requests
import json
from typing import Optional
from .base import BaseLLMProvider


class CustomLLMProvider(BaseLLMProvider):
    """Provider for custom LLM endpoints (compatible with OpenAI API format)"""

    def __init__(
        self,
        model_name: str,
        endpoint: str = "http://localhost:8000",
        temperature: float = 0.0,
        max_tokens: int = 6000
    ):

        super().__init__(model_name, temperature, max_tokens)
        self.endpoint = endpoint.rstrip('/')
        self.api_url = f"{self.endpoint}/v1/chat/completions"

    @property
    def provider_name(self) -> str:
        return "custom"

    def call(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a helpful assistant."})

        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "messages": messages,
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=200,
                verify=False
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Handle models that include thinking tags
            if "</think>" in content:
                content = content.split("</think>", 1)[-1].strip()

            return content
        except Exception as e:
            print(f"Error during custom LLM API call: {e}")
            raise
