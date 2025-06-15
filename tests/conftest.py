import os
import sys

# 1) Force a dummy API key for Gemini / OpenAI so the client _init_ won't throw
os.environ.setdefault("GEMINI_API_KEY", "testkey")
os.environ.setdefault("OPENAI_API_KEY", "testkey")

# 2) Add project root to sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Load  .env 
load_dotenv()

#  import the app
from main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)
