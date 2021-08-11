"""Database Managers."""
# Standard Python Libraries
from datetime import datetime
from uuid import uuid4

# Third-Party Libraries
from flask import g
import pymongo

# cisagov Libraries
from api.config import DB
from api.schemas.customer_schema import CustomerSchema
from api.schemas.landing_page_schema import LandingPageSchema
from api.schemas.sending_profile_schema import SendingProfileSchema
from api.schemas.template_schema import TemplateSchema


class Manager:
    """Manager."""

    def __init__(self, collection, schema, unique_indexes=[], other_indexes=[]):
        """Initialize Manager."""
        self.collection = collection
        self.schema = schema
        self.unique_indexes = unique_indexes
        self.other_indexes = other_indexes
        self.uuid_field = f"{collection}_uuid"
        self.db = getattr(DB, collection)

    def get_query(self, data):
        """Get query parameters from schema."""
        schema = self.schema()
        return schema.load(dict(data), partial=True)

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
            return schema.load(schema.dump(data))
        return data

    def load_data(self, data, many=False, partial=False):
        """Load data into database."""
        schema = self.schema(many=many)
        return schema.load(data, partial=partial)

    def create_indexes(self):
        """Create indexes for collection."""
        for index in self.unique_indexes:
            self.db.create_index(index, unique=True)
        for index in self.other_indexes:
            self.db.create_index(index, unique=False)

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
        invalid_fields = ["_id", "created", "updated", self.uuid_field]
        if type(data) is dict:
            for field in invalid_fields:
                if data.get(field):
                    data.pop(field)
        elif type(data) is list:
            for item in data:
                for field in invalid_fields:
                    if item.get(field):
                        item.pop(field)
        return data

    def get(self, uuid=None, filter_data=None, fields=None):
        """Get item from collection by id or filter."""
        if uuid:
            return self.read_data(
                self.db.find_one(
                    {self.uuid_field: str(uuid)},
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

    def delete(self, uuid=None, params=None):
        """Delete item by object id."""
        if uuid:
            return self.db.delete_one({self.uuid_field: str(uuid)}).raw_result
        if params:
            return self.db.delete_many(params).raw_result
        raise Exception(
            "Either a document id or params must be supplied when deleting."
        )

    def update(self, uuid, data):
        """Update item by id."""
        data = self.clean_data(data)
        data = self.add_updated(data)
        return self.db.update_one(
            {self.uuid_field: str(uuid)},
            {"$set": self.load_data(data, partial=True)},
        ).raw_result

    def save(self, data):
        """Save new item to collection."""
        self.create_indexes()
        data = self.clean_data(data)
        data = self.add_created(data)
        data[self.uuid_field] = str(uuid4())
        self.db.insert_one(self.load_data(data))
        return {self.uuid_field: data[self.uuid_field]}

    def add_to_list(self, uuid, field, data):
        """Add item to list in document."""
        return self.db.update_one(
            {self.uuid_field: str(uuid)}, {"$push": {field: data}}
        ).raw_result

    def delete_from_list(self, uuid, field, data):
        """Delete item from list in document."""
        return self.db.update_one(
            {self.uuid_field: str(uuid)}, {"$pull": {field: data}}
        ).raw_result

    def update_in_list(self, uuid, field, data, params):
        """Update item in list from document."""
        return self.db.update_one(
            {self.uuid_field: str(uuid), **params}, {"$set": {field: data}}
        ).raw_result

    def random(self, count=1):
        """Select a random record from collection."""
        return list(self.db.aggregate([{"$sample": {"size": count}}]))

    def exists(self, parameters=None):
        """Check if record exists."""
        fields = self.convert_fields([self.uuid_field])
        result = list(self.db.find(parameters, fields))
        return bool(result)


class CustomerManager(Manager):
    """Customer Manager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="customer",
            schema=CustomerSchema,
        )


class SendingProfileManager(Manager):
    """SendingProfileManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="sending_profile",
            schema=SendingProfileSchema,
        )


class TemplateManager(Manager):
    """Template Manager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="template",
            schema=TemplateSchema,
        )


class LandingPageManager(Manager):
    """LandingPageManager."""

    def __init__(self):
        """Super."""
        return super().__init__(
            collection="landing_page",
            schema=LandingPageSchema,
        )

    def clear_and_set_default(self, uuid):
        """Set Default Landing Page."""
        sub_query = {}
        newvalues = {"$set": {"is_default_template": False}}
        self.db.update_many(sub_query, newvalues)
        sub_query = {"landing_page_uuid": str(uuid)}
        newvalues = {"$set": {"is_default_template": True}}
        self.db.update_one(sub_query, newvalues)
