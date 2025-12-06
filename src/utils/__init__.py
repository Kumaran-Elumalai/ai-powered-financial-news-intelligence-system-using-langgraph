# src/utils/__init__.py

def canonical_text(doc: dict) -> str:
    """
    Combine title + description into a clean canonical text
    for embedding and dedupe purposes.
    """
    title = doc.get("title", "") or ""
    desc = doc.get("description", "") or ""
    return f"{title}\n\n{desc}".strip()
