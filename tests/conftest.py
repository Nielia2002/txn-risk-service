import os
import sys

# Insert the project root (one level up) into sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()               # load your .env
from main import app        # now this will resolve correctly

@pytest.fixture(scope="module")
def client():
    return TestClient(app)