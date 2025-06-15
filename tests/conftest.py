import os
import sys
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Add the main application directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load any .env you may have locally
load_dotenv()

# This will be overridden in the test cases
from main import app

@pytest.fixture(scope="module")
def client():
    """
    Provides a TestClient for the FastAPI app.
    """
    return TestClient(app)
