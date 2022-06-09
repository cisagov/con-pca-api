"""Configuration test."""
# Third-Party Libraries
import pytest

# cisagov Libraries
from api.main import app


@pytest.fixture
def client():
    """Client."""
    app.config.update({"TEST": True})

    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture(autouse=True)
def no_db(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("pymongo.MongoClient")
