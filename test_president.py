from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app  # your FastAPI file

client = TestClient(app)
