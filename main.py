import os
import logging
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from openai_client import analyze_transaction
from notification_client import send_admin_notification

load_dotenv()  # loads API_KEY and ADMIN_WEBHOOK_URL from .env

# Set up structured logging
logger = logging.getLogger("txn-service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

API_KEY = os.getenv("API_KEY")

app = FastAPI(title="Transaction Risk Service")


class TransactionWebhook(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction ID")
    user_id:        str = Field(..., description="User who made the transaction")
    amount:         float = Field(..., gt=0, description="Amount in the given currency")
    currency:       str = Field(..., description="ISO currency code, e.g. USD")
    timestamp:      str = Field(..., description="RFC3339 timestamp of the transaction")
    country:        str = Field(..., description="2-letter country code")


class AdminNotification(BaseModel):
    transaction: TransactionWebhook
    analysis: dict


@app.get("/")
async def root():
    return {"message": "txn-risk-service is up!"}


@app.post("/webhook/transaction")
async def transaction_webhook(
    payload: TransactionWebhook,
    x_api_key: str = Header(...)
):
    # 1) Authenticate
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2) LLM analysis with error mapping
    try:
        analysis = analyze_transaction(payload.model_dump())
    except RuntimeError as e:
        msg = str(e)
        if "rate limit" in msg.lower():
            raise HTTPException(status_code=429, detail=msg)
        raise HTTPException(status_code=502, detail=msg)

    # Structured log instead of print
    logger.info("Analysis complete for txn %s: %s", payload.transaction_id, analysis)

    # 3) Admin notification
    notification = AdminNotification(transaction=payload, analysis=analysis).model_dump()
    try:
        await send_admin_notification(notification)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Notify error: {e}")

    # 4) Success response
    return {
        "status": "received",
        "transaction_id": payload.transaction_id,
        "analysis": analysis
    }
