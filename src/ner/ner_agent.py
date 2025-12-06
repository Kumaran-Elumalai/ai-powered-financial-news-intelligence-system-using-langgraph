# src/ner/ner_agent.py
import logging
from src.utils import canonical_text
from src.utils.logger import get_logger

logger = get_logger("NERAgent")

# Try to import user's custom NER. If not available, fallback to spaCy.
try:
    from src.ner.custom_ner import final_ner_logic_v4
    HAS_CUSTOM_NER = True
    logger.info("Using custom final_ner_logic_v4 NER backend.")
except Exception as ex:
    HAS_CUSTOM_NER = False
    logger.warning(f"Custom NER not found; falling back to spaCy. Reason: {ex}")

if not HAS_CUSTOM_NER:
    import spacy
    # use the small English model (already installed via requirements)
    nlp = spacy.load("en_core_web_sm")

def run_ner_on_text(text: str):
    """
    Return list of entities: [{'text':..., 'label':..., 'start':..., 'end':..., 'source':...}, ...]
    """
    text = text or ""
    if HAS_CUSTOM_NER:
        try:
            ents = final_ner_logic_v4(text)
            # Normalize to standard keys if required by your implementation:
            normalized = []
            for e in ents:
                text_val = e.get("text") or e.get("entity") or ""
                label_val = e.get("label") or e.get("type") or "MISC"

                normalized.append({
                    "text": text_val,
                    "label": label_val,
                    "start": e.get("start"),
                    "end": e.get("end"),
                    "source": e.get("source", "custom"),
                    "confidence": e.get("confidence")
                })

            return normalized
        except Exception as ex:
            logger.exception("Custom NER failed, falling back to spaCy: %s", ex)

    # spaCy fallback
    doc = nlp(text)
    out = []
    for ent in doc.ents:
        out.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
            "source": "spacy",
            "confidence": None
        })
    return out

def run_ner(doc: dict):
    """
    Enrich the doc with a `entities` field (list of entity dicts).
    Returns the doc (modified).
    """
    combined = canonical_text(doc)
    entities = run_ner_on_text(combined)
    # Optionally deduplicate overlapping entities by text (very simple)
    seen = set()
    unique = []
    for e in entities:
        text_val = (e.get("text") or "").strip().lower()
        label_val = e.get("label") or "MISC"
        key = (text_val, label_val)
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)
    doc["entities"] = unique
    return doc
