#!/usr/bin/env python3
"""Tiny OpenAI-compatible chat client (stdlib only): Ollama, vLLM, llama.cpp server, LM Studio, or a hosted API."""

from __future__ import annotations

import json
import urllib.request

DEFAULT_BASE_URL = "http://localhost:11434/v1"


def chat(messages: list[dict], model: str, base_url: str = DEFAULT_BASE_URL, api_key: str | None = None,
         temperature: float = 0.0, timeout: int = 300) -> str:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps({"model": model, "messages": messages, "temperature": temperature}).encode(),
        headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {api_key}"} if api_key else {})},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode())
    return payload["choices"][0]["message"]["content"]
