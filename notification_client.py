import os
from typing import Any, Dict
import httpx
from dotenv import load_dotenv
import logging

load_dotenv()
WEBHOOK_URL = os.getenv("ADMIN_WEBHOOK_URL")

logger = logging.getLogger("txn-service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


async def send_admin_notification(payload: Dict[str, Any]) -> None:
    """
    POST the given payload to the admin webhook URL.
    Raises httpx.HTTPError on non-2xx responses.
    """
    if not WEBHOOK_URL:
        raise RuntimeError("ADMIN_WEBHOOK_URL not configured")

    logger.info("Sending admin notification to: %s", WEBHOOK_URL)
    logger.debug("↪ Payload: %r", payload)

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(WEBHOOK_URL, json=payload)
        logger.info(" Notification response status: %d", r.status_code)
        logger.debug(" Notification response body: %s", r.text)
        r.raise_for_status()