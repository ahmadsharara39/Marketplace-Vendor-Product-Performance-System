import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def detect_intent(prompt: str) -> dict:
    """
    Returns:
      { "intent": "add_vendor" | "add_product" | "qa" | "ambiguous", "confidence": 0..1, "reason": "..." }
    """
    system = """
You are an intent classifier for a marketplace chatbot UI.
Decide whether the user wants to:
- add_vendor: user wants to add/insert/register/onboard a vendor
- add_product: user wants to add/insert/register/onboard a product
- qa: user is asking a question (analytics, last added, performance, etc.)
- ambiguous: unclear whether vendor or product

Rules:
- If the user asks things like "last vendor added" or "last product added" -> qa
- If the user asks to "add" something but doesn't specify vendor vs product -> ambiguous
- Output ONLY valid JSON. No extra text.
"""

    user = f'Prompt: """{prompt}"""'

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    # Safe parse
    import json
    try:
        return json.loads(resp.choices[0].message.content)
    except Exception:
        # fallback if model ever returns weird output
        return {"intent": "qa", "confidence": 0.0, "reason": "fallback_parse_failed"}