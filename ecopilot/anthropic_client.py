from __future__ import annotations

import httpx


class DuoAnthropicClient:
    """Thin client wrapper for Anthropic calls through GitLab-managed endpoints."""

    def __init__(self, endpoint: str, token: str, model: str, timeout: float = 20.0):
        self._endpoint = endpoint
        self._token = token
        self._model = model
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        if not self._endpoint or not self._token:
            raise RuntimeError("duo anthropic client is not configured")
        payload = {
            "model": self._model,
            "max_tokens": 1200,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}
        response = httpx.post(self._endpoint, json=payload, headers=headers, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        content = data.get("content")
        if isinstance(content, list) and content:
            text = content[0].get("text", "")
            if isinstance(text, str) and text.strip():
                return text.strip()
        if isinstance(content, str) and content.strip():
            return content.strip()
        raise RuntimeError("invalid anthropic response format")

