"""DB Utils file for api."""
# Standard Python Libraries
import asyncio
import datetime
import os
import uuid

# cisagov Libraries
from config import settings
from database.service import Service


def __db_service(collection_name, model):
    mongo_uri = get_mongo_uri()

    service = Service(
        mongo_uri,
        collection_name=collection_name,
        model=model,
    )

    return service


def get_mongo_uri():
    """Get Mongo Connection String."""
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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    service = __db_service(collection, model)
    return service, loop


def get_list(parameters, collection, model, fields=None):
    """Get list of documents from database."""
    service, loop = __get_service_loop(collection, model)
    return loop.run_until_complete(
        service.filter_list(parameters=parameters, fields=fields)
    )


def save_single(post_data, collection, model):
    """Save Single."""
    service, loop = __get_service_loop(collection, model)
    create_timestamp = datetime.datetime.utcnow()
    current_user = "dev user"
    post_data["{}_uuid".format(collection)] = str(uuid.uuid4())
    post_data["created_by"] = post_data["last_updated_by"] = current_user
    post_data["cb_timestamp"] = post_data["lub_timestamp"] = create_timestamp

    return loop.run_until_complete(service.create(to_create=post_data))


def get(uuid, collection, model, fields=None):
    """Get."""
    service, loop = __get_service_loop(collection, model)
    return loop.run_until_complete(service.get(uuid=uuid, fields=fields))


def get_single(parameters, collection, model, fields=None):
    """Get Single."""
    service, loop = __get_service_loop(collection, model)
    return loop.run_until_complete(
        service.get_single(parameters=parameters, fields=fields)
    )


def update_single(uuid, put_data, collection, model):
    """Update Single."""
    service, loop = __get_service_loop(collection, model)
    put_data["last_updated_by"] = "dev user"
    put_data["lub_timestamp"] = datetime.datetime.utcnow()

    return loop.run_until_complete(service.update(uuid, put_data))


def push_nested_item(uuid, field, put_data, collection, model, params=None):
    """Push Nested Item."""
    service, loop = __get_service_loop(collection, model)

    list_update_object = {field: put_data}

    return loop.run_until_complete(
        service.push_nested_item(uuid, list_update_object, params)
    )


def update_nested_single(uuid, field, put_data, collection, model, params=None):
    """
    Update Nested Single.

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
    """Delete Single."""
    service, loop = __get_service_loop(collection, model)

    return loop.run_until_complete(service.delete(uuid=uuid))


def exists(parameters, collection, model):
    """Check exists."""
    service, loop = __get_service_loop(collection, model)
    document_list = loop.run_until_complete(
        service.filter_list(parameters=parameters, fields={"_id": 1})
    )
    if document_list:
        return True
    return False
