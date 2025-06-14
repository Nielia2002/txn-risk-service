import os, json, openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def analyze_transaction(txn: dict) -> dict:
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

    try:
        resp = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You analyze transaction risk."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0
        )
        return json.loads(resp.choices[0].message.content.strip())

    except openai.RateLimitError as e:
        # *** FALLBACK DUMMY ANALYSIS ***
        return {
            "risk_score": 0.5,
            "risk_factors": ["fallback due to rate limit"],
            "reasoning": "Default analysis because quota was exceeded.",
            "recommended_action": "Please review manually."
        }

    except Exception as e:
        # For any other error, also return dummy so we can test notifications
        return {
            "risk_score": 0.5,
            "risk_factors": [f"fallback due to error: {e}"],
            "reasoning": "Default analysis because of an internal error.",
            "recommended_action": "Please review manually."
        }
