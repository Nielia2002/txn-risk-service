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
    prompt = (
    "You are a financial risk analysis engine.  Given the following JSON transaction, output a JSON object with exactly these keys:\n\n"
    "  • risk_score (0–1)\n"
    "  • risk_factors (array of strings explaining what drove the score; be sure to consider:\n"
    "      Payment method indicators: type (card, bank-transfer, crypto), whether it's new to the user, and any known associated risks.\n"
    "      Merchant factors: merchant category code, known fraud rates for that category, and merchant reputation history.\n"
    "      Transaction amount, currency, customer and payment-method country alignment, high-value flags, high-risk countries.\n"
    "  )\n"
    "  • reasoning (one-paragraph explanation)\n"
    "  • recommended_action (one sentence)\n\n"
    f"Here is the transaction:\n\n{json.dumps(txn, indent=2)}\n\nRespond **ONLY** with the JSON object."
)


    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",  "content": "You analyze transaction risk."},
            {"role": "user",    "content": prompt},
        ],
        temperature=0.0
    )
    raw = response.choices[0].message.content or ""

    # remove opening ```json line (with newline) and closing ``` fence
    cleaned = re.sub(r"^```(?:json)?\s*\r?\n", "", raw, flags=re.IGNORECASE)
    cleaned = re.sub(r"\r?\n```$", "", cleaned, flags=re.IGNORECASE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON from model:\n---\n{cleaned}\n---")
