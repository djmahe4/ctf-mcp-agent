"""
Pytest configuration and fixtures
"""
import pytest
import os
from pathlib import Path

# Set test environment variables
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/test_ctf"
os.environ["SECRET_KEY"] = "test_secret_key_for_jwt_token_generation_12345"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

# Make GOOGLE_API_KEY optional for tests
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = ""  # Empty means AI will be unavailable


@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def mock_user():
    """Mock user for testing"""
    return {
        "user_id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com",
        "role": "user"
    }


@pytest.fixture
def mock_admin():
    """Mock admin for testing"""
    return {
        "user_id": "admin_123",
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin"
    }


@pytest.fixture
def mock_challenge():
    """Mock challenge for testing"""
    return {
        "challenge_id": "sqli_basic_001",
        "title": "SQL Injection Basics",
        "description": "Learn SQL injection",
        "vulnerability_type": "sqli",
        "difficulty": "easy",
        "points": 100
    }
