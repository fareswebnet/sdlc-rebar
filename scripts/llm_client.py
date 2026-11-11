#!/usr/bin/env python3
"""Tiny OpenAI-compatible chat client (stdlib only): Ollama, vLLM, llama.cpp server, LM Studio, or a hosted API."""

from __future__ import annotations

import json
import subprocess
import tempfile
import urllib.request

DEFAULT_BASE_URL = "http://localhost:11434/v1"
CLAUDE_CLI = "claude-cli"  # pass as base_url to use the local Claude Code CLI in print mode
AGY_CLI = "agy-cli"  # pass as base_url to use the local Antigravity CLI (agy) in print mode


def _chat_claude_cli(messages: list[dict], model: str, timeout: int) -> str:
    """Single-turn call through `claude -p` with tools, skills, MCP connectors, and settings disabled so only the given prompt applies."""
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    user = "\n\n".join(f"{m['role'].upper()}: {m['content']}" if m["role"] == "assistant" else m["content"] for m in messages if m["role"] != "system")
    command = ["claude", "-p", "--model", model, "--tools", "", "--disable-slash-commands", "--no-session-persistence", "--setting-sources", "", "--strict-mcp-config"]
    if system:
        command += ["--system-prompt", system]
    result = subprocess.run(command, input=user, capture_output=True, text=True, timeout=timeout, cwd=tempfile.gettempdir())
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr.strip()[:500]}")
    return result.stdout.strip()


def _chat_agy_cli(messages: list[dict], model: str, timeout: int) -> str:
    """Single-turn call through `agy -p`. agy has no flag to remove its tools or set a system prompt, so the system text is prefixed to the prompt and the run happens in an empty directory."""
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    user = "\n\n".join(m["content"] for m in messages if m["role"] != "system")
    prompt = f"{system}\n\n---\n\n{user}" if system else user
    with tempfile.TemporaryDirectory() as empty:
        result = subprocess.run(["agy", "--disable-slash-commands", "--model", model, f"-p={prompt}"], capture_output=True, text=True, timeout=timeout, cwd=empty)
    if result.returncode != 0 or "AGY_ERROR" in result.stdout + result.stderr:
        raise RuntimeError(f"agy failed: {(result.stderr or result.stdout).strip()[:500]}")
    return result.stdout.strip()


def chat(messages: list[dict], model: str, base_url: str = DEFAULT_BASE_URL, api_key: str | None = None,
         temperature: float = 0.0, timeout: int = 300) -> str:
    if base_url == CLAUDE_CLI:
        return _chat_claude_cli(messages, model, timeout)
    if base_url == AGY_CLI:
        return _chat_agy_cli(messages, model, timeout)
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps({"model": model, "messages": messages, "temperature": temperature}).encode(),
        headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {api_key}"} if api_key else {})},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode())
    return payload["choices"][0]["message"]["content"]
