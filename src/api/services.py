import logging
from rest_framework import serializers
import pymongo

from api.utils import db_utils as db

from api.models import campaign_models
from api.serializers import campaign_serializers

from api.models import customer_models
from api.serializers import customer_serializers

from api.models import dhs_models
from api.serializers import dhs_serializers

from api.models import landing_page_models
from api.serializers import landing_page_serializers

from api.models import recommendations_models
from api.serializers import recommendations_serializers

from api.models import subscription_models
from api.serializers import subscriptions_serializers

from api.models import tag_models
from api.serializers import tag_serializers

from api.models import target_history_models
from api.serializers import target_history_serializers

from api.models import template_models
from api.serializers import template_serializers


class DBService:
    def __init__(
        self,
        collection,
        model,
        save_serializer,
        update_serializer,
    ):
        self.collection = collection
        self.model = model
        self.save_serializer = save_serializer
        self.update_serializer = update_serializer

    def validate_serializer(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logging.exception(e)
            raise e

    def convert_fields(self, fields):
        if not fields:
            return None
        result = {}
        for field in fields:
            result[field] = 1
        return result

    def delete(self, uuid):
        return db.delete_single(
            uuid=str(uuid),
            collection=self.collection,
            model=self.model,
        )

    def get(self, uuid, fields=None):
        fields = self.convert_fields(fields)
        return db.get(
            uuid=str(uuid),
            collection=self.collection,
            model=self.model,
            fields=fields,
        )

    def get_single(self, parameters, fields=None):
        fields = self.convert_fields(fields)
        return db.get_single(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
            fields=fields,
        )

    def get_list(self, parameters=None, fields=None):
        fields = self.convert_fields(fields)
        return db.get_list(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
            fields=fields,
        )

    def save(self, data):
        serializer = self.save_serializer(data=data)
        self.validate_serializer(serializer)
        result = db.save_single(
            post_data=serializer.validated_data,
            collection=self.collection,
            model=self.model,
        )
        if type(result) is dict:
            if result.get("errors"):
                logging.error(result.get("errors"))
                raise Exception(result.get("errors"))

        return result

    def update(self, uuid, data):
        serializer = self.update_serializer(data=data)
        self.validate_serializer(serializer)
        result = db.update_single(
            uuid=str(uuid),
            put_data=serializer.validated_data,
            collection=self.collection,
            model=self.model,
        )
        print(result)
        if type(result) is dict:
            if result.get("errors"):
                logging.error(result.get("errors"))
                raise Exception(result.get("errors"))
        return result

    def update_nested(self, uuid, field, data, params=None):
        return db.update_nested_single(
            uuid=str(uuid),
            field=field,
            put_data=data,
            collection=self.collection,
            model=self.model,
            params=params,
        )

    def push_nested(self, uuid, field, data, params=None):
        return db.push_nested_item(
            uuid=str(uuid),
            field=field,
            put_data=data,
            collection=self.collection,
            model=self.model,
            params=params,
        )

    def exists(self, parameters=None):
        return db.exists(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
        )


class CampaignService(DBService):
    def __init__(self):
        return super().__init__(
            collection="campaign",
            model=campaign_models.GoPhishCampaignsModel,
            save_serializer=campaign_serializers.GoPhishCampaignsPostSerializer,
            update_serializer=campaign_serializers.GoPhishCampaignsPatchSerializer,
        )


class LandingPageService(DBService):
    def __init__(self):
        return super().__init__(
            collection="landing_page",
            model=landing_page_models.LandingPageModel,
            save_serializer=landing_page_serializers.LandingPagePostSerializer,
            update_serializer=landing_page_serializers.LandingPagePatchSerializer,
        )

    def clear_and_set_default(self, uuid):
        db_url = db.get_mongo_uri()
        client = pymongo.MongoClient(db_url)
        collection = client["pca_data_dev"]["landing_page"]
        sub_query = {}
        newvalues = {"$set": {"is_default_template": False}}
        collection.update_many(sub_query, newvalues)
        sub_query = {"landing_page_uuid": str(uuid)}
        newvalues = {"$set": {"is_default_template": True}}
        collection.update_one(sub_query, newvalues)


class SubscriptionService(DBService):
    def __init__(self):
        self.campaign_service = CampaignService()
        return super().__init__(
            collection="subscription",
            model=subscription_models.SubscriptionModel,
            save_serializer=subscriptions_serializers.SubscriptionPostSerializer,
            update_serializer=subscriptions_serializers.SubscriptionPatchSerializer,
        )

    def get(self, uuid, fields=None):
        fields = self.convert_fields(fields)
        subscription = db.get(
            uuid=str(uuid), collection=self.collection, model=self.model, fields=fields
        )

        if not fields or "campaigns" in fields:
            subscription["campaigns"] = self.campaign_service.get_list(
                {"subscription_uuid": str(uuid)}
            )
        return subscription


class RecommendationService(DBService):
    def __init__(self):
        return super().__init__(
            collection="recommendations",
            model=recommendations_models.RecommendationsModel,
            save_serializer=recommendations_serializers.RecommendationsPostSerializer,
            update_serializer=recommendations_serializers.RecommendationsPatchSerializer,
        )


class TemplateService(DBService):
    def __init__(self):
        return super().__init__(
            collection="template",
            model=template_models.TemplateModel,
            save_serializer=template_serializers.TemplatePostSerializer,
            update_serializer=template_serializers.TemplatePatchSerializer,
        )


class TagService(DBService):
    def __init__(self):
        return super().__init__(
            collection="tag_definition",
            model=tag_models.TagModel,
            save_serializer=tag_serializers.TagPostSerializer,
            update_serializer=tag_serializers.TagPatchSerializer,
        )


class DHSContactService(DBService):
    def __init__(self):
        return super().__init__(
            collection="dhs_contact",
            model=dhs_models.DHSContactModel,
            save_serializer=dhs_serializers.DHSContactPostSerializer,
            update_serializer=dhs_serializers.DHSContactPatchSerializer,
        )


class CustomerService(DBService):
    def __init__(self):
        return super().__init__(
            collection="customer",
            model=customer_models.CustomerModel,
            save_serializer=customer_serializers.CustomerPostSerializer,
            update_serializer=customer_serializers.CustomerPatchSerializer,
        )


class TargetHistoryService(DBService):
    def __init__(self):
        return super().__init__(
            collection="target",
            model=target_history_models.TargetHistoryModel,
            save_serializer=target_history_serializers.TargetHistoryPostSerializer,
            update_serializer=target_history_serializers.TargetHistoryPatchSerializer,
        )
