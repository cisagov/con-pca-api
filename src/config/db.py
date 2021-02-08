"""Database configuration."""
# Standard Python Libraries
import os

# Third-Party Libraries
from pymongo import MongoClient


def get_connection_string(db_user, db_pw, db_host, db_port):
    """Get connection string for connecting to MongoDB."""
    if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
        fmt = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&retryWrites=false"
    else:
        fmt = "mongodb://{}:{}@{}:{}/"
    return fmt.format(db_user, db_pw, db_host, db_port)


def get_db():
    """Get the Pymongo Database."""
    conn_str = get_connection_string(
        db_user=os.environ.get("DB_USER"),
        db_pw=os.environ.get("DB_PW"),
        db_host=os.environ.get("DB_HOST"),
        db_port=os.environ.get("DB_PORT"),
    )
    client = MongoClient(conn_str)
    return client.pca_data_dev
