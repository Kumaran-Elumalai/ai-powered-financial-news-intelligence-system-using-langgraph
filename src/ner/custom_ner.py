# src/ner/custom_ner.py

import re
import spacy
from rapidfuzz import fuzz, process

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

# -----------------------------
# 1) Base Company List (expand later)
# -----------------------------
COMPANY_LIST = [
    "HDFC Bank", "ICICI Securities", "ICICI Bank", "Tejas Networks",
    "Bajaj Finance", "Persistent Systems",
    "Aditya Birla Fashion and Retail",
    "Wipro", "Infosys", "HDFC Life Insurance Company",
    "Patel Engineering"
]

# -----------------------------
# 2) Clean headline text
# -----------------------------
def clean_headline_text(text: str) -> str:
    """
    Removes leading action words (Buy, Sell, Reduce, etc.)
    Example: "Buy HDFC Bank..." → "HDFC Bank..."
    """
    return re.sub(
        r"^(Buy|Reduce|Accumulate|Sell|Hold)\s+",
        "",
        text,
        flags=re.I
    ).strip()

# -----------------------------
# 3) Fuzzy company name matching
# -----------------------------
def match_company_name(text: str):
    """
    Fuzzy match extracted entity against known companies.
    Returns best match if score >= 80 else None.
    """
    if not text:
        return None

    match, score, _ = process.extractOne(
        text,
        COMPANY_LIST,
        scorer=fuzz.WRatio
    )

    return match if score >= 80 else None

# -----------------------------
# 4) FINAL NER LOGIC (updated)
# -----------------------------
def final_ner_logic_v4(text: str):
    """
    Updated version of your NER logic:
    - Accepts a *single combined text*
    - Cleans headline
    - Detects MONEY patterns (Rs/₹)
    - Extracts spaCy entities
    - Applies fuzzy matching for company correction
    - Removes duplicates
    """

    full_text = clean_headline_text(text)
    doc = nlp(full_text)

    cleaned_entities = []

    # -----------------------------
    # 1) REGEX MONEY extraction
    # -----------------------------
    money_regex = r"(Rs\.?\s?\d[\d,]*|₹\s?\d[\d,]*)"
    money_matches = re.findall(money_regex, full_text)

    for m in money_matches:
        cleaned_entities.append({
            "entity": m.strip(),
            "type": "MONEY",
            "source": "regex_money"
        })

    # -----------------------------
    # 2) spaCy Named Entities
    # -----------------------------
    for ent in doc.ents:
        ent_text = ent.text.strip()
        ent_label = ent.label_

        # 2A — Try fuzzy match to known company names
        best_match = match_company_name(ent_text)
        if best_match:
            cleaned_entities.append({
                "entity": best_match,
                "type": "ORG",
                "source": "company_match"
            })
            continue

        # 2B — Skip CARDINAL if it's already counted as MONEY
        if ent_label == "CARDINAL" and any(ent_text in m for m in money_matches):
            continue

        # 2C — DATE → MONEY (if purely numeric)
        if ent_label == "DATE" and re.match(r"^[\d,]+$", ent_text):
            cleaned_entities.append({
                "entity": ent_text,
                "type": "MONEY",
                "source": "corrected_DATE"
            })
            continue

        # 2D — Keep spaCy entities
        cleaned_entities.append({
            "entity": ent_text,
            "type": ent_label,
            "source": "spacy"
        })

    # -----------------------------
    # 3) Remove Duplicates
    # -----------------------------
    final_unique = []
    seen = set()

    for e in cleaned_entities:
        key = (e["entity"].lower(), e["type"])
        if key not in seen:
            final_unique.append(e)
            seen.add(key)

    return final_unique
