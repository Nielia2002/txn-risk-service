import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL       = os.getenv("HF_MODEL", "gpt-3.5-turbo")  # or any HF hosted model
if not HF_API_TOKEN:
    raise RuntimeError("HF_API_TOKEN not set in .env")

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type":  "application/json",
}


def analyze_transaction(txn: dict) -> dict:
    # build the same prompt you used against OpenAI:
    prompt = (
        "You are a financial risk analysis engine. "
        "Given the following JSON transaction, output a JSON object with exactly "
        "these keys:\n\n"
        "  • risk_score (a number between 0 and 1)\n"
        "  • risk_factors (an array of strings explaining what drove the score)\n"
        "  • reasoning (a concise explanation in one paragraph)\n"
        "  • recommended_action (one-sentence suggested next step)\n\n"
        "Here is the transaction:\n\n"
        f"{json.dumps(txn, indent=2)}\n\n"
        "Respond **ONLY** with the JSON object."
    )

    payload = {
        "inputs": prompt,
        # some models support `options: { wait_for_model: true }`
        "options": { "wait_for_model": True }
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        # HF returns a list of generations; each has `generated_text`
        generations = resp.json()
        text = generations[0]["generated_text"]
        return json.loads(text.strip())

    except Exception as e:
        # fallback exactly like your OpenAI client
        return {
            "risk_score": 0.5,
            "risk_factors": [f"fallback due to error: {e}"],
            "reasoning": "Default analysis because of an external error.",
            "recommended_action": "Please review manually."
        }
