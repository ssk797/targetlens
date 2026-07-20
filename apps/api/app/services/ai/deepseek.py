from collections.abc import Sequence
from typing import Any

import httpx
from pydantic import SecretStr


class DeepSeekProviderError(RuntimeError):
    """Provider failures are surfaced without leaking request headers or keys."""


Message = dict[str, str]


class DeepSeekClient:
    def __init__(self, api_key: SecretStr, base_url: str, fast_model: str, reasoning_model: str) -> None:
        self._api_key = api_key.get_secret_value().strip()
        self._base_url = base_url.rstrip("/")
        self._fast_model = fast_model
        self._reasoning_model = reasoning_model
        if not self._api_key:
            raise DeepSeekProviderError("DEEPSEEK_API_KEY is empty")

    @classmethod
    def from_settings(cls, settings: Any) -> "DeepSeekClient":
        if settings.deepseek_api_key is None:
            raise DeepSeekProviderError("DEEPSEEK_API_KEY is not configured")
        return cls(settings.deepseek_api_key, settings.deepseek_base_url, settings.deepseek_model_fast, settings.deepseek_model_reasoning)

    async def complete(self, messages: Sequence[Message], *, reasoning: bool = False, max_tokens: int = 1200) -> str:
        payload: dict[str, Any] = {
            "model": self._reasoning_model if reasoning else self._fast_model,
            "messages": list(messages),
            "stream": False,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }
        if reasoning:
            payload["thinking"] = {"type": "enabled"}
            payload["reasoning_effort"] = "high"

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0)) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise DeepSeekProviderError("DeepSeek request failed") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise DeepSeekProviderError("DeepSeek response did not contain a message") from exc
        if not isinstance(content, str) or not content.strip():
            raise DeepSeekProviderError("DeepSeek response was empty")
        return content.strip()
