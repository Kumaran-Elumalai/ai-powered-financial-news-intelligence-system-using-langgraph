# src/llm/llm_client.py

import requests

# Ollama local server endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"   

def call_llm(prompt: str, max_tokens: int = 200) -> str:
    """
    Unified LLM caller for the whole system.
    Uses local Ollama model instead of HuggingFace.
    """
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "max_tokens": max_tokens
            },
            timeout=180
        )

        r.raise_for_status()
        data = r.json()

        return data.get("response", "").strip()

    except Exception as ex:
        return f"[LLM Error: {ex}]"
