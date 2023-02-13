"""Settings for the database."""
# Standard Python Libraries
import os

# Third-Party Libraries
from pymongo import MongoClient


def get_db():
    """Get database client."""
    return MongoClient(os.environ["MONGO_CLUSTER_URI"], tz_aware=True).pca
