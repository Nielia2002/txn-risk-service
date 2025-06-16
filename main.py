import os
import logging

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge

from gemini_client import analyze_transaction
from notification_client import send_admin_notification

# 1) Load .env
load_dotenv()

# 2) Set up structured logging
logger = logging.getLogger("txn-service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

# 3) Read API key
API_KEY = os.getenv("API_KEY")

# 4) Prometheus gauge for risk score
risk_score_gauge = Gauge(
    "transaction_risk_score",
    "Risk score assigned to each transaction",
    ["currency", "country"]
)

# 5) Create FastAPI app
app = FastAPI(title="Transaction Risk Service", debug=True)

# 6) Instrument app for Prometheus metrics
Instrumentator().instrument(app).expose(app)

# 7) Define your data models
class TransactionWebhook(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction ID")
    user_id:        str = Field(..., description="User who made the transaction")
    amount:         float = Field(..., gt=0, description="Amount in the given currency")
    currency:       str = Field(..., description="ISO currency code, e.g. USD")
    timestamp:      str = Field(..., description="RFC3339 timestamp of the transaction")
    country:        str = Field(..., description="2-letter country code")

class AdminNotification(BaseModel):
    transaction: TransactionWebhook
    analysis:    dict

# 8) Health check
@app.get("/")
async def root():
    return {"message": "txn-risk-service is up!"}

# 9) Transaction webhook
@app.post("/webhook/transaction")
async def transaction_webhook(
    payload: TransactionWebhook,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    # 1) Authenticate
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # 2) LLM analysis with error-branching
    try:
        analysis = analyze_transaction(payload.model_dump())
    except RuntimeError as e:
        msg = str(e)
        if "rate limit" in msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=msg
            )
    except Exception as e:
        # unexpected errors
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )

    # ← record the custom metric here
    risk_score_gauge.labels(
        currency=payload.currency,
        country=payload.country
    ).set(analysis["risk_score"])

    # 3) Structured logging
    logger.info("Analysis complete for txn %s: %s", payload.transaction_id, analysis)

    # 4) Notify admin in background
    notification = AdminNotification(transaction=payload, analysis=analysis).model_dump()
    try:
        await send_admin_notification(notification)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Notify error: {e}")

    # 5) Return success response
    return {
        "status": "received",
        "transaction_id": payload.transaction_id,
        "analysis": analysis
    }
