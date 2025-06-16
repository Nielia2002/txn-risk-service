import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

def analyze_transaction(txn: dict) -> dict:
    prompt = f"""
You are a fraud-risk engine.
Rate this transaction 0.0–1.0 and return JSON with exactly:
  • risk_score
  • risk_factors
  • reasoning
  • recommended_action (allow|review|block)

Buckets: 0–0.3=allow,0.3–0.7=review,0.7–1=block.

Consider:
 • geo: customer vs payment country, IP mismatch, high-risk jurisdictions
 • timing: odd hours, bursts of activity
 • amount vs merchant norms
 • payment method type/new-method risk
 • merchant category, fraud rate & reputation

Transaction:
{json.dumps(txn, indent=2)}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You analyze transaction risk."},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.0
    )
    raw = response.choices[0].message.content or ""

    # Strip markdown fences if present
    cleaned = re.sub(r"^```(?:json)?\s*\r?\n", "", raw, flags=re.IGNORECASE)
    cleaned = re.sub(r"\r?\n```$", "", cleaned, flags=re.IGNORECASE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON from model:\n---\n{cleaned}\n---")
