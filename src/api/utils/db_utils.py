"""DB Utils file for api."""
# Standard Python Libraries
import asyncio
import datetime
import uuid

# Models
from database.service import Service
from config import settings
import os


def __db_service(collection_name, model):
    """
    Db_service.

    This is a method for handling db connection in api.
    Might refactor this into database lib.
    """
    mongo_uri = get_mongo_uri()

    service = Service(
        mongo_uri,
        collection_name=collection_name,
        model=model,
    )

    return service


def get_mongo_uri():
    if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
        mongo_uri = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&retryWrites=false".format(
            settings.DB_CONFIG["DB_USER"],
            settings.DB_CONFIG["DB_PW"],
            settings.DB_CONFIG["DB_HOST"],
            settings.DB_CONFIG["DB_PORT"],
        )
    else:
        mongo_uri = "mongodb://{}:{}@{}:{}/".format(
            settings.DB_CONFIG["DB_USER"],
            settings.DB_CONFIG["DB_PW"],
            settings.DB_CONFIG["DB_HOST"],
            settings.DB_CONFIG["DB_PORT"],
        )
    return mongo_uri


def __get_service_loop(collection, model):
    """
    Get Service Loop.

    Getting loop for asyncio and service for DB.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    service = __db_service(collection, model)
    return service, loop


def get_list(parameters, collection, model, fields=None):
    """Gets list of documents from database."""
    service, loop = __get_service_loop(collection, model)
    return loop.run_until_complete(
        service.filter_list(parameters=parameters, fields=fields)
    )


def save_single(post_data, collection, model):
    """
    Save_data method.

    This method takes in
    post_data and saves it to the db with the required feilds.
    """
    service, loop = __get_service_loop(collection, model)
    create_timestamp = datetime.datetime.utcnow()
    current_user = "dev user"
    post_data["{}_uuid".format(collection)] = str(uuid.uuid4())
    post_data["created_by"] = post_data["last_updated_by"] = current_user
    post_data["cb_timestamp"] = post_data["lub_timestamp"] = create_timestamp

    return loop.run_until_complete(service.create(to_create=post_data))


def get(uuid, collection, model, fields=None):
    """Gets single record by uuid"""
    service, loop = __get_service_loop(collection, model)
    return loop.run_until_complete(service.get(uuid=uuid, fields=fields))


def get_single(parameters, collection, model, fields=None):
    """gets single record by given params"""
    service, loop = __get_service_loop(collection, model)
    return loop.run_until_complete(
        service.get_single(parameters=parameters, fields=fields)
    )


def update_single(uuid, put_data, collection, model):
    """Updates single item by uuid in database"""
    service, loop = __get_service_loop(collection, model)
    put_data["last_updated_by"] = "dev user"
    put_data["lub_timestamp"] = datetime.datetime.utcnow()

    return loop.run_until_complete(service.update(uuid, put_data))


def push_nested_item(uuid, field, put_data, collection, model, params=None):
    service, loop = __get_service_loop(collection, model)

    list_update_object = {field: put_data}

    return loop.run_until_complete(
        service.push_nested_item(uuid, list_update_object, params)
    )


def update_nested_single(uuid, field, put_data, collection, model, params=None):
    """
    update_nested_single method.

    This builds $addToSet object for db, updates, then returns.

    Example: uuid="123-123-123", field="timeline", put_data={...data...}, ...
    if params!=None:
        the db will query using extra params
        {uuid="123-123-123", "campaigns.campaign_id": 85}
        then for a nested set:
        field="campaigns.$.timeline"
        and put_data = [value1,value2,...]

    Example call:
        update_nested_single(
            uuid="123-123-123",
            field="campaigns.$.timeline",
            put_data=[<object>], "subscription", SubscriptionModel,validate_subscription,
            params={"campaigns.campaign_id": 85})
    """
    service, loop = __get_service_loop(collection, model)

    list_update_object = {field: put_data}

    return loop.run_until_complete(
        service.update_nested_single(uuid, list_update_object, params)
    )


def delete_single(uuid, collection, model):
    """ Deletes object by uuid from database """
    service, loop = __get_service_loop(collection, model)

    return loop.run_until_complete(service.delete(uuid=uuid))


def exists(parameters, collection, model):
    """Check if item exists for given parameter."""
    service, loop = __get_service_loop(collection, model)
    document_list = loop.run_until_complete(
        service.filter_list(parameters=parameters, fields={"_id": 1})
    )
    if document_list:
        return True
    return False
