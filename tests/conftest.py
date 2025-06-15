import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from fastapi.testclient import TestClient
import pytest

load_dotenv()               # load API_KEY, GEMINI_API_KEY, etc. into env

from main import app        # import the FastAPI app from main.py

@pytest.fixture(scope="module")
def client():
    """
    Provides a TestClient for the FastAPI app.
    """
    return TestClient(app)
