from api.utils import db_utils as db
from api.models.landing_page_models import LandingPageModel, validate_landing_page

import pymongo


def clear_and_set_default(landing_page_uuid):
    db_url = db.get_mongo_uri()
    client = pymongo.MongoClient(db_url)
    collection = client["pca_data_dev"]["landing_page"]
    sub_query = {}
    newvalues = {"$set": {"is_default_template": False}}
    collection.update_many(sub_query, newvalues)
    sub_query = {"landing_page_uuid": landing_page_uuid}
    newvalues = {"$set": {"is_default_template": True}}
    collection.update_one(sub_query, newvalues)


def get_landing_page(landing_page_uuid):
    return db.get_single(
        landing_page_uuid, "landing_page", LandingPageModel, validate_landing_page
    )
