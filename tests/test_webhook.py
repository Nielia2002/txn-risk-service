import os
import pytest
from fastapi import status
from fastapi.testclient import TestClient
import main

@pytest.fixture(scope="module")
def client():
    return TestClient(main.app)

@pytest.fixture(autouse=True)
def stub_and_set_api_key(monkeypatch):
    """
    Sets up test environment by stubbing and overriding key functions and variables.

    This function performs the following actions:
    1. Sets a known API key in the environment and overrides the `API_KEY` in the `main` module.
    2. Stubs the `analyze_transaction` function in the `main` module to return a fixed response for testing.
    3. Stubs the `send_admin_notification` function in the `main` module to simulate a no-op asynchronous call.

    Args:
        monkeypatch: pytest's monkeypatch fixture used to modify or override attributes and environment variables during testing.
    """
    # 1) Set a known API_KEY in the environment and override the API_KEY in the main module
    monkeypatch.setenv("API_KEY", "testkey")
    monkeypatch.setattr(main, "API_KEY", "testkey")

    # 2) Stub the LLM call
    def fake_analyze(txn):
        return {
            "risk_score": 0.42,
            "risk_factors": ["test factor"],
            "reasoning": "Test reasoning.",
            "recommended_action": "Test action."
        }
    monkeypatch.setattr(main, "analyze_transaction", fake_analyze)

    # 3) Stub the notification call
    async def fake_notify(payload):
        return None
    monkeypatch.setattr(main, "send_admin_notification", fake_notify)


def test_health_check(client: TestClient):
    res = client.get("/")
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {"message": "txn-risk-service is up!"}


def test_unauthorized_missing_key(client: TestClient):
    payload = {
        "transaction_id": "t1",
        "user_id": "u1",
        "amount": 1.0,
        "currency": "USD",
        "timestamp": "2025-06-14T00:00:00Z",
        "country": "US"
    }
    res = client.post("/webhook/transaction", json=payload)
    assert res.status_code in (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_401_UNAUTHORIZED
    )


def test_unauthorized_wrong_key(client: TestClient):
    payload = {
        "transaction_id": "t2",
        "user_id": "u2",
        "amount": 2.0,
        "currency": "USD",
        "timestamp": "2025-06-14T00:00:00Z",
        "country": "US"
    }
    res = client.post(
        "/webhook/transaction",
        json=payload,
        headers={"X-API-Key": "wrong-key"}
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_successful_transaction(client: TestClient):
    payload = {
        "transaction_id": "t3",
        "user_id": "u3",
        "amount": 3.0,
        "currency": "USD",
        "timestamp": "2025-06-14T00:00:00Z",
        "country": "US"
    }
    headers = {"X-API-Key": os.getenv("API_KEY")}
    res = client.post(
        "/webhook/transaction",
        json=payload,
        headers=headers
    )
    assert res.status_code == status.HTTP_200_OK

    body = res.json()
    assert body["status"] == "received"
    assert body["transaction_id"] == "t3"

    analysis = body["analysis"]
    assert analysis["risk_score"] == 0.42
    assert analysis["reasoning"] == "Test reasoning."
    assert analysis["recommended_action"] == "Test action."
    assert "test factor" in analysis["risk_factors"]


@pytest.mark.parametrize("exc,expected", [
    (RuntimeError("rate limit"), status.HTTP_429_TOO_MANY_REQUESTS),
    (RuntimeError("something else"), status.HTTP_502_BAD_GATEWAY),
])
def test_error_branches(client: TestClient, monkeypatch, exc, expected):
    # Force analyze_transaction to raise
    monkeypatch.setattr(
        main,
        "analyze_transaction",
        lambda txn: (_ for _ in ()).throw(exc)
    )

    payload = {
        "transaction_id": "t4",
        "user_id": "u4",
        "amount": 4.0,
        "currency": "USD",
        "timestamp": "2025-06-14T00:00:00Z",
        "country": "US"
    }
    headers = {"X-API-Key": os.getenv("API_KEY")}
    res = client.post(
        "/webhook/transaction",
        json=payload,
        headers=headers
    )
    assert res.status_code == expected
    assert "detail" in res.json()
