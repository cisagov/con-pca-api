from api.utils.db_utils import get_mongo_uri, get_single
from api.models.landing_page_models import LandingPageModel, validate_landing_page
import pymongo


def clear_and_set_default(landing_page_uuid):
    db_url = get_mongo_uri()
    client = pymongo.MongoClient(db_url)
    db = client["pca_data_dev"]
    collection = db["landing_page"]
    sub_query = {}
    newvalues = {"$set": {"is_default_template": False}}
    collection.update_many(sub_query, newvalues)
    sub_query = {"landing_page_uuid": landing_page_uuid}
    newvalues = {"$set": {"is_default_template": True}}
    collection.update_one(sub_query, newvalues)


def get_landing_page(landing_page_uuid):
    return get_single(
        landing_page_uuid, "landing_page", LandingPageModel, validate_landing_page
    )
