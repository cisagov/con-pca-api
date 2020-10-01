from src.api.utils import db_utils as db
from src.database.service import Service

from unittest import mock
import os


@mock.patch("database.service.Service")
def test_db_service(mock_db):
    result = db.__db_service("collection", "model", "validate")
    assert result.model == "model"


def test_get_mongo_uri():
    os.environ["MONGO_TYPE"] = "MONGO"
    result = db.get_mongo_uri()
    assert "rds-combined-ca-bundle.pem" not in result
    os.environ["MONGO_TYPE"] = "DOCUMENTDB"
    result = db.get_mongo_uri()
    assert "rds-combined-ca-bundle.pem" in result
