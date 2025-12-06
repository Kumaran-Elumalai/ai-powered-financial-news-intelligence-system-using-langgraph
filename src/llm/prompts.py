# SAFE, EXTRACTIVE, NON-HALLUCINATING PROMPTS

SUMMARY_PROMPT = """
You are an extractive financial summarizer.
Only use EXACT phrases from the provided article. 
Do NOT add any new information.
If a summary cannot be generated, reply: "Not enough information to summarize."

Write a single-sentence summary (max 20 words).

Article Title: {title}
Article Body: {body}

Extractive summary:
"""

IMPACT_EXPLAIN_PROMPT = """
You are an extractive financial impact assistant.
Only use information explicitly found in the article.
Do NOT infer, speculate, or hallucinate.
If the article does not clearly mention an impact on the company, reply exactly:
"No direct impact found."

Write 2 bullet points (if information exists), otherwise the line above.

Article Title: {title}
Article Body: {body}
Company of interest: {company}

Extractive explanation:
"""
