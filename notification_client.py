import os
from typing import Any, Dict
import httpx
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("ADMIN_WEBHOOK_URL")

async def send_admin_notification(payload: Dict[str, Any]) -> None:
    """
    POST the given payload to the admin webhook URL.
    Raises httpx.HTTPError on non-2xx responses.
    """
    if not WEBHOOK_URL:
        raise RuntimeError("ADMIN_WEBHOOK_URL not configured")

    print("Sending admin notification to:", WEBHOOK_URL)
    print("Payload:", payload)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(WEBHOOK_URL, json=payload)
        # Log the status and body returned by httpbin
        print(f"Notification response status: {response.status_code}")
        print("Notification response body:", response.text)
        response.raise_for_status()