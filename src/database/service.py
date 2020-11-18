"""
This is the main service for controller/api.

This is the toplevel service that should be imported for connecting with mongodb.
This creates a Service class that is given:
    mongo_url, collection_name, model, model_validation
on init.
this will then handle all transacations for the given collection and model.
"""
from .repository.generics import GenericRepository, GenericRepositoryInterface


class Service:
    """This loads configuration from env."""

    def __init__(self, mongo_url, collection_name, model):
        """Init for service creation."""
        self.model = model
        self.service = GenericRepositoryInterface(
            GenericRepository(mongo_url, collection_name, model_cls=model)
        )

    async def count(self, parameters=None):
        """
        Count.

        Takes in parameters that are field names and values and
        filters all documents and returns a count of
        documents matching results.
        """
        return await self.service.count(parameters)

    async def filter_list(self, parameters=None, fields=None):
        """
        Filter_list.

        Takes in parameters that are field names and values and
        filters all documents and returns list of results.
        """
        return await self.service.filter(parameters, fields)

    async def get(self, uuid, fields=None):
        """
        Get.

        Given a uuid of object, will return document with unique uuid.
        """
        return await self.service.get(uuid, fields)

    async def get_single(self, parameters, fields=None):
        """Find single item from database."""
        return await self.service.get_single(parameters, fields)

    async def create(self, to_create):
        """
        Create.

        Given a json object, it wil validate the fields and create a db entrie.
        This will return the objectID of the created object
        """
        return await self.service.create(to_create)

    async def update(self, uuid, to_update):
        """
        Update.

        Given a json object, it wil validate the fields and update a db entrie.
        This will return the objectID of the updated object
        """
        return await self.service.update(uuid, to_update)

    async def update_nested_single(self, uuid, to_update, params=None):
        """
        Update.

        Given a json object, it wil validate the fields and update a db entrie.
        This will return the objectID of the updated object
        """
        resp = await self.service.update_nested(uuid, to_update, params)
        return resp.raw_result

    async def push_nested_item(self, uuid, item, params=None):
        """
        Push.

        Given a json object, it will add that object to an array in the document.
        """
        resp = await self.service.push_nested_item(uuid, item, params)
        return resp.raw_result

    async def delete(self, uuid):
        """
        Delete.

        Given a uuid of object deleteted
        Returns bool of acknowledged of object being deleted.
        """
        return await self.service.delete(uuid)
