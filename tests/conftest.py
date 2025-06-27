import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
from app.student_db import StudentDB

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    # Используем in-memory SQLite для тестов
    return StudentDB("sqlite:///:memory:")

