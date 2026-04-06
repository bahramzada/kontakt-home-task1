import json
import logging
from typing import Any

import requests

from .config import Settings
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()  # Session reuse memory leak riskini azaldır.

    def evaluate(self, call_id: str, transcript: str) -> dict[str, Any]:
        if not self.settings.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY tapılmadı.")

        payload = {
            "model": self.settings.openrouter_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(call_id, transcript)},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        response = self.session.post(
            self.settings.openrouter_base_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=self.settings.request_timeout_seconds,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"LLM xətası: {response.status_code} - {response.text[:300]}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("LLM JSON parse edilə bilmədi: %s", content)
            raise RuntimeError("LLM cavabı JSON formatında deyil.") from exc
