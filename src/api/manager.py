"""Database Managers."""
# Standard Python Libraries
from datetime import datetime
import logging
import re

# Third-Party Libraries
from bson.objectid import ObjectId
from flask import abort, g, jsonify, make_response
import pymongo

# cisagov Libraries
from api.config.environment import DB
from api.schemas.config_schema import ConfigSchema
from api.schemas.customer_schema import CustomerSchema
from api.schemas.cycle_schema import CycleSchema
from api.schemas.failed_email_schema import FailedEmailSchema
from api.schemas.landing_domain_schema import LandingDomainSchema
from api.schemas.landing_page_schema import LandingPageSchema
from api.schemas.logging_schema import LoggingSchema
from api.schemas.nonhuman_schema import NonHumanSchema
from api.schemas.recommendation_schema import RecommendationsSchema
from api.schemas.sending_profile_schema import SendingProfileSchema
from api.schemas.subscription_schema import SubscriptionSchema
from api.schemas.target_schema import TargetSchema
from api.schemas.template_schema import TemplateSchema


class Manager:
    """Manager."""

    def __init__(
        self, collection, schema, unique_indexes=[], other_indexes=[], ttl_indexes=[]
    ):
        """Initialize Manager."""
        self.collection = collection
        self.schema = schema
        self.unique_indexes = unique_indexes
        self.other_indexes = other_indexes
        self.ttl_indexes = ttl_indexes
        self.db = getattr(DB, collection)

    def get_query(self, data):
        """Get query parameters from schema."""
        schema = self.schema()
        return schema.load(dict(data), partial=True)

    def document_query(self, document_id):
        """Get query for a document by id."""
        if type(document_id) is str:
            return {"_id": ObjectId(document_id)}
        elif type(document_id) is ObjectId:
            return {"_id": document_id}

    def convert_fields(self, fields):
        """Convert list of fields into mongo syntax."""
        if not fields:
            return None
        result = {}
        for field in fields:
            result[field] = 1
        return result

    def format_params(self, params):
        """Format params."""
        if not params:
            return {}
        if params.get("_id", {}).get("$in"):
            new_ids = []
            for i in params["_id"]["$in"]:
                new_ids.append(ObjectId(i))
            params["_id"]["$in"] = new_ids
        return params

    def format_sort(self, sortby: dict):
        """Format sortby for pymongo."""
        sorts = []
        for k, v in sortby.items():
            if v == "DESC":
                sorts.append((k, pymongo.DESCENDING))
            if v == "ASC":
                sorts.append((k, pymongo.ASCENDING))
        return sorts

    def read_data(self, data, many=False):
        """Read data from database."""
        if data:
            schema = self.schema(many=many)
            return schema.load(schema.dump(data), partial=True)
        return data

    def load_data(self, data, many=False, partial=False):
        """Load data into database."""
        schema = self.schema(many=many)
        return schema.load(data, partial=partial)

    def create_indexes(self, ttl_in_seconds=345600):
        """Create indexes for collection."""
        for index in self.other_indexes:
            self.db.create_index(index, unique=False)
        for index in self.ttl_indexes:
            if (
                self.db.index_information()
                and self.db.index_information()[index + "_1"]["expireAfterSeconds"]
                != ttl_in_seconds
            ):
                try:
                    DB.command(
                        "collMod",
                        "logging",
                        index={
                            "name": "created_1",
                            "expireAfterSeconds": ttl_in_seconds,
                        },
                    )
                except Exception as e:
                    logging.exception(e)
            else:
                try:
                    self.db.create_index(index, expireAfterSeconds=ttl_in_seconds)
                except Exception as e:
                    logging.exception(e)

    def add_created(self, data):
        """Add created attribute to data on save."""
        if type(data) is dict:
            data["created"] = datetime.utcnow().isoformat()
            data["created_by"] = g.get("username", "bot")
        elif type(data) is list:
            for item in data:
                item["created"] = datetime.utcnow().isoformat()
                item["created_by"] = g.get("username", "bot")
        return data

    def add_updated(self, data):
        """Update updated data on update."""
        if type(data) is dict:
            data["updated"] = datetime.utcnow().isoformat()
            data["updated_by"] = g.get("username", "bot")
        elif type(data) is list:
            for item in data:
                item["updated"] = datetime.utcnow().isoformat()
                item["updated_by"] = g.get("username", "bot")
        return data

    def clean_data(self, data):
        """Clean data for saves to the database."""
        invalid_fields = ["_id", "created", "updated"]
        if type(data) is dict:
            for field in invalid_fields:
                if field in data:
                    data.pop(field)
        elif type(data) is list:
            for item in data:
                for field in invalid_fields:
                    if field in item:
                        item.pop(field)
        return data

    def get(self, document_id=None, filter_data=None, fields=None):
        """Get item from collection by id or filter."""
        if document_id:
            return self.read_data(
                self.db.find_one(
                    self.document_query(document_id),
                    self.convert_fields(fields),
                )
            )
        else:
            return self.read_data(
                self.db.find_one(
                    filter_data,
                    self.convert_fields(fields),
                )
            )

    def all(self, params=None, fields=None, sortby=None, limit=None):
        """Get all items in a collection."""
        query = self.db.find(self.format_params(params), self.convert_fields(fields))
        if sortby:
            query.sort(self.format_sort(sortby))
        if limit:
            query.limit(limit)
        return self.read_data(query, many=True)

    def delete(self, document_id=None, params=None):
        """Delete item by object id."""
        if document_id:
            self.db.delete_one(self.document_query(document_id))
            return
        if params or params == {}:
            self.db.delete_many(params)
            return
        raise Exception(
            "Either a document id or params must be supplied when deleting."
        )

    def update(self, document_id, data, update=True):
        """Update item by id."""
        exists = []
        for unique_field in self.unique_indexes:
            if (
                self.exists(
                    {
                        unique_field: {
                            "$regex": f"^{re.escape(data[unique_field].strip())}$",
                            "$options": "i",
                        }
                    }
                )
                and self.get(document_id=document_id)[unique_field]
                != data[unique_field]
            ):
                exists.append(
                    f"A {self.collection} with {unique_field} '{data[unique_field]}' already exists."
                )

        if exists:
            abort(
                make_response(
                    jsonify({"error": ". ".join(exists)}),
                    400,
                )
            )

        data = self.clean_data(data)
        if update:
            data = self.add_updated(data)
        self.db.update_one(
            self.document_query(document_id),
            {"$set": self.load_data(data, partial=True)},
        )

    def update_many(self, params, data):
        """Update many items with params."""
        data = self.clean_data(data)
        data = self.add_updated(data)
        self.db.update_many(
            params,
            {"$set": self.load_data(data, partial=True)},
        )

    def save(self, data, ttl_in_seconds=345600):
        """Save new item to collection."""
        exists = []
        for unique_field in self.unique_indexes:
            if self.exists(
                {
                    unique_field: {
                        "$regex": f"^{re.escape(data[unique_field].strip())}$",
                        "$options": "i",
                    }
                }
            ):
                exists.append(
                    f"A {self.collection} with {unique_field} '{data[unique_field]}' already exists."
                )

        if exists:
            abort(
                make_response(
                    jsonify({"error": ". ".join(exists)}),
                    400,
                )
            )

        self.create_indexes(ttl_in_seconds)
        data = self.clean_data(data)
        data = self.add_created(data)
        data = self.add_updated(data)
        result = self.db.insert_one(self.load_data(data))
        return {"_id": str(result.inserted_id)}

    def save_many(self, data):
        """Save list to collection."""
        self.create_indexes()
        data = self.clean_data(data)
        data = self.add_created(data)
        result = self.db.insert_many(self.load_data(data, many=True))
        return result.inserted_ids

    def add_to_list(self, document_id, field, data):
        """Add item to list in document."""
        return self.db.update_one(
            self.document_query(document_id), {"$push": {field: data}}
        )

    def delete_from_list(self, document_id, field, data):
        """Delete item from list in document."""
        return self.db.update_one(
            self.document_query(document_id), {"$pull": {field: data}}
        )

    def update_in_list(self, document_id, field, data, params):
        """Update item in list from document."""
        query = self.document_query(document_id)
        query.update(params)
        self.db.update_one(query, {"$set": {field: data}})

    def upsert(self, query, data):
        """Upsert documents into the database."""
        data = self.clean_data(data)
        data = self.add_created(data)
        data = self.add_updated(data)
        self.db.update_one(
            query,
            {"$set": self.load_data(data)},
            upsert=True,
        )

    def random(self, count=1):
        """Select a random record from collection."""
        return list(self.db.aggregate([{"$sample": {"size": count}}]))

    def count(self, query={}):
        """Count the number of documents matching the query in a collection."""
        return self.db.count_documents(query)

    def distinct_count(self, field, query={}):
        """Count the number of distinct values for a field matching the query in a collection."""
        return len(self.db.distinct(field, query))

    def aggregate(self, pipeline=[]):
        """Aggregate the quantity according to the aggregation pipeline."""
        return list(self.db.aggregate(pipeline))

    def exists(self, parameters=None):
        """Check if record exists."""
        fields = self.convert_fields(["_id"])
        result = list(self.db.find(parameters, fields))
        return bool(result)

    def find_one_and_update(self, params, data, fields=None):
        """Find an object and update it."""
        data = self.clean_data(data)
        data = self.add_updated(data)
        return self.db.find_one_and_update(
            params,
            {"$set": self.load_data(data, partial=True)},
            return_document=pymongo.ReturnDocument.AFTER,
            projection=self.convert_fields(fields),
        )


