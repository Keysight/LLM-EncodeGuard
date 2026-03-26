"""Google Gemini LLM Provider"""

import os
import requests
from typing import Optional
from .base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):


    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.0, max_tokens: int = 6000):
        super().__init__(model_name, temperature, max_tokens)
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    @property
    def provider_name(self) -> str:
        return "gemini"

    def call(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generation_config": {
                "temperature": self.temperature
            }
        }

        # Add system instruction if provided
        if system_prompt:
            payload["system_instruction"] = {
                "parts": [{"text": system_prompt}]
            }

        headers = {
            "Content-Type": "application/json"
        }

        # Use params to keep API key out of error messages
        params = {
            "key": self.api_key
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                params=params,
                timeout=180
            )
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.HTTPError as e:
            # Sanitize error message to not expose API key
            error_msg = str(e).replace(self.api_key, "***API_KEY***")
            print(f"Error during Gemini API call: {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            raise
