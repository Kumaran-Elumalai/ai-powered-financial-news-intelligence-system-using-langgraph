import requests

# Ollama local server endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"   # Your installed model


def call_ollama(prompt: str, max_tokens=200) -> str:
    """
    Calls local Ollama safely with extended timeout.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "max_tokens": max_tokens
            },
            timeout=240   # 4 minutes initial load allowed
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()

    except Exception as e:
        return f"[LLM Error: {e}]"



# -------------------------------------------------------------
#  ARTICLE SUMMARY (NO HALLUCINATIONS)
# -------------------------------------------------------------
def summarize_article(title: str, body: str) -> str:
    prompt = f"""
Summarize this article in exactly 2 short bullet points.
Use only the information present. 
No guessing.

Article:
{body}

SUMMARY:
"""
    return call_ollama(prompt, max_tokens=120)


# -------------------------------------------------------------
#  IMPACT EXPLANATION (STRICT, NO GUESSING)
# -------------------------------------------------------------
def explain_impact(title: str, body: str, company: str) -> str:
    prompt = f"""
You are a financial analyst.
Explain in 2 sentences how this article impacts **{company}**.

RULES:
- Use only information present in the article.
- No hallucinations.
- If no clear impact exists, respond exactly with:
  "No direct impact found."

TITLE: {title}

ARTICLE:
{body}

EXPLANATION:
"""
    return call_ollama(prompt, max_tokens=120)