class ConfigManager(Manager):
    """ConfigManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="config",
            schema=ConfigSchema,
        )


class CustomerManager(Manager):
    """Customer Manager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="customer",
            schema=CustomerSchema,
            unique_indexes=["name"],
        )


class CycleManager(Manager):
    """CycleManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="cycle",
            schema=CycleSchema,
        )


class LandingDomainManager(Manager):
    """LandingDomainManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="landing_domain",
            schema=LandingDomainSchema,
            unique_indexes=["domain"],
        )


class LandingPageManager(Manager):
    """LandingPageManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="landing_page",
            schema=LandingPageSchema,
            unique_indexes=["name"],
        )

    def clear_and_set_default(self, document_id):
        """Set Default Landing Page."""
        sub_query = {}
        newvalues = {"$set": {"is_default_template": False}}
        self.db.update_many(sub_query, newvalues)
        sub_query = self.document_query(document_id)
        newvalues = {"$set": {"is_default_template": True}}
        self.db.update_one(sub_query, newvalues)


class NonHumanManager(Manager):
    """NonHumanManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="nonhuman",
            schema=NonHumanSchema,
        )


class RecommendationManager(Manager):
    """RecommendationManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="recommendation",
            schema=RecommendationsSchema,
            unique_indexes=["title"],
        )


class SendingProfileManager(Manager):
    """SendingProfileManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="sending_profile",
            schema=SendingProfileSchema,
            unique_indexes=["name"],
        )


class SubscriptionManager(Manager):
    """SubscriptionManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="subscription",
            schema=SubscriptionSchema,
        )


class TargetManager(Manager):
    """Target Manager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="target",
            schema=TargetSchema,
            other_indexes=["email"],
        )


class TemplateManager(Manager):
    """Template Manager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="template", schema=TemplateSchema, unique_indexes=["name"]
        )


class LoggingManager(Manager):
    """LoggingManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="logging",
            schema=LoggingSchema,
            ttl_indexes=["created"],
        )


class FailedEmailManager(Manager):
    """FailedEmailManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="failed_emails",
            schema=FailedEmailSchema,
            unique_indexes=["recipient"],
        )
